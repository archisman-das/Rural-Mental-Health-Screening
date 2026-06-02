import json
import os
import sys
import tempfile
from pathlib import Path

from flask import Flask, Response, jsonify, request, send_from_directory

ROOT = Path(__file__).resolve().parent
SRC_PATH = str(ROOT / "src")
if SRC_PATH not in sys.path:
    sys.path.append(SRC_PATH)

from mental_health_screening.constants import PREDICTION_DOMAINS, PREDICTION_LABELS
from mental_health_screening.predict import screen
from mental_health_screening.report import create_assessment_pdf_bytes
from mental_health_screening.storage import (
    create_assessment_record,
    fetch_assessment_record,
    get_database_metadata,
    list_assessment_records,
)
from mental_health_screening.utils import average, normalize_score, risk_level


app = Flask(__name__, static_folder=str(ROOT / "web"), static_url_path="/web")


def _modality_failure_note(modality: str, reason: str | None, result: dict | None = None) -> str:
    if modality == "audio" and reason == "audio_too_short":
        duration = round(float((result or {}).get("duration", 0.0)), 2)
        minimum = round(float((result or {}).get("minimum_duration", 2.5)), 2)
        return f"Audio upload was received, but it was too short for analysis ({duration}s). Minimum required duration is {minimum}s."
    if modality == "audio" and reason == "librosa_not_installed":
        return "Audio upload was received, but backend audio dependencies are not installed on this machine."
    if modality == "audio" and reason == "audio_invalid_duration":
        return "Audio upload was received, but the clip duration could not be validated for analysis."
    if modality == "image" and reason == "no_face_detected":
        return "Image upload was received, but no detectable face was found, so facial-cue analysis was skipped."
    if modality == "image" and reason == "vision_dependencies_not_installed":
        return "Image upload was received, but backend vision dependencies are not installed on this machine."
    if modality == "image" and reason == "image_unreadable":
        return "Image upload was received, but the backend could not read it as a usable image."
    return (
        f"Dashboard captured {modality} upload metadata for {(result or {}).get('features', {}).get('file_name', 'the uploaded file')}. "
        f"The file reached the backend, but no usable {modality} inference result was produced from it."
    )


def _metadata_modality(modality: str, metadata: dict | None, reason: str | None = None, source_result: dict | None = None) -> dict:
    if not isinstance(metadata, dict) or not metadata:
        return {"available": False}

    payload = {
        "available": False,
        "modality": modality,
        "confidence": 0.2,
        "notes": _modality_failure_note(modality, reason, source_result),
        "features": {
            "upload_received": True,
            "file_name": metadata.get("file_name", "unknown"),
            "file_size_kb": metadata.get("file_size_kb", 0),
            "mime_type": metadata.get("mime_type", "unknown"),
        },
    }
    if reason:
        payload["features"]["precheck_reason"] = reason
    if isinstance(source_result, dict):
        for key in ("duration", "minimum_duration", "reason"):
            if key in source_result:
                payload["features"][key] = source_result[key]
    for domain in PREDICTION_DOMAINS:
        payload[f"{domain}_score"] = 0.0
    return payload


def _parse_json_field(value: str | None, default):
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def _save_uploaded_file(file_storage, suffix: str) -> tuple[str | None, dict | None]:
    if file_storage is None or not getattr(file_storage, "filename", ""):
        return None, None

    _, extension = os.path.splitext(file_storage.filename)
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"{suffix}{extension}") as handle:
        file_storage.save(handle.name)
        path = handle.name

    metadata = {
        "file_name": file_storage.filename,
        "file_size_kb": round(os.path.getsize(path) / 1024),
        "mime_type": file_storage.mimetype or "unknown",
    }
    return path, metadata


def _cleanup_temp_paths(*paths: str | None) -> None:
    for path in paths:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass


def _decorate_modality_result(result: dict, metadata: dict | None, modality: str) -> dict:
    if result.get("available"):
        features = dict(result.get("features") or {})
        if metadata:
            features.update(metadata)
        return {
            **result,
            "modality": modality,
            "features": features,
        }
    return _metadata_modality(modality, metadata, reason=result.get("reason"), source_result=result)


