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

from mental_health_screening import get_adaptive_question_bank, get_adaptive_tuning, get_response_options
from mental_health_screening.constants import PREDICTION_DOMAINS, PREDICTION_LABELS
from mental_health_screening.predict import screen
from mental_health_screening.report import create_assessment_pdf_bytes
from mental_health_screening.model_store import summarize_all_bundles
from mental_health_screening.storage import (
    build_assessment_trajectory,
    delete_assessment_record,
    create_assessment_record,
    create_database_backup,
    fetch_assessment_record,
    get_database_metadata,
    list_assessment_records,
    list_audit_logs,
    list_backup_runs,
)
from mental_health_screening.utils import average, normalize_score, risk_level


app = Flask(__name__, static_folder=str(ROOT / "web"), static_url_path="/web")
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

MAX_TEXT_INPUT_LENGTH = 5000
LIST_LIMIT_DEFAULT = 50
LIST_LIMIT_MAX = 250


def _json_error(message: str, status_code: int = 400, details: dict | None = None):
    payload = {"error": message}
    if details:
        payload["details"] = details
    return jsonify(payload), status_code


def _clean_text(value: str | None, max_length: int | None = None) -> str:
    text = str(value or "").strip()
    if max_length is not None:
        return text[:max_length]
    return text


def _normalize_language(value: str | None) -> str:
    text = _clean_text(value, 30).lower()
    if text in {"hindi", "hi", "हिंदी"}:
        return "Hindi"
    if text in {"bengali", "bangla", "bn", "বাংলা", "বাঙলা"}:
        return "Bengali"
    return "English"


def _normalize_profile(profile: dict | None) -> dict:
    safe_profile = profile if isinstance(profile, dict) else {}
    age_value = safe_profile.get("age", 0)
    try:
        age = int(age_value)
    except (TypeError, ValueError):
        age = 0
    age = max(0, min(age, 120))
    normalized_language = _normalize_language(safe_profile.get("language") or "English")
    return {
        "full_name": _clean_text(safe_profile.get("full_name"), 120),
        "age": age,
        "gender": _clean_text(safe_profile.get("gender") or "Prefer not to say", 40) or "Prefer not to say",
        "village": _clean_text(safe_profile.get("village"), 120),
        "phone": _clean_text(safe_profile.get("phone"), 40),
        "assessor": _clean_text(safe_profile.get("assessor"), 120),
        "language": normalized_language,
        "consent_received": bool(safe_profile.get("consent_received")),
        "record_origin": _clean_text(safe_profile.get("record_origin") or "test", 30).lower(),
    }


def _normalize_questionnaire(questionnaire: dict | None) -> dict:
    if not isinstance(questionnaire, dict):
        return {}
    safe_questionnaire = {
        "available": bool(questionnaire.get("available", True)),
        "notes": _clean_text(questionnaire.get("notes"), 500),
    }
    for domain in PREDICTION_DOMAINS:
        safe_questionnaire[f"{domain}_score"] = normalize_score(questionnaire.get(f"{domain}_score", 0.0))
        safe_questionnaire[f"{domain}_risk"] = risk_level(safe_questionnaire[f"{domain}_score"])
    safe_questionnaire["overall_score"] = normalize_score(
        average([safe_questionnaire[f"{domain}_score"] for domain in PREDICTION_DOMAINS])
    )
    return safe_questionnaire


def _validate_assessment_payload(profile: dict, questionnaire: dict, require_consent: bool = True) -> dict | None:
    if not profile.get("full_name"):
        return {"field": "full_name", "message": "Candidate full name is required."}
    if not profile.get("village"):
        return {"field": "village", "message": "Village or local area is required."}
    if not profile.get("assessor"):
        return {"field": "assessor", "message": "Assessor name is required."}
    if require_consent and not profile.get("consent_received"):
        return {"field": "consent_received", "message": "Consent is required before saving an assessment."}
    missing_scores = [
        domain for domain in PREDICTION_DOMAINS
        if f"{domain}_score" not in questionnaire
    ]
    if missing_scores:
        return {"field": "questionnaire", "message": "Questionnaire scores are incomplete.", "missing_domains": missing_scores}
    return None


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
    if modality == "passive_biomarkers" and reason == "passive_signals_missing":
        return "Passive biomarkers were not provided, so zero-hardware analysis from camera or typing rhythm was skipped."
    if modality == "passive_biomarkers" and reason == "video_missing":
        return "The phone-camera video signal was not provided, so rPPG-style analysis was skipped."
    if modality == "passive_biomarkers" and reason == "vision_dependencies_not_installed":
        return "The phone-camera video was received, but backend vision dependencies are not installed on this machine."
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


