from __future__ import annotations

import base64
import gzip
import hashlib
import json
import os
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet

try:
    from psycopg import connect
    from psycopg.rows import dict_row
except ImportError:  # pragma: no cover - optional dependency fallback
    connect = None
    dict_row = None


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
BACKUP_DIR = DATA_DIR / "backups"
RESULTS_FILE = DATA_DIR / "screening_results.json"
LEGACY_SQLITE_FILE = DATA_DIR / "screening_results.db"
ENCRYPTION_KEY_FILE = DATA_DIR / "storage.key"
MAX_LIST_LIMIT = 250
MAX_AUDIT_LIMIT = 500
STORAGE_SCHEMA_VERSION = 3
DEFAULT_DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5432/mental_health_screening"

_STORAGE_LOCK = threading.Lock()
_STORAGE_READY = False


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _database_url() -> str:
    return os.getenv("DATABASE_URL") or os.getenv("MHS_DATABASE_URL") or DEFAULT_DATABASE_URL


def _masked_database_url() -> str:
    value = _database_url()
    if "@" not in value or "://" not in value:
        return value
    prefix, suffix = value.split("://", 1)
    credentials, host = suffix.split("@", 1)
    if ":" in credentials:
        username, _password = credentials.split(":", 1)
        return f"{prefix}://{username}:***@{host}"
    return f"{prefix}://***@{host}"


def _connect():
    if connect is None or dict_row is None:
        raise RuntimeError("psycopg is not installed")
    return connect(
        _database_url(),
        row_factory=dict_row,
        connect_timeout=10,
    )


def _postgres_enabled() -> bool:
    return connect is not None and dict_row is not None


def _load_or_create_encryption_key() -> bytes:
    env_key = os.getenv("MHS_STORAGE_ENCRYPTION_KEY")
    if env_key:
        return env_key.encode("utf-8")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if ENCRYPTION_KEY_FILE.exists():
        return ENCRYPTION_KEY_FILE.read_bytes().strip()

    key = Fernet.generate_key()
    ENCRYPTION_KEY_FILE.write_bytes(key)
    return key


def _encryption_key_source() -> str:
    return "environment" if os.getenv("MHS_STORAGE_ENCRYPTION_KEY") else "local_key_file"


def _fernet() -> Fernet:
    return Fernet(_load_or_create_encryption_key())


def _encrypt_payload(payload: Any) -> bytes:
    serialized = json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    return _fernet().encrypt(serialized)


def _decrypt_payload(ciphertext: bytes | memoryview | bytearray | None) -> Any:
    if ciphertext is None:
        return None
    token = bytes(ciphertext)
    plaintext = _fernet().decrypt(token)
    return json.loads(plaintext.decode("utf-8"))