def _build_dashboard_recommendation(overall: dict) -> str:
    high = [domain for domain in PREDICTION_DOMAINS if overall.get(domain) == "high"]
    moderate = [domain for domain in PREDICTION_DOMAINS if overall.get(domain) == "moderate"]

    if high:
        joined = ", ".join(PREDICTION_LABELS[domain].lower() for domain in high)
        return f"High risk detected for {joined}. Arrange guided follow-up and mental health referral as soon as possible."
    if moderate:
        joined = ", ".join(PREDICTION_LABELS[domain].lower() for domain in moderate)
        return f"Moderate risk detected for {joined}. Plan a structured follow-up conversation and repeat screening."
    return "Current dashboard signals are low risk. Continue monitoring and re-screen if symptoms persist or worsen."


def _questionnaire_completeness(questionnaire: dict) -> float:
    scored_keys = [f"{domain}_score" for domain in PREDICTION_DOMAINS]
    present = sum(1 for key in scored_keys if key in questionnaire and questionnaire.get(key) is not None)
    return normalize_score(present / len(scored_keys)) if scored_keys else 0.0


def _questionnaire_screening_agreement(questionnaire: dict, screening_scores: dict) -> float:
    agreements = []
    for domain in PREDICTION_DOMAINS:
        questionnaire_score = normalize_score(questionnaire.get(f"{domain}_score", 0.0))
        screening_score = normalize_score(screening_scores.get(domain, questionnaire_score))
        agreements.append(1.0 - abs(questionnaire_score - screening_score))
    return normalize_score(average(agreements)) if agreements else 0.0


def _dashboard_confidence(questionnaire: dict, screening_overall: dict, modalities: list[dict]) -> float:
    available_modalities = [modality for modality in modalities if modality.get("available")]
    if not available_modalities:
        return normalize_score(0.5 + 0.25 * _questionnaire_completeness(questionnaire))

    modality_coverage = normalize_score(
        sum(1 for modality in modalities if modality.get("available")) / max(1, len(modalities))
    )
    modality_confidence = average([float(modality.get("confidence", 0.0)) for modality in available_modalities])
    questionnaire_completeness = _questionnaire_completeness(questionnaire)
    agreement = _questionnaire_screening_agreement(questionnaire, screening_overall.get("scores", {}))

    return normalize_score(
        0.4 * modality_confidence
        + 0.2 * modality_coverage
        + 0.2 * questionnaire_completeness
        + 0.2 * agreement
    )


def _build_dashboard_multimodal(
    text_input: str,
    questionnaire: dict,
    audio_path: str | None = None,
    image_path: str | None = None,
    audio_metadata: dict | None = None,
    image_metadata: dict | None = None,
) -> dict:
    screening = screen(
        text_input=text_input or "",
        audio_path=audio_path,
        image_path=image_path,
    )
    text_result = screening.get("text") or {"available": False}
    audio_result = _decorate_modality_result(screening.get("audio") or {"available": False}, audio_metadata, "audio")
    image_result = _decorate_modality_result(screening.get("image") or {"available": False}, image_metadata, "image")
    screening_overall = screening.get("overall") or {"confidence": 0.0, "scores": {}}
    overall_scores = {}
    overall_levels = {}

    for domain in PREDICTION_DOMAINS:
        questionnaire_score = normalize_score(questionnaire.get(f"{domain}_score", 0.0))
        screening_score = normalize_score(screening_overall.get("scores", {}).get(domain, questionnaire_score))
        has_screening_signal = any(
            modality.get("available")
            for modality in (text_result, audio_result, image_result)
        )
        combined_score = normalize_score(average([questionnaire_score, screening_score])) if has_screening_signal else questionnaire_score
        overall_scores[domain] = combined_score
        overall_levels[domain] = risk_level(combined_score)

    overall_confidence = _dashboard_confidence(
        questionnaire=questionnaire,
        screening_overall=screening_overall,
        modalities=[text_result, audio_result, image_result],
    )
    overall = {
        **overall_levels,
        "confidence": normalize_score(overall_confidence),
        "scores": overall_scores,
    }

    return {
        "text": text_result,
        "audio": audio_result,
        "image": image_result,
        "overall": overall,
        "recommendation": _build_dashboard_recommendation(overall),
        "disclaimer": screening.get(
            "disclaimer",
            "This dashboard provides an early screening summary only. It does not replace diagnosis, emergency support, or clinician judgment.",
        ),
    }