def _build_dashboard_recommendation(overall: dict, language: str = "english") -> str:
    language = str(language or "english").strip().lower()
    high = [domain for domain in PREDICTION_DOMAINS if overall.get(domain) == "high"]
    moderate = [domain for domain in PREDICTION_DOMAINS if overall.get(domain) == "moderate"]

    if language == "hindi":
        if high:
            joined = ", ".join(PREDICTION_LABELS[domain].lower() for domain in high)
            return f"{joined} के लिए उच्च जोखिम संकेत मिला। संरचित फॉलो-अप और मानसिक स्वास्थ्य रेफरल जल्द करें।"
        if moderate:
            joined = ", ".join(PREDICTION_LABELS[domain].lower() for domain in moderate)
            return f"{joined} के लिए मध्यम जोखिम संकेत मिला। फॉलो-अप बातचीत और दोबारा स्क्रीनिंग की योजना बनाएं।"
        return "वर्तमान संकेत कम जोखिम दिखाते हैं। लक्षण बने रहें या बढ़ें तो निगरानी और दोबारा स्क्रीनिंग करें।"

    if language == "bengali":
        if high:
            joined = ", ".join(PREDICTION_LABELS[domain].lower() for domain in high)
            return f"{joined} এর জন্য উচ্চ ঝুঁকির ইঙ্গিত পাওয়া গেছে। দ্রুত ফলো-আপ ও মানসিক স্বাস্থ্য রেফারাল প্রয়োজন।"
        if moderate:
            joined = ", ".join(PREDICTION_LABELS[domain].lower() for domain in moderate)
            return f"{joined} এর জন্য মাঝারি ঝুঁকির ইঙ্গিত পাওয়া গেছে। ফলো-আপ আলোচনা ও পুনরায় স্ক্রিনিং পরিকল্পনা করুন।"
        return "বর্তমান সংকেত কম ঝুঁকি দেখাচ্ছে। উপসর্গ থাকলে বা বাড়লে পর্যবেক্ষণ ও পুনরায় স্ক্রিনিং করুন।"

    if high:
        joined = ", ".join(PREDICTION_LABELS[domain].lower() for domain in high)
        return f"High risk detected for {joined}. Arrange guided follow-up and mental health referral as soon as possible."
    if moderate:
        joined = ", ".join(PREDICTION_LABELS[domain].lower() for domain in moderate)
        return f"Moderate risk detected for {joined}. Plan a structured follow-up conversation and repeat screening."
    return "Current dashboard signals are low risk. Continue monitoring and re-screen if symptoms persist or worsen."


def _comorbidity_note(comorbidity: dict | None, language: str = "english") -> str:
    if not comorbidity:
        return ""
    top_pairs = comorbidity.get("top_pairs") or []
    if not top_pairs:
        return ""
    top_pair = top_pairs[0]
    if float(top_pair.get("probability", 0.0) or 0.0) < 0.55:
        return ""
    domains = top_pair.get("domains") or []
    if len(domains) != 2:
        return ""
    joined = " + ".join(PREDICTION_LABELS.get(domain, domain.title()) for domain in domains)
    language = str(language or "english").strip().lower()
    if language == "hindi":
        return f"संयुक्त comorbidity संकेत: {joined} साथ-साथ बढ़ रहे हैं; एकीकृत follow-up पर विचार करें।"
    if language == "bengali":
        return f"সমন্বিত comorbidity সংকেত: {joined} একসঙ্গে বাড়ছে; সমন্বিত follow-up বিবেচনা করুন।"
    return f"Joint comorbidity signal: {joined} are trending together; consider an integrated follow-up."


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