def _payload_checksum(profile: dict, questionnaire: dict, multimodal: dict) -> str:
    digest = hashlib.sha256()
    for payload in (profile, questionnaire, multimodal):
        digest.update(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8"))
    return digest.hexdigest()


def _normalize_identity_text(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _normalize_phone(value: Any) -> str:
    return "".join(character for character in str(value or "") if character.isdigit())


def _patient_key(profile: dict | None) -> str:
    safe_profile = profile if isinstance(profile, dict) else {}
    explicit_id = _normalize_identity_text(safe_profile.get("patient_id"))
    if explicit_id:
        return f"patient_id:{explicit_id}"

    phone = _normalize_phone(safe_profile.get("phone"))
    if len(phone) >= 6:
        return f"phone:{phone}"

    full_name = _normalize_identity_text(safe_profile.get("full_name"))
    village = _normalize_identity_text(safe_profile.get("village"))
    age = str(safe_profile.get("age", "")).strip()
    gender = _normalize_identity_text(safe_profile.get("gender"))
    identity_basis = "|".join(part for part in (full_name, village, age, gender) if part)
    if not identity_basis:
        return "unknown"
    digest = hashlib.sha256(identity_basis.encode("utf-8")).hexdigest()[:20]
    return f"profile:{digest}"


def _record_origin(profile: dict | None, fallback: str = "backend") -> str:
    safe_profile = profile if isinstance(profile, dict) else {}
    origin = str(safe_profile.get("record_origin") or "").strip().lower()
    if origin:
        return origin
    return fallback


def _record_scores(record: dict) -> dict[str, float]:
    overall = ((record.get("multimodal") or {}).get("overall") or {}).get("scores") or {}
    return {
        domain: max(0.0, min(float(overall.get(domain, 0.0) or 0.0), 1.0))
        for domain in (
            "depression",
            "anxiety",
            "stress",
            "sleep_disorder",
            "burnout",
            "loneliness",
            "substance_abuse",
        )
    }


def _strongest_domain(scores: dict[str, float]) -> str:
    if not scores:
        return "unknown"
    return max(scores.items(), key=lambda item: item[1])[0]


def _overall_score(record: dict) -> float:
    scores = _record_scores(record)
    if not scores:
        return 0.0
    return sum(scores.values()) / len(scores)


def _linear_slope(series: list[tuple[float, float]]) -> float:
    if len(series) < 2:
        return 0.0
    xs = [point[0] for point in series]
    ys = [point[1] for point in series]
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    denominator = sum((value - mean_x) ** 2 for value in xs)
    if denominator <= 1e-9:
        return 0.0
    numerator = sum((x_value - mean_x) * (y_value - mean_y) for x_value, y_value in zip(xs, ys))
    return numerator / denominator


def _trajectory_direction(slope: float) -> str:
    if slope >= 0.035:
        return "worsening"
    if slope <= -0.035:
        return "improving"
    return "stable"


def _trajectory_status_label(status: str) -> str:
    return {
        "insufficient_history": "Need more screenings",
        "escalating": "Escalating risk",
        "worsening": "Worsening trend",
        "improving": "Improving trend",
        "volatile": "Volatile trajectory",
        "stable": "Stable trajectory",
    }.get(status, "Trajectory available")


def _build_trajectory_summary(history: list[dict], patient_key: str) -> dict:
    ordered = sorted(history, key=lambda item: item.get("created_at", ""))
    if not ordered:
        return {
            "patient_key": patient_key,
            "history_count": 0,
            "status": "insufficient_history",
            "status_label": _trajectory_status_label("insufficient_history"),
            "summary": "No history available for this person yet.",
            "points": [],
            "domains": {},
        }

    points = []
    baseline_reference = None
    for index, record in enumerate(ordered):
        scores = _record_scores(record)
        overall_score = _overall_score(record)
        overall_levels = (record.get("multimodal") or {}).get("overall") or {}
        created_at = record.get("created_at")
        timestamp = datetime.fromisoformat(str(created_at).replace("Z", "+00:00")) if created_at else _utc_now()
        if baseline_reference is None:
            baseline_reference = timestamp
        elapsed_days = max((timestamp - baseline_reference).total_seconds() / 86400.0, 0.0)
        points.append(
            {
                "assessment_id": record.get("assessment_id"),
                "created_at": created_at,
                "sequence": index + 1,
                "overall_score": round(overall_score, 4),
                "overall_risk": overall_levels.get(_strongest_domain(scores), "low"),
                "confidence": round(float(overall_levels.get("confidence", 0.0) or 0.0), 4),
                "scores": {domain: round(value, 4) for domain, value in scores.items()},
                "strongest_domain": _strongest_domain(scores),
                "elapsed_days": round(elapsed_days, 3),
            }
        )

    latest = points[-1]
    baseline = points[0]
    previous = points[-2] if len(points) > 1 else points[0]
    overall_series = [(point["elapsed_days"] or float(index), point["overall_score"]) for index, point in enumerate(points)]
    overall_slope = _linear_slope(overall_series)
    recent_delta = latest["overall_score"] - previous["overall_score"]
    baseline_delta = latest["overall_score"] - baseline["overall_score"]
    step_changes = [
        abs(points[index]["overall_score"] - points[index - 1]["overall_score"])
        for index in range(1, len(points))
    ]
    volatility = (sum(step_changes) / len(step_changes)) if step_changes else 0.0

    domain_summaries = {}
    worsening_domains = []
    improving_domains = []
    for domain in points[0]["scores"].keys():
        domain_series = [(point["elapsed_days"] or float(index), point["scores"][domain]) for index, point in enumerate(points)]
        slope = _linear_slope(domain_series)
        direction = _trajectory_direction(slope)
        latest_score = latest["scores"][domain]
        baseline_score = baseline["scores"][domain]
        delta = latest_score - baseline_score
        domain_summaries[domain] = {
            "latest_score": round(latest_score, 4),
            "baseline_score": round(baseline_score, 4),
            "change_from_baseline": round(delta, 4),
            "slope_per_day": round(slope, 6),
            "direction": direction,
        }
        if direction == "worsening" and delta >= 0.08:
            worsening_domains.append(domain)
        if direction == "improving" and delta <= -0.08:
            improving_domains.append(domain)

    latest_strongest = latest["strongest_domain"]
    latest_risk_level = ordered[-1].get("multimodal", {}).get("overall", {}).get(latest_strongest, "low")
    if len(points) < 2:
        status = "insufficient_history"
    elif volatility >= 0.16 and abs(overall_slope) < 0.03:
        status = "volatile"
    elif overall_slope >= 0.035 or recent_delta >= 0.12:
        status = "escalating" if latest_risk_level == "high" or baseline_delta >= 0.2 else "worsening"
    elif overall_slope <= -0.035 or recent_delta <= -0.12:
        status = "improving"
    else:
        status = "stable"

    if status == "insufficient_history":
        summary = "Only one screening is available. Capture at least one follow-up to start trend modeling."
    elif status == "volatile":
        summary = "Risk is fluctuating across visits. The person may need closer follow-up because the pattern is unstable."
    elif status in {"worsening", "escalating"}:
        domains_text = ", ".join(worsening_domains[:3]) if worsening_domains else latest_strongest.replace("_", " ")
        summary = f"Risk is rising over time, especially around {domains_text}. Prioritize follow-up and compare against the last visit."
    elif status == "improving":
        domains_text = ", ".join(improving_domains[:3]) if improving_domains else latest_strongest.replace("_", " ")
        summary = f"Recent screenings show improving scores, including {domains_text}. Continue follow-up to confirm the improvement holds."
    else:
        summary = "Overall risk has been relatively stable across the recorded screenings."

    return {
        "patient_key": patient_key,
        "history_count": len(points),
        "status": status,
        "status_label": _trajectory_status_label(status),
        "summary": summary,
        "latest_assessment_id": latest["assessment_id"],
        "baseline_assessment_id": baseline["assessment_id"],
        "latest_overall_score": round(latest["overall_score"], 4),
        "baseline_overall_score": round(baseline["overall_score"], 4),
        "change_from_baseline": round(baseline_delta, 4),
        "change_from_previous": round(recent_delta, 4),
        "slope_per_day": round(overall_slope, 6),
        "volatility": round(volatility, 4),
        "strongest_domain": latest_strongest,
        "domains": domain_summaries,
        "points": points,
    }


def _ensure_storage() -> None:
    global _STORAGE_READY
    if _STORAGE_READY:
        return

    with _STORAGE_LOCK:
        if _STORAGE_READY:
            return

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        if not RESULTS_FILE.exists():
            RESULTS_FILE.write_text("[]", encoding="utf-8")

        if not _postgres_enabled():
            _STORAGE_READY = True
            return

        with _connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS storage_metadata (
                        key TEXT PRIMARY KEY,
                        value_json JSONB NOT NULL
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS assessments (
                        assessment_id TEXT PRIMARY KEY,
                        created_at TIMESTAMPTZ NOT NULL,
                        profile_encrypted BYTEA NOT NULL,
                        questionnaire_encrypted BYTEA NOT NULL,
                        multimodal_encrypted BYTEA NOT NULL,
                        encryption_key_source TEXT NOT NULL,
                        record_checksum TEXT NOT NULL
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_assessments_created_at
                    ON assessments(created_at DESC)
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        audit_id TEXT PRIMARY KEY,
                        occurred_at TIMESTAMPTZ NOT NULL,
                        actor TEXT NOT NULL,
                        action TEXT NOT NULL,
                        assessment_id TEXT NULL,
                        source_ip TEXT NULL,
                        details_encrypted BYTEA NOT NULL
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_audit_logs_occurred_at
                    ON audit_logs(occurred_at DESC)
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS backup_runs (
                        backup_id TEXT PRIMARY KEY,
                        created_at TIMESTAMPTZ NOT NULL,
                        backup_path TEXT NOT NULL,
                        backup_sha256 TEXT NOT NULL,
                        record_count INTEGER NOT NULL,
                        audit_log_count INTEGER NOT NULL,
                        size_bytes BIGINT NOT NULL
                    )
                    """
                )
                cursor.execute(
                    """
                    INSERT INTO storage_metadata (key, value_json)
                    VALUES ('schema', %s::jsonb)
                    ON CONFLICT (key) DO UPDATE SET value_json = EXCLUDED.value_json
                    """,
                    (json.dumps({"version": STORAGE_SCHEMA_VERSION, "updated_at": _utc_now().isoformat()}),),
                )
            connection.commit()

        _migrate_legacy_sources()
        _STORAGE_READY = True


def _write_audit_log(
    connection,
    *,
    action: str,
    actor: str,
    assessment_id: str | None = None,
    source_ip: str | None = None,
    details: dict | None = None,
) -> None:
    payload = {
        "assessment_id": assessment_id,
        "details": details or {},
    }
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO audit_logs (
                audit_id,
                occurred_at,
                actor,
                action,
                assessment_id,
                source_ip,
                details_encrypted
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                f"AUD-{uuid.uuid4().hex[:12].upper()}",
                _utc_now(),
                actor,
                action,
                assessment_id,
                source_ip,
                _encrypt_payload(payload),
            ),
        )


def _table_count(connection, table_name: str) -> int:
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) AS total FROM {table_name}")
        row = cursor.fetchone()
    return int(row["total"] if row else 0)


def _migrate_legacy_sources() -> None:
    with _connect() as connection:
        if _table_count(connection, "assessments") > 0:
            return

        migrated = 0
        if LEGACY_SQLITE_FILE.exists():
            migrated += _migrate_sqlite(connection, LEGACY_SQLITE_FILE)
        if migrated == 0 and RESULTS_FILE.exists():
            migrated += _migrate_json_cache(connection, RESULTS_FILE)

        if migrated > 0:
            _write_audit_log(
                connection,
                action="legacy_storage_migration",
                actor="storage.bootstrap",
                details={"migrated_records": migrated},
            )
            connection.commit()
            _sync_json_cache()


def _migrate_sqlite(connection, sqlite_path: Path) -> int:
    migrated = 0
    with sqlite3.connect(sqlite_path) as legacy_connection:
        legacy_connection.row_factory = sqlite3.Row
        try:
            rows = legacy_connection.execute(
                """
                SELECT assessment_id, created_at, profile_json, questionnaire_json, multimodal_json
                FROM assessments
                ORDER BY datetime(created_at) DESC
                """
            ).fetchall()
        except sqlite3.Error:
            return 0

    for row in rows:
        record = {
            "assessment_id": row["assessment_id"],
            "created_at": row["created_at"],
            "profile": json.loads(row["profile_json"]),
            "questionnaire": json.loads(row["questionnaire_json"]),
            "multimodal": json.loads(row["multimodal_json"]),
        }
        _insert_record(connection, record)
        migrated += 1
    return migrated


def _migrate_json_cache(connection, json_path: Path) -> int:
    try:
        cached_records = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception:
        return 0
    if not isinstance(cached_records, list):
        return 0

    migrated = 0
    for record in cached_records:
        if not isinstance(record, dict):
            continue
        _insert_record(connection, record)
        migrated += 1
    return migrated


def _insert_record(connection, record: dict) -> None:
    profile = dict(record.get("profile") or {})
    questionnaire = dict(record.get("questionnaire") or {})
    multimodal = dict(record.get("multimodal") or {})
    created_at = record.get("created_at") or _utc_now().isoformat()
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO assessments (
                assessment_id,
                created_at,
                profile_encrypted,
                questionnaire_encrypted,
                multimodal_encrypted,
                encryption_key_source,
                record_checksum
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (assessment_id) DO NOTHING
            """,
            (
                record["assessment_id"],
                created_at,
                _encrypt_payload(profile),
                _encrypt_payload(questionnaire),
                _encrypt_payload(multimodal),
                _encryption_key_source(),
                _payload_checksum(profile, questionnaire, multimodal),
            ),
        )


def _row_to_record(row: dict) -> dict:
    profile = _decrypt_payload(row["profile_encrypted"])
    return {
        "assessment_id": row["assessment_id"],
        "created_at": row["created_at"].isoformat() if hasattr(row["created_at"], "isoformat") else str(row["created_at"]),
        "profile": profile,
        "questionnaire": _decrypt_payload(row["questionnaire_encrypted"]),
        "multimodal": _decrypt_payload(row["multimodal_encrypted"]),
        "patient_key": _patient_key(profile),
        "record_origin": _record_origin(profile, fallback="backend"),
    }


def _fetch_records(connection, limit: int | None = None) -> list[dict]:
    query = """
        SELECT assessment_id, created_at, profile_encrypted, questionnaire_encrypted, multimodal_encrypted
        FROM assessments
        ORDER BY created_at DESC
    """
    params: tuple[Any, ...] = ()
    if limit is not None:
        query += " LIMIT %s"
        params = (limit,)
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()
    return [_row_to_record(row) for row in rows]


def _sync_json_cache() -> None:
    if not _postgres_enabled():
        return
    with _connect() as connection:
        records = _fetch_records(connection)
    RESULTS_FILE.write_text(json.dumps(records, indent=2), encoding="utf-8")


def _append_json_cache(record: dict) -> None:
    try:
        cached_records = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
        if not isinstance(cached_records, list):
            raise ValueError("Cache payload is not a list.")
        cached_records.insert(0, record)
        RESULTS_FILE.write_text(json.dumps(cached_records, indent=2), encoding="utf-8")
    except Exception:
        _sync_json_cache()


def _legacy_load_records() -> list[dict]:
    try:
        payload = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return [record for record in payload if isinstance(record, dict)]
    except Exception:
        pass

    if not LEGACY_SQLITE_FILE.exists():
        return []
    try:
        with sqlite3.connect(LEGACY_SQLITE_FILE) as legacy_connection:
            legacy_connection.row_factory = sqlite3.Row
            rows = legacy_connection.execute(
                """
                SELECT assessment_id, created_at, profile_json, questionnaire_json, multimodal_json
                FROM assessments
                ORDER BY datetime(created_at) DESC
                """
            ).fetchall()
    except sqlite3.Error:
        return []

    records = []
    for row in rows:
        profile = json.loads(row["profile_json"])
        record = {
            "assessment_id": row["assessment_id"],
            "created_at": row["created_at"],
            "profile": profile,
            "questionnaire": json.loads(row["questionnaire_json"]),
            "multimodal": json.loads(row["multimodal_json"]),
            "patient_key": _patient_key(profile),
            "record_origin": _record_origin(profile, fallback="backend"),
        }
        records.append(record)
    return records


def create_assessment_record(
    profile: dict,
    questionnaire: dict,
    multimodal: dict,
    *,
    actor: str = "application",
    source_ip: str | None = None,
) -> dict:
    _ensure_storage()
    stored_profile = dict(profile or {})
    stored_profile["record_origin"] = _record_origin(stored_profile, fallback="test")
    record = {
        "assessment_id": f"MHS-{uuid.uuid4().hex[:8].upper()}",
        "created_at": _utc_now().isoformat(),
        "profile": stored_profile,
        "questionnaire": questionnaire,
        "multimodal": multimodal,
        "record_origin": _record_origin(stored_profile, fallback="test"),
    }
    record["patient_key"] = _patient_key(stored_profile)

    if not _postgres_enabled():
        existing = _legacy_load_records()
        existing.insert(0, record)
        RESULTS_FILE.write_text(json.dumps(existing, indent=2), encoding="utf-8")
        return record

    with _connect() as connection:
        _insert_record(connection, record)
        _write_audit_log(
            connection,
            action="assessment_created",
            actor=actor,
            assessment_id=record["assessment_id"],
            source_ip=source_ip,
            details={
                "profile_fields": sorted(profile.keys()),
                "questionnaire_fields": sorted(questionnaire.keys()),
                "multimodal_keys": sorted(multimodal.keys()),
            },
        )
        connection.commit()

    _append_json_cache(record)
    return record


def fetch_assessment_record(
    assessment_id: str,
    *,
    actor: str = "application",
    source_ip: str | None = None,
) -> dict | None:
    _ensure_storage()
    normalized = assessment_id.strip().upper()
    if not _postgres_enabled():
        for record in _legacy_load_records():
            if str(record.get("assessment_id", "")).upper() == normalized:
                record.setdefault("patient_key", _patient_key(record.get("profile") or {}))
                return record
        return None
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT assessment_id, created_at, profile_encrypted, questionnaire_encrypted, multimodal_encrypted
                FROM assessments
                WHERE UPPER(assessment_id) = %s
                """,
                (normalized,),
            )
            row = cursor.fetchone()

        _write_audit_log(
            connection,
            action="assessment_fetched",
            actor=actor,
            assessment_id=normalized,
            source_ip=source_ip,
            details={"found": bool(row)},
        )
        connection.commit()

    if row is None:
        return None
    return _row_to_record(row)


def delete_assessment_record(
    assessment_id: str,
    *,
    actor: str = "application",
    source_ip: str | None = None,
) -> bool:
    _ensure_storage()
    normalized = assessment_id.strip().upper()
    if not normalized:
        return False

    if not _postgres_enabled():
        records = _legacy_load_records()
        remaining = [record for record in records if str(record.get("assessment_id", "")).upper() != normalized]
        deleted = len(remaining) != len(records)
        if deleted:
            RESULTS_FILE.write_text(json.dumps(remaining, indent=2), encoding="utf-8")
        return deleted

    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM assessments
                WHERE UPPER(assessment_id) = %s
                RETURNING assessment_id
                """,
                (normalized,),
            )
            row = cursor.fetchone()
        _write_audit_log(
            connection,
            action="assessment_deleted",
            actor=actor,
            assessment_id=normalized,
            source_ip=source_ip,
            details={"deleted": bool(row)},
        )
        connection.commit()

    if row is not None:
        _sync_json_cache()
    return row is not None


def list_assessment_records(
    limit: int | None = None,
    *,
    audit_actor: str = "application",
    source_ip: str | None = None,
) -> list[dict]:
    _ensure_storage()
    if limit is not None:
        limit = max(1, min(int(limit), MAX_LIST_LIMIT))

    if not _postgres_enabled():
        rows = _legacy_load_records()
        if limit is not None:
            rows = rows[:limit]
        for row in rows:
            row.setdefault("patient_key", _patient_key(row.get("profile") or {}))
        return rows

    with _connect() as connection:
        rows = _fetch_records(connection, limit=limit)
        _write_audit_log(
            connection,
            action="assessments_listed",
            actor=audit_actor,
            source_ip=source_ip,
            details={"limit": limit, "returned_count": len(rows)},
        )
        connection.commit()
    return rows


def build_assessment_trajectory(
    assessment_id: str,
    *,
    actor: str = "application",
    source_ip: str | None = None,
) -> dict | None:
    _ensure_storage()
    normalized = assessment_id.strip().upper()
    if not _postgres_enabled():
        records = list_assessment_records(limit=None)
        target_record = next((record for record in records if record["assessment_id"].upper() == normalized), None)
        if target_record is None:
            return None
        patient_key = target_record.get("patient_key") or _patient_key(target_record.get("profile") or {})
        patient_history = [
            record for record in records
            if (record.get("patient_key") or _patient_key(record.get("profile") or {})) == patient_key
        ]
        return _build_trajectory_summary(patient_history, patient_key)
    with _connect() as connection:
        records = _fetch_records(connection)
        target_record = next((record for record in records if record["assessment_id"].upper() == normalized), None)
        patient_key = target_record.get("patient_key", "unknown") if target_record else "unknown"
        patient_history = [record for record in records if record.get("patient_key") == patient_key] if target_record else []
        _write_audit_log(
            connection,
            action="trajectory_fetched",
            actor=actor,
            assessment_id=normalized,
            source_ip=source_ip,
            details={
                "found": bool(target_record),
                "patient_key": patient_key,
                "history_count": len(patient_history),
            },
        )
        connection.commit()

    if target_record is None:
        return None
    return _build_trajectory_summary(patient_history, patient_key)


def list_audit_logs(limit: int | None = 100) -> list[dict]:
    _ensure_storage()
    if not _postgres_enabled():
        return []
    safe_limit = max(1, min(int(limit or 100), MAX_AUDIT_LIMIT))
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT audit_id, occurred_at, actor, action, assessment_id, source_ip, details_encrypted
                FROM audit_logs
                ORDER BY occurred_at DESC
                LIMIT %s
                """,
                (safe_limit,),
            )
            rows = cursor.fetchall()

    results = []
    for row in rows:
        decrypted = _decrypt_payload(row["details_encrypted"])
        results.append(
            {
                "audit_id": row["audit_id"],
                "occurred_at": row["occurred_at"].isoformat() if hasattr(row["occurred_at"], "isoformat") else str(row["occurred_at"]),
                "actor": row["actor"],
                "action": row["action"],
                "assessment_id": row["assessment_id"],
                "source_ip": row["source_ip"],
                "details": decrypted.get("details", {}),
            }
        )
    return results


def create_database_backup(
    output_path: str | Path | None = None,
    *,
    actor: str = "application",
    source_ip: str | None = None,
    include_audit_logs: bool = True,
) -> dict:
    _ensure_storage()
    backup_id = f"BKP-{uuid.uuid4().hex[:10].upper()}"
    timestamp = _utc_now().strftime("%Y%m%dT%H%M%SZ")
    backup_path = Path(output_path) if output_path else BACKUP_DIR / f"{timestamp}_{backup_id}.backup.enc"

    if not _postgres_enabled():
        records = _legacy_load_records()
        backup_payload = {
            "backup_id": backup_id,
            "created_at": _utc_now().isoformat(),
            "database": "JSON fallback",
            "database_url": None,
            "schema_version": STORAGE_SCHEMA_VERSION,
            "encryption_key_source": _encryption_key_source(),
            "assessments": records,
            "audit_logs": [],
        }
        compressed = gzip.compress(json.dumps(backup_payload, ensure_ascii=True, separators=(",", ":")).encode("utf-8"))
        encrypted_backup = _fernet().encrypt(compressed)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        backup_path.write_bytes(encrypted_backup)
        checksum = hashlib.sha256(encrypted_backup).hexdigest()
        size_bytes = backup_path.stat().st_size
        return {
            "backup_id": backup_id,
            "backup_path": str(backup_path.resolve()),
            "backup_sha256": checksum,
            "record_count": len(records),
            "audit_log_count": 0,
            "size_bytes": size_bytes,
            "encrypted": True,
        }

    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT assessment_id, created_at, profile_encrypted, questionnaire_encrypted, multimodal_encrypted,
                       encryption_key_source, record_checksum
                FROM assessments
                ORDER BY created_at DESC
                """
            )
            assessment_rows = cursor.fetchall()

            audit_rows: list[dict] = []
            if include_audit_logs:
                cursor.execute(
                    """
                    SELECT audit_id, occurred_at, actor, action, assessment_id, source_ip, details_encrypted
                    FROM audit_logs
                    ORDER BY occurred_at DESC
                    """
                )
                audit_rows = cursor.fetchall()

        backup_payload = {
            "backup_id": backup_id,
            "created_at": _utc_now().isoformat(),
            "database": "PostgreSQL",
            "database_url": _masked_database_url(),
            "schema_version": STORAGE_SCHEMA_VERSION,
            "encryption_key_source": _encryption_key_source(),
            "assessments": [
                {
                    "assessment_id": row["assessment_id"],
                    "created_at": row["created_at"].isoformat() if hasattr(row["created_at"], "isoformat") else str(row["created_at"]),
                    "profile_encrypted_b64": base64.b64encode(bytes(row["profile_encrypted"])).decode("ascii"),
                    "questionnaire_encrypted_b64": base64.b64encode(bytes(row["questionnaire_encrypted"])).decode("ascii"),
                    "multimodal_encrypted_b64": base64.b64encode(bytes(row["multimodal_encrypted"])).decode("ascii"),
                    "encryption_key_source": row["encryption_key_source"],
                    "record_checksum": row["record_checksum"],
                }
                for row in assessment_rows
            ],
            "audit_logs": [
                {
                    "audit_id": row["audit_id"],
                    "occurred_at": row["occurred_at"].isoformat() if hasattr(row["occurred_at"], "isoformat") else str(row["occurred_at"]),
                    "actor": row["actor"],
                    "action": row["action"],
                    "assessment_id": row["assessment_id"],
                    "source_ip": row["source_ip"],
                    "details_encrypted_b64": base64.b64encode(bytes(row["details_encrypted"])).decode("ascii"),
                }
                for row in audit_rows
            ],
        }

        compressed = gzip.compress(json.dumps(backup_payload, ensure_ascii=True, separators=(",", ":")).encode("utf-8"))
        encrypted_backup = _fernet().encrypt(compressed)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        backup_path.write_bytes(encrypted_backup)
        checksum = hashlib.sha256(encrypted_backup).hexdigest()
        size_bytes = backup_path.stat().st_size

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO backup_runs (
                    backup_id,
                    created_at,
                    backup_path,
                    backup_sha256,
                    record_count,
                    audit_log_count,
                    size_bytes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    backup_id,
                    _utc_now(),
                    str(backup_path.resolve()),
                    checksum,
                    len(assessment_rows),
                    len(audit_rows),
                    size_bytes,
                ),
            )
        _write_audit_log(
            connection,
            action="backup_created",
            actor=actor,
            source_ip=source_ip,
            details={
                "backup_id": backup_id,
                "backup_path": str(backup_path.resolve()),
                "record_count": len(assessment_rows),
                "audit_log_count": len(audit_rows),
                "size_bytes": size_bytes,
            },
        )
        connection.commit()

    return {
        "backup_id": backup_id,
        "backup_path": str(backup_path.resolve()),
        "backup_sha256": checksum,
        "record_count": len(assessment_rows),
        "audit_log_count": len(audit_rows),
        "size_bytes": size_bytes,
        "encrypted": True,
    }