def _extract_request_payload():
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        return {
            "profile": payload.get("profile"),
            "questionnaire": payload.get("questionnaire"),
            "multimodal": payload.get("multimodal"),
            "text_input": payload.get("text_input", ""),
            "audio_metadata": payload.get("audio_metadata"),
            "image_metadata": payload.get("image_metadata"),
            "audio_path": None,
            "image_path": None,
        }

    profile = _parse_json_field(request.form.get("profile"), {})
    questionnaire = _parse_json_field(request.form.get("questionnaire"), {})
    multimodal = _parse_json_field(request.form.get("multimodal"), None)
    text_input = request.form.get("text_input", "")
    audio_path, audio_metadata = _save_uploaded_file(request.files.get("audio_file"), "_audio")
    image_path, image_metadata = _save_uploaded_file(request.files.get("image_file"), "_image")
    return {
        "profile": profile,
        "questionnaire": questionnaire,
        "multimodal": multimodal,
        "text_input": text_input,
        "audio_metadata": audio_metadata,
        "image_metadata": image_metadata,
        "audio_path": audio_path,
        "image_path": image_path,
    }


@app.get("/")
def root():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok", "database": get_database_metadata()})


@app.get("/api/assessments")
def api_list_assessments():
    limit = request.args.get("limit", type=int)
    return jsonify(list_assessment_records(limit=limit))


@app.post("/api/assessments")
def api_create_assessment():
    payload = _extract_request_payload()
    profile = payload["profile"]
    questionnaire = payload["questionnaire"]
    multimodal = payload["multimodal"]

    if not isinstance(profile, dict) or not isinstance(questionnaire, dict):
        _cleanup_temp_paths(payload["audio_path"], payload["image_path"])
        return jsonify({"error": "Invalid payload. Expected profile and questionnaire objects."}), 400
    try:
        if not isinstance(multimodal, dict):
            multimodal = _build_dashboard_multimodal(
                text_input=payload["text_input"],
                questionnaire=questionnaire,
                audio_path=payload["audio_path"],
                image_path=payload["image_path"],
                audio_metadata=payload["audio_metadata"],
                image_metadata=payload["image_metadata"],
            )

        record = create_assessment_record(
            profile=profile,
            questionnaire=questionnaire,
            multimodal=multimodal,
        )
        return jsonify(record), 201
    finally:
        _cleanup_temp_paths(payload["audio_path"], payload["image_path"])


@app.post("/api/preview")
def api_preview_assessment():
    payload = _extract_request_payload()
    questionnaire = payload["questionnaire"] or {}

    if not isinstance(questionnaire, dict):
        _cleanup_temp_paths(payload["audio_path"], payload["image_path"])
        return jsonify({"error": "Invalid payload. Expected questionnaire object."}), 400
    try:
        return jsonify(
            _build_dashboard_multimodal(
                text_input=payload["text_input"],
                questionnaire=questionnaire,
                audio_path=payload["audio_path"],
                image_path=payload["image_path"],
                audio_metadata=payload["audio_metadata"],
                image_metadata=payload["image_metadata"],
            )
        )
    finally:
        _cleanup_temp_paths(payload["audio_path"], payload["image_path"])


@app.get("/api/assessments/<assessment_id>")
def api_fetch_assessment(assessment_id: str):
    record = fetch_assessment_record(assessment_id)
    if record is None:
        return jsonify({"error": "Assessment not found."}), 404
    return jsonify(record)


@app.get("/api/assessments/<assessment_id>/report.pdf")
def api_assessment_pdf(assessment_id: str):
    record = fetch_assessment_record(assessment_id)
    if record is None:
        return jsonify({"error": "Assessment not found."}), 404

    pdf_bytes = create_assessment_pdf_bytes(record)
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{record["assessment_id"]}_report.pdf"',
        },
    )


@app.get("/api/database")
def api_database_metadata():
    return jsonify(get_database_metadata())


@app.get("/api/sample")
def api_sample_dataset():
    sample_path = ROOT / "web" / "sample-results.json"
    if not sample_path.exists():
        return jsonify([])
    return Response(sample_path.read_text(encoding="utf-8"), mimetype="application/json")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False)