def _comorbidity_note(comorbidity: dict | None) -> str:
    if not comorbidity:
        return ""
    top_pairs = comorbidity.get("top_pairs") or []
    if not top_pairs:
        return ""
    top_pair = top_pairs[0]
    if float(top_pair.get("probability", 0.0) or 0.0) < 0.55:
        return ""
    domains = top_pair.get("domains") or []
    if len(domains) != 2:
        return ""
    joined = " + ".join(PREDICTION_LABELS.get(domain, domain.title()) for domain in domains)
    return f"Joint comorbidity signal: {joined} are trending together; consider an integrated follow-up."


def _build_dashboard_multimodal(
    text_input: str,
    questionnaire: dict,
    language: str = "english",
    audio_path: str | None = None,
    image_path: str | None = None,
    passive_video_path: str | None = None,
    typing_events: list[dict] | dict | list[float] | None = None,
    audio_metadata: dict | None = None,
    image_metadata: dict | None = None,
    passive_metadata: dict | None = None,
) -> dict:
    screening = screen(
        text_input=text_input or "",
        audio_path=audio_path,
        image_path=image_path,
        passive_video_path=passive_video_path,
        typing_events=typing_events,
        language=language,
    )
    text_result = screening.get("text") or {"available": False}
    audio_result = _decorate_modality_result(screening.get("audio") or {"available": False}, audio_metadata, "audio")
    image_result = _decorate_modality_result(screening.get("image") or {"available": False}, image_metadata, "image")
    passive_result = _decorate_modality_result(
        screening.get("passive") or {"available": False},
        passive_metadata,
        "passive_biomarkers",
    )
    comorbidity = screening.get("comorbidity") or {}
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
    model_stats = summarize_all_bundles()
    recommendation = screening.get(
        "recommendation",
        _build_dashboard_recommendation(overall, language=language),
    )
    comorbidity_note = _comorbidity_note(comorbidity, language=language)
    if comorbidity_note:
        recommendation = f"{recommendation} {comorbidity_note}".strip()

    return {
        "text": text_result,
        "audio": audio_result,
        "image": image_result,
        "passive": passive_result,
        "overall": overall,
        "comorbidity": comorbidity,
        "model_stats": model_stats,
        "recommendation": recommendation,
        "disclaimer": screening.get(
            "disclaimer",
            "This dashboard provides an early screening summary only. It does not replace diagnosis, emergency support, or clinician judgment.",
        ),
    }


def _extract_request_payload():
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        return {
            "profile": _normalize_profile(payload.get("profile")),
            "questionnaire": _normalize_questionnaire(payload.get("questionnaire")),
            "multimodal": payload.get("multimodal"),
            "text_input": _clean_text(payload.get("text_input"), MAX_TEXT_INPUT_LENGTH),
            "audio_metadata": payload.get("audio_metadata"),
            "image_metadata": payload.get("image_metadata"),
            "passive_metadata": payload.get("passive_metadata"),
            "typing_events": payload.get("typing_events"),
            "audio_path": None,
            "image_path": None,
            "passive_video_path": None,
        }

    profile = _normalize_profile(_parse_json_field(request.form.get("profile"), {}))
    questionnaire = _normalize_questionnaire(_parse_json_field(request.form.get("questionnaire"), {}))
    multimodal = _parse_json_field(request.form.get("multimodal"), None)
    text_input = _clean_text(request.form.get("text_input", ""), MAX_TEXT_INPUT_LENGTH)
    audio_path, audio_metadata = _save_uploaded_file(request.files.get("audio_file"), "_audio")
    image_path, image_metadata = _save_uploaded_file(request.files.get("image_file"), "_image")
    passive_video_path, passive_metadata = _save_uploaded_file(request.files.get("passive_video_file"), "_passive")
    return {
        "profile": profile,
        "questionnaire": questionnaire,
        "multimodal": multimodal,
        "text_input": text_input,
        "audio_metadata": audio_metadata,
        "image_metadata": image_metadata,
        "passive_metadata": passive_metadata,
        "typing_events": _parse_json_field(request.form.get("typing_events"), None),
        "audio_path": audio_path,
        "image_path": image_path,
        "passive_video_path": passive_video_path,
    }