def list_backup_runs(limit: int | None = 20) -> list[dict]:
    _ensure_storage()
    if not _postgres_enabled():
        return []
    safe_limit = max(1, min(int(limit or 20), 100))
    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT backup_id, created_at, backup_path, backup_sha256, record_count, audit_log_count, size_bytes
                FROM backup_runs
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (safe_limit,),
            )
            rows = cursor.fetchall()
    return [
        {
            "backup_id": row["backup_id"],
            "created_at": row["created_at"].isoformat() if hasattr(row["created_at"], "isoformat") else str(row["created_at"]),
            "backup_path": row["backup_path"],
            "backup_sha256": row["backup_sha256"],
            "record_count": row["record_count"],
            "audit_log_count": row["audit_log_count"],
            "size_bytes": row["size_bytes"],
        }
        for row in rows
    ]


def get_database_metadata() -> dict:
    _ensure_storage()
    if not _postgres_enabled():
        records = _legacy_load_records()
        return {
            "database": "JSON fallback",
            "database_url": None,
            "cache_path": str(RESULTS_FILE),
            "backup_dir": str(BACKUP_DIR),
            "legacy_sqlite_path": str(LEGACY_SQLITE_FILE),
            "total_records": len(records),
            "total_audit_logs": 0,
            "total_backups": 0,
            "encryption_at_rest": False,
            "encryption_key_source": _encryption_key_source(),
            "schema_version": STORAGE_SCHEMA_VERSION,
            "longitudinal_tracking": True,
            "storage_mode": "fallback_without_psycopg",
        }
    with _connect() as connection:
        total_records = _table_count(connection, "assessments")
        total_audit_logs = _table_count(connection, "audit_logs")
        total_backups = _table_count(connection, "backup_runs")
    return {
        "database": "PostgreSQL",
        "database_url": _masked_database_url(),
        "cache_path": str(RESULTS_FILE),
        "backup_dir": str(BACKUP_DIR),
        "legacy_sqlite_path": str(LEGACY_SQLITE_FILE),
        "total_records": total_records,
        "total_audit_logs": total_audit_logs,
        "total_backups": total_backups,
        "encryption_at_rest": True,
        "encryption_key_source": _encryption_key_source(),
        "schema_version": STORAGE_SCHEMA_VERSION,
        "longitudinal_tracking": True,
    }
