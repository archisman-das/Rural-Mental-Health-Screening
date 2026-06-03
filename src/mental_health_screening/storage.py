import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
RESULTS_FILE = DATA_DIR / "screening_results.json"
DB_FILE = DATA_DIR / "screening_results.db"
MAX_LIST_LIMIT = 250


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_FILE, timeout=30)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA synchronous=NORMAL")
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("PRAGMA busy_timeout=30000")
    return connection


def _ensure_storage() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not RESULTS_FILE.exists():
        RESULTS_FILE.write_text("[]", encoding="utf-8")

    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS assessments (
                assessment_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                profile_json TEXT NOT NULL,
                questionnaire_json TEXT NOT NULL,
                multimodal_json TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_assessments_created_at
            ON assessments(created_at DESC)
            """
        )
        connection.commit()

    _migrate_json_cache_to_sqlite()


def _migrate_json_cache_to_sqlite() -> None:
    if not RESULTS_FILE.exists():
        return

    cached_records = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    if not cached_records:
        return

    with _connect() as connection:
        existing_count = connection.execute("SELECT COUNT(*) FROM assessments").fetchone()[0]
        if existing_count > 0:
            return

        for record in cached_records:
            connection.execute(
                """
                INSERT OR IGNORE INTO assessments (
                    assessment_id,
                    created_at,
                    profile_json,
                    questionnaire_json,
                    multimodal_json
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    record["assessment_id"],
                    record["created_at"],
                    json.dumps(record["profile"]),
                    json.dumps(record["questionnaire"]),
                    json.dumps(record["multimodal"]),
                ),
            )
        connection.commit()


def _row_to_record(row: sqlite3.Row) -> dict:
    return {
        "assessment_id": row["assessment_id"],
        "created_at": row["created_at"],
        "profile": json.loads(row["profile_json"]),
        "questionnaire": json.loads(row["questionnaire_json"]),
        "multimodal": json.loads(row["multimodal_json"]),
    }


def _sync_json_cache() -> None:
    records = list_assessment_records()
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


def create_assessment_record(profile: dict, questionnaire: dict, multimodal: dict) -> dict:
    _ensure_storage()
    record = {
        "assessment_id": f"MHS-{uuid.uuid4().hex[:8].upper()}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "profile": profile,
        "questionnaire": questionnaire,
        "multimodal": multimodal,
    }

    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO assessments (
                assessment_id,
                created_at,
                profile_json,
                questionnaire_json,
                multimodal_json
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                record["assessment_id"],
                record["created_at"],
                json.dumps(record["profile"]),
                json.dumps(record["questionnaire"]),
                json.dumps(record["multimodal"]),
            ),
        )
        connection.commit()

    _append_json_cache(record)
    return record


def fetch_assessment_record(assessment_id: str) -> dict | None:
    _ensure_storage()
    normalized = assessment_id.strip().upper()
    with _connect() as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            """
            SELECT assessment_id, created_at, profile_json, questionnaire_json, multimodal_json
            FROM assessments
            WHERE UPPER(assessment_id) = ?
            """,
            (normalized,),
        ).fetchone()

    if row is None:
        return None
    return _row_to_record(row)


def list_assessment_records(limit: int | None = None) -> list[dict]:
    _ensure_storage()
    if limit is not None:
        limit = max(1, min(int(limit), MAX_LIST_LIMIT))
    query = """
        SELECT assessment_id, created_at, profile_json, questionnaire_json, multimodal_json
        FROM assessments
        ORDER BY datetime(created_at) DESC
    """
    params: tuple = ()
    if limit is not None:
        query += " LIMIT ?"
        params = (limit,)

    with sqlite3.connect(DB_FILE) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(query, params).fetchall()
    return [_row_to_record(row) for row in rows]


def get_database_metadata() -> dict:
    _ensure_storage()
    with sqlite3.connect(DB_FILE) as connection:
        total_records = connection.execute("SELECT COUNT(*) FROM assessments").fetchone()[0]
    return {
        "database": "SQLite",
        "database_path": str(DB_FILE),
        "cache_path": str(RESULTS_FILE),
        "total_records": total_records,
    }