def _extract_adaptive_request_payload():
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        responses = payload.get("responses")
        language = payload.get("language")
    else:
        responses = _parse_json_field(request.form.get("responses"), {})
        language = request.form.get("language")

    if not isinstance(responses, dict):
        return None

    normalized_responses = {}
    for question_id, value in responses.items():
        if value is None:
            continue
        try:
            normalized_responses[str(question_id)] = int(value)
        except (TypeError, ValueError):
            continue
    return {"responses": normalized_responses, "language": _normalize_language(language)}


@app.get("/")
def root():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/sw.js")
def service_worker():
    response = send_from_directory(app.static_folder, "sw.js")
    response.headers["Cache-Control"] = "no-cache"
    response.mimetype = "application/javascript"
    return response


@app.get("/manifest.webmanifest")
def manifest():
    response = send_from_directory(app.static_folder, "manifest.webmanifest")
    response.headers["Cache-Control"] = "no-cache"
    response.mimetype = "application/manifest+json"
    return response


@app.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "database": get_database_metadata(),
            "limits": {
                "max_upload_mb": round(app.config["MAX_CONTENT_LENGTH"] / (1024 * 1024), 2),
                "max_text_input_length": MAX_TEXT_INPUT_LENGTH,
                "max_list_limit": LIST_LIMIT_MAX,
            },
        }
    )


@app.get("/api/assessments")
def api_list_assessments():
    limit = request.args.get("limit", default=LIST_LIMIT_DEFAULT, type=int)
    limit = max(1, min(limit, LIST_LIMIT_MAX))
    return jsonify(list_assessment_records(limit=limit, audit_actor="dashboard_api", source_ip=request.remote_addr))


@app.post("/api/assessments")
def api_create_assessment():
    payload = _extract_request_payload()
    profile = payload["profile"]
    questionnaire = payload["questionnaire"]
    multimodal = payload["multimodal"]

    if not isinstance(profile, dict) or not isinstance(questionnaire, dict):
        _cleanup_temp_paths(payload["audio_path"], payload["image_path"], payload.get("passive_video_path"))
        return _json_error("Invalid payload. Expected profile and questionnaire objects.", 400)
    validation_error = _validate_assessment_payload(profile, questionnaire, require_consent=True)
    if validation_error:
        _cleanup_temp_paths(payload["audio_path"], payload["image_path"], payload.get("passive_video_path"))
        return _json_error(validation_error["message"], 400, validation_error)
    try:
        if not isinstance(multimodal, dict):
            multimodal = _build_dashboard_multimodal(
                text_input=payload["text_input"],
                questionnaire=questionnaire,
                language=profile.get("language", "English"),
                audio_path=payload["audio_path"],
                image_path=payload["image_path"],
                passive_video_path=payload.get("passive_video_path"),
                typing_events=payload.get("typing_events"),
                audio_metadata=payload["audio_metadata"],
                image_metadata=payload["image_metadata"],
                passive_metadata=payload["passive_metadata"],
            )

        record = create_assessment_record(
            profile=profile,
            questionnaire=questionnaire,
            multimodal=multimodal,
            actor="dashboard_api",
            source_ip=request.remote_addr,
        )
        record["trajectory"] = build_assessment_trajectory(
            record["assessment_id"],
            actor="dashboard_api",
            source_ip=request.remote_addr,
        )
        return jsonify(record), 201
    finally:
        _cleanup_temp_paths(payload["audio_path"], payload["image_path"], payload.get("passive_video_path"))


@app.post("/api/preview")
def api_preview_assessment():
    payload = _extract_request_payload()
    questionnaire = payload["questionnaire"] or {}
    profile = payload["profile"] or {}

    if not isinstance(questionnaire, dict):
        _cleanup_temp_paths(payload["audio_path"], payload["image_path"], payload.get("passive_video_path"))
        return _json_error("Invalid payload. Expected questionnaire object.", 400)
    validation_error = _validate_assessment_payload(profile, questionnaire, require_consent=False)
    if validation_error and validation_error.get("field") == "questionnaire":
        _cleanup_temp_paths(payload["audio_path"], payload["image_path"], payload.get("passive_video_path"))
        return _json_error(validation_error["message"], 400, validation_error)
    try:
        return jsonify(
            _build_dashboard_multimodal(
                text_input=payload["text_input"],
                questionnaire=questionnaire,
                language=profile.get("language", "English"),
                audio_path=payload["audio_path"],
                image_path=payload["image_path"],
                passive_video_path=payload.get("passive_video_path"),
                typing_events=payload.get("typing_events"),
                audio_metadata=payload["audio_metadata"],
                image_metadata=payload["image_metadata"],
                passive_metadata=payload["passive_metadata"],
            )
        )
    finally:
        _cleanup_temp_paths(payload["audio_path"], payload["image_path"], payload.get("passive_video_path"))


@app.get("/api/adaptive/config")
def api_adaptive_config():
    language = request.args.get("language")
    tuning = get_adaptive_tuning()
    response_options = [
        {"label": label, "value": value}
        for label, value in get_response_options(language).items()
    ]
    return jsonify(
        {
            "tuning": tuning,
            "response_options": response_options,
            "choose_one_label": get_adaptive_question_bank({}, language).get("choose_one_label", "Choose one"),
        }
    )


@app.post("/api/adaptive/next")
def api_adaptive_next_question():
    payload = _extract_adaptive_request_payload()
    if payload is None:
        return _json_error("Invalid payload. Expected responses object.", 400)
    return jsonify(get_adaptive_question_bank(payload["responses"], payload.get("language")))


@app.get("/api/assessments/<assessment_id>")
def api_fetch_assessment(assessment_id: str):
    record = fetch_assessment_record(assessment_id, actor="dashboard_api", source_ip=request.remote_addr)
    if record is None:
        return _json_error("Assessment not found.", 404)
    record["trajectory"] = build_assessment_trajectory(
        record["assessment_id"],
        actor="dashboard_api",
        source_ip=request.remote_addr,
    )
    return jsonify(record)


@app.delete("/api/assessments/<assessment_id>")
def api_delete_assessment(assessment_id: str):
    deleted = delete_assessment_record(assessment_id, actor="dashboard_api", source_ip=request.remote_addr)
    if not deleted:
        return _json_error("Assessment not found.", 404)
    return jsonify({"assessment_id": assessment_id.upper(), "deleted": True})


@app.get("/api/assessments/<assessment_id>/trajectory")
def api_assessment_trajectory(assessment_id: str):
    trajectory = build_assessment_trajectory(
        assessment_id,
        actor="dashboard_api",
        source_ip=request.remote_addr,
    )
    if trajectory is None:
        return _json_error("Assessment not found.", 404)
    return jsonify(trajectory)


@app.get("/api/assessments/<assessment_id>/report.pdf")
def api_assessment_pdf(assessment_id: str):
    record = fetch_assessment_record(assessment_id, actor="dashboard_pdf", source_ip=request.remote_addr)
    if record is None:
        return _json_error("Assessment not found.", 404)

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


@app.get("/api/database/audit-logs")
def api_database_audit_logs():
    limit = request.args.get("limit", default=100, type=int)
    return jsonify(list_audit_logs(limit=limit))


@app.get("/api/database/backups")
def api_database_backups():
    limit = request.args.get("limit", default=20, type=int)
    return jsonify(list_backup_runs(limit=limit))


@app.post("/api/database/backup")
def api_database_backup():
    payload = request.get_json(silent=True) or {}
    output_path = payload.get("output_path")
    backup = create_database_backup(
        output_path=output_path,
        actor="dashboard_api",
        source_ip=request.remote_addr,
        include_audit_logs=bool(payload.get("include_audit_logs", True)),
    )
    return jsonify(backup), 201


@app.get("/api/model-stats")
def api_model_stats():
    return jsonify(summarize_all_bundles())


@app.get("/api/sample")
def api_sample_dataset():
    sample_path = ROOT / "web" / "sample-results.json"
    if not sample_path.exists():
        return jsonify([])
    return Response(sample_path.read_text(encoding="utf-8"), mimetype="application/json")


@app.errorhandler(413)
def payload_too_large(_error):
    return _json_error("Uploaded media is too large for the dashboard server.", 413)


@app.errorhandler(500)
def internal_error(_error):
    if request.path.startswith("/api/"):
        return _json_error("The dashboard server hit an internal error while processing this request.", 500)
    return _error


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False)
