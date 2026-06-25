import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from datetime import datetime, timezone

from flask import Flask, Response, jsonify, request, send_from_directory

ROOT = Path(__file__).resolve().parent
SRC_PATH = str(ROOT / "src")
if SRC_PATH not in sys.path:
    sys.path.append(SRC_PATH)

from mental_health_screening import get_adaptive_question_bank, get_adaptive_tuning, get_response_options, get_validated_instrument, get_validated_instruments
from mental_health_screening.constants import PREDICTION_DOMAINS, PREDICTION_LABELS
from mental_health_screening.predict import screen
from mental_health_screening.report import create_assessment_pdf_bytes, create_quality_check_pdf_bytes
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
from mental_health_screening.utils import average, confidence_weighted_score, normalize_score, risk_level


app = Flask(__name__, static_folder=str(ROOT / "web"), static_url_path="/web")
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024
APP_BUILD = "2026-06-24"

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


def _validation_text(key: str, language: str = "English") -> str:
    language = _normalize_language(language)
    messages = {
        "English": {
            "full_name_required": "Candidate full name is required.",
            "village_required": "Village or local area is required.",
            "assessor_required": "Assessor name is required.",
            "consent_required": "Consent is required before saving an assessment.",
            "questionnaire_incomplete": "Questionnaire scores are incomplete.",
        },
        "Hindi": {
            "full_name_required": "उम्मीदवार का पूरा नाम आवश्यक है।",
            "village_required": "गाँव या स्थानीय क्षेत्र आवश्यक है।",
            "assessor_required": "आकलनकर्ता का नाम आवश्यक है।",
            "consent_required": "आकलन सहेजने से पहले सहमति आवश्यक है।",
            "questionnaire_incomplete": "प्रश्नावली स्कोर अधूरे हैं।",
        },
        "Bengali": {
            "full_name_required": "প্রার্থীর পূর্ণ নাম প্রয়োজন।",
            "village_required": "গ্রাম বা স্থানীয় এলাকা প্রয়োজন।",
            "assessor_required": "মূল্যায়নকারীর নাম প্রয়োজন।",
            "consent_required": "মূল্যায়ন সংরক্ষণের আগে সম্মতি প্রয়োজন।",
            "questionnaire_incomplete": "প্রশ্নমালার স্কোর অসম্পূর্ণ।",
        },
    }
    return messages.get(language, messages["English"]).get(key, key)


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
    validated_instrument = questionnaire.get("validated_instrument")
    if isinstance(validated_instrument, dict):
        validated_instrument = {
            "id": _clean_text(validated_instrument.get("id"), 32),
            "label": _clean_text(validated_instrument.get("label"), 120),
            "language": _clean_text(validated_instrument.get("language"), 40),
            "description": _clean_text(validated_instrument.get("description"), 250),
            "localized_label": _clean_text(validated_instrument.get("localized_label"), 120),
            "localized_description": _clean_text(validated_instrument.get("localized_description"), 250),
        }
    else:
        validated_instrument = None
    safe_questionnaire = {
        "available": bool(questionnaire.get("available", True)),
        "notes": _clean_text(questionnaire.get("notes"), 500),
        "validated_instrument": validated_instrument,
    }
    for domain in PREDICTION_DOMAINS:
        safe_questionnaire[f"{domain}_score"] = normalize_score(questionnaire.get(f"{domain}_score", 0.0))
        safe_questionnaire[f"{domain}_risk"] = risk_level(safe_questionnaire[f"{domain}_score"])
    safe_questionnaire["overall_score"] = normalize_score(
        average([safe_questionnaire[f"{domain}_score"] for domain in PREDICTION_DOMAINS])
    )
    return safe_questionnaire


def _default_validated_instrument(language: str | None) -> dict | None:
    instrument = get_validated_instrument(language)
    if not isinstance(instrument, dict):
        return None
    return {
        "id": _clean_text(instrument.get("id"), 32),
        "label": _clean_text(instrument.get("label"), 120),
        "language": _clean_text(instrument.get("language"), 40),
        "description": _clean_text(instrument.get("description"), 250),
        "localized_label": _clean_text(instrument.get("localized_label"), 120),
        "localized_description": _clean_text(instrument.get("localized_description"), 250),
    }


def _validate_assessment_payload(profile: dict, questionnaire: dict, require_consent: bool = True, language: str = "English") -> dict | None:
    if not profile.get("full_name"):
        return {"field": "full_name", "message": _validation_text("full_name_required", language)}
    if not profile.get("village"):
        return {"field": "village", "message": _validation_text("village_required", language)}
    if not profile.get("assessor"):
        return {"field": "assessor", "message": _validation_text("assessor_required", language)}
    if require_consent and not profile.get("consent_received"):
        return {"field": "consent_received", "message": _validation_text("consent_required", language)}
    missing_scores = [
        domain for domain in PREDICTION_DOMAINS
        if f"{domain}_score" not in questionnaire
    ]
    if missing_scores:
        return {"field": "questionnaire", "message": _validation_text("questionnaire_incomplete", language), "missing_domains": missing_scores}
    return None


def _modality_failure_note(modality: str, reason: str | None, result: dict | None = None, language: str = "English") -> str:
    language = _normalize_language(language)
    text_map = {
        "English": {
            "audio_too_short": "Audio upload was received, but it was too short for analysis ({duration}s). Minimum required duration is {minimum}s.",
            "librosa_not_installed": "Audio upload was received, but backend audio dependencies are not installed on this machine.",
            "audio_invalid_duration": "Audio upload was received, but the clip duration could not be validated for analysis.",
            "no_face_detected": "Image upload was received, but no detectable face was found, so facial-cue analysis was skipped.",
            "vision_dependencies_not_installed": "Image upload was received, but backend vision dependencies are not installed on this machine.",
            "image_unreadable": "Image upload was received, but the backend could not read it as a usable image.",
            "passive_signals_missing": "Passive biomarkers were not provided, so zero-hardware analysis from camera or typing rhythm was skipped.",
            "video_missing": "The phone-camera video signal was not provided, so rPPG-style analysis was skipped.",
            "passive_vision_missing": "The phone-camera video was received, but backend vision dependencies are not installed on this machine.",
            "fallback": "Dashboard captured {modality} upload metadata for {file_name}. The file reached the backend, but no usable {modality} inference result was produced from it.",
        },
        "Hindi": {
            "audio_too_short": "ऑडियो अपलोड मिला, लेकिन वह विश्लेषण के लिए बहुत छोटा था ({duration}s)। आवश्यक न्यूनतम अवधि {minimum}s है।",
            "librosa_not_installed": "ऑडियो अपलोड मिला, लेकिन इस मशीन पर बैकएंड ऑडियो निर्भरताएँ स्थापित नहीं हैं।",
            "audio_invalid_duration": "ऑडियो अपलोड मिला, लेकिन विश्लेषण के लिए क्लिप अवधि की पुष्टि नहीं हो सकी।",
            "no_face_detected": "इमेज अपलोड मिली, लेकिन कोई पहचानने योग्य चेहरा नहीं मिला, इसलिए चेहरे के संकेत विश्लेषण को छोड़ दिया गया।",
            "vision_dependencies_not_installed": "इमेज अपलोड मिली, लेकिन इस मशीन पर बैकएंड विज़न निर्भरताएँ स्थापित नहीं हैं।",
            "image_unreadable": "इमेज अपलोड मिली, लेकिन बैकएंड उसे उपयोग योग्य छवि के रूप में नहीं पढ़ सका।",
            "passive_signals_missing": "निष्क्रिय संकेत उपलब्ध नहीं थे, इसलिए कैमरा या टाइपिंग रिद्म से शून्य-हार्डवेयर विश्लेषण छोड़ दिया गया।",
            "video_missing": "फोन-कैमरा वीडियो संकेत उपलब्ध नहीं था, इसलिए rPPG-शैली विश्लेषण छोड़ दिया गया।",
            "passive_vision_missing": "फोन-कैमरा वीडियो प्राप्त हुआ, लेकिन इस मशीन पर बैकएंड विज़न निर्भरताएँ स्थापित नहीं हैं।",
            "fallback": "डैशबोर्ड ने {file_name} के लिए {modality} अपलोड मेटाडेटा प्राप्त किया। फ़ाइल बैकएंड तक पहुँची, लेकिन उससे कोई उपयोगी {modality} निष्कर्ष नहीं मिला।",
        },
        "Bengali": {
            "audio_too_short": "অডিও আপলোড পাওয়া গেছে, কিন্তু বিশ্লেষণের জন্য সেটি খুব ছোট ({duration}s)। ন্যূনতম প্রয়োজনীয় দৈর্ঘ্য {minimum}s।",
            "librosa_not_installed": "অডিও আপলোড পাওয়া গেছে, কিন্তু এই মেশিনে ব্যাকএন্ড অডিও নির্ভরতা ইনস্টল করা নেই।",
            "audio_invalid_duration": "অডিও আপলোড পাওয়া গেছে, কিন্তু বিশ্লেষণের জন্য ক্লিপের দৈর্ঘ্য যাচাই করা যায়নি।",
            "no_face_detected": "ইমেজ আপলোড পাওয়া গেছে, কিন্তু কোনো শনাক্তযোগ্য মুখ পাওয়া যায়নি, তাই মুখ-সংকেত বিশ্লেষণ এড়িয়ে যাওয়া হয়েছে।",
            "vision_dependencies_not_installed": "ইমেজ আপলোড পাওয়া গেছে, কিন্তু এই মেশিনে ব্যাকএন্ড ভিশন নির্ভরতা ইনস্টল করা নেই।",
            "image_unreadable": "ইমেজ আপলোড পাওয়া গেছে, কিন্তু ব্যাকএন্ড সেটি ব্যবহারযোগ্য ছবি হিসেবে পড়তে পারেনি।",
            "passive_signals_missing": "প্যাসিভ বায়োমার্কার দেওয়া হয়নি, তাই ক্যামেরা বা টাইপিং রিদম থেকে হার্ডওয়্যারবিহীন বিশ্লেষণ এড়িয়ে যাওয়া হয়েছে।",
            "video_missing": "ফোন-ক্যামেরার ভিডিও সংকেত দেওয়া হয়নি, তাই rPPG-ধরনের বিশ্লেষণ এড়িয়ে যাওয়া হয়েছে।",
            "passive_vision_missing": "ফোন-ক্যামেরার ভিডিও পাওয়া গেছে, কিন্তু এই মেশিনে ব্যাকএন্ড ভিশন নির্ভরতা ইনস্টল করা নেই।",
            "fallback": "ড্যাশবোর্ড {file_name}-এর জন্য {modality} আপলোড মেটাডেটা পেয়েছে। ফাইলটি ব্যাকএন্ডে পৌঁছেছে, কিন্তু কোনো ব্যবহারযোগ্য {modality} ফলাফল তৈরি হয়নি।",
        },
    }.get(language, {})
    if modality == "audio" and reason == "audio_too_short":
        duration = round(float((result or {}).get("duration", 0.0)), 2)
        minimum = round(float((result or {}).get("minimum_duration", 2.5)), 2)
        return text_map["audio_too_short"].format(duration=duration, minimum=minimum)
    if modality == "audio" and reason == "librosa_not_installed":
        return text_map["librosa_not_installed"]
    if modality == "audio" and reason == "audio_invalid_duration":
        return text_map["audio_invalid_duration"]
    if modality == "image" and reason == "no_face_detected":
        return text_map["no_face_detected"]
    if modality == "image" and reason == "vision_dependencies_not_installed":
        return text_map["vision_dependencies_not_installed"]
    if modality == "image" and reason == "image_unreadable":
        return text_map["image_unreadable"]
    if modality == "passive_biomarkers" and reason == "passive_signals_missing":
        return text_map["passive_signals_missing"]
    if modality == "passive_biomarkers" and reason == "video_missing":
        return text_map["video_missing"]
    if modality == "passive_biomarkers" and reason == "vision_dependencies_not_installed":
        return text_map["passive_vision_missing"]
    return text_map["fallback"].format(
        modality=modality,
        file_name=(result or {}).get("features", {}).get("file_name", "the uploaded file"),
    )


def _metadata_modality(modality: str, metadata: dict | None, reason: str | None = None, source_result: dict | None = None, language: str = "English") -> dict:
    if not isinstance(metadata, dict) or not metadata:
        return {"available": False}

    payload = {
        "available": False,
        "modality": modality,
        "confidence": 0.2,
        "notes": _modality_failure_note(modality, reason, source_result, language=language),
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


def _parse_raw_json_body(default=None):
    raw_body = request.get_data(cache=True, as_text=True) or ""
    text = raw_body.strip()
    if not text or text[0] not in "{[":
        return default
    try:
        return json.loads(text)
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


def _decorate_modality_result(result: dict, metadata: dict | None, modality: str, language: str = "English") -> dict:
    if result.get("available"):
        features = dict(result.get("features") or {})
        if metadata:
            features.update(metadata)
        return {
            **result,
            "modality": modality,
            "features": features,
        }
    return _metadata_modality(modality, metadata, reason=result.get("reason"), source_result=result, language=language)


def _run_quality_check_report(records: list[dict], mismatches: int = 10) -> dict:
    tool_path = ROOT / "tools" / "run_quality_check.py"
    if not tool_path.exists():
        raise FileNotFoundError(f"Quality check tool not found: {tool_path}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        input_path = temp_dir_path / "quality_input.json"
        output_path = temp_dir_path / "quality_report.json"
        input_path.write_text(json.dumps(records, indent=2), encoding="utf-8")

        command = [
            sys.executable,
            str(tool_path),
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--mismatches",
            str(max(0, int(mismatches))),
        ]
        completed = subprocess.run(command, cwd=str(ROOT), capture_output=True, text=True)
        if completed.returncode not in (0, 1):
            raise RuntimeError(
                "Quality check tool failed: "
                f"{completed.stderr.strip() or completed.stdout.strip() or 'unknown error'}"
            )
        if not output_path.exists():
            raise RuntimeError("Quality check tool did not produce a report.")

        report = json.loads(output_path.read_text(encoding="utf-8"))
        report["generated_at"] = datetime.now(timezone.utc).isoformat()
        report["tool_stdout"] = completed.stdout.strip()
        report["tool_stderr"] = completed.stderr.strip()
        report["source"] = "live_database"
        return report


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


def _blend_questionnaire_with_screening(questionnaire_score: float, screening_score: float, screening_confidence: float) -> float:
    questionnaire_score = normalize_score(questionnaire_score)
    screening_score = normalize_score(screening_score)
    screening_confidence = normalize_score(screening_confidence)
    # Keep the questionnaire as the stronger prior, but let strong multimodal evidence nudge the score.
    evidence_weight = 0.12 + (0.18 * screening_confidence)
    evidence_weight = max(0.12, min(evidence_weight, 0.30))
    questionnaire_weight = 1.0 - evidence_weight
    return normalize_score((questionnaire_score * questionnaire_weight) + (screening_score * evidence_weight))


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


def _comorbidity_note_basic(comorbidity: dict | None, language: str = "english") -> str:
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
    audio_result = _decorate_modality_result(screening.get("audio") or {"available": False}, audio_metadata, "audio", language=language)
    image_result = _decorate_modality_result(screening.get("image") or {"available": False}, image_metadata, "image", language=language)
    passive_result = _decorate_modality_result(
        screening.get("passive") or {"available": False},
        passive_metadata,
        "passive_biomarkers",
        language=language,
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
            for modality in (text_result, audio_result, image_result, passive_result)
        )
        if has_screening_signal:
            screening_confidence = normalize_score(screening_overall.get("confidence", 0.0))
            weighted_screening = confidence_weighted_score(
                screening_score,
                screening_confidence,
                neutral=questionnaire_score,
                minimum_weight=0.35,
            )
            combined_score = _blend_questionnaire_with_screening(questionnaire_score, weighted_screening, screening_confidence)
        else:
            combined_score = questionnaire_score
        overall_scores[domain] = combined_score
        overall_levels[domain] = risk_level(combined_score)

    overall_confidence = _dashboard_confidence(
        questionnaire=questionnaire,
        screening_overall=screening_overall,
        modalities=[text_result, audio_result, image_result, passive_result],
    )
    overall = {
        **overall_levels,
        "confidence": normalize_score(overall_confidence),
        "evidence_strength": normalize_score(overall_confidence),
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
            {
                "English": "This dashboard provides an early screening summary only. It does not replace diagnosis, emergency support, or clinician judgment.",
                "Hindi": "यह डैशबोर्ड केवल प्रारंभिक स्क्रीनिंग सारांश प्रदान करता है। यह निदान, आपातकालीन सहायता, या चिकित्सकीय निर्णय का स्थान नहीं लेता।",
                "Bengali": "এই ড্যাশবোর্ডটি শুধুমাত্র প্রাথমিক স্ক্রিনিং সারাংশ দেয়। এটি নির্ণয়, জরুরি সহায়তা বা চিকিৎসকের বিচারের বিকল্প নয়।",
            }.get(_normalize_language(language), "This dashboard provides an early screening summary only. It does not replace diagnosis, emergency support, or clinician judgment."),
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

    payload = _parse_raw_json_body()
    if isinstance(payload, dict):
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
        payload = _parse_raw_json_body({})
        if isinstance(payload, dict):
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
    response = send_from_directory(app.static_folder, "index.html")
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["X-App-Build"] = APP_BUILD
    return response


@app.get("/version")
def version():
    return jsonify(
        {
            "build": APP_BUILD,
            "service": "learning-disorder-intelligence",
        }
    )


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


@app.after_request
def add_response_headers(response):
    if request.path == "/" or request.path.startswith("/api/") or request.path in {"/version", "/health", "/healthz"}:
        response.headers.setdefault("Cache-Control", "no-store, max-age=0")
        response.headers["X-App-Build"] = APP_BUILD
    return response


@app.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "build": APP_BUILD,
            "database": get_database_metadata(),
            "limits": {
                "max_upload_mb": round(app.config["MAX_CONTENT_LENGTH"] / (1024 * 1024), 2),
                "max_text_input_length": MAX_TEXT_INPUT_LENGTH,
                "max_list_limit": LIST_LIMIT_MAX,
            },
        }
    )


@app.get("/healthz")
def healthz():
    return health()


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
    if not questionnaire.get("validated_instrument"):
        questionnaire["validated_instrument"] = _default_validated_instrument(profile.get("language"))

    if not isinstance(profile, dict) or not isinstance(questionnaire, dict):
        _cleanup_temp_paths(payload["audio_path"], payload["image_path"], payload.get("passive_video_path"))
        return _json_error("Invalid payload. Expected profile and questionnaire objects.", 400)
    validation_error = _validate_assessment_payload(profile, questionnaire, require_consent=True, language=profile.get("language", "English"))
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
    if not questionnaire.get("validated_instrument"):
        questionnaire["validated_instrument"] = _default_validated_instrument(profile.get("language"))

    if not isinstance(questionnaire, dict):
        _cleanup_temp_paths(payload["audio_path"], payload["image_path"], payload.get("passive_video_path"))
        return _json_error("Invalid payload. Expected questionnaire object.", 400)
    validation_error = _validate_assessment_payload(profile, questionnaire, require_consent=False, language=profile.get("language", "English"))
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


@app.get("/api/validated-instruments")
def api_validated_instruments():
    language = request.args.get("language")
    return jsonify({"instruments": get_validated_instruments(language)})


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
    if str(record.get("assessment_id") or "").upper().startswith("MHS-DEMO") or str(record.get("record_origin") or record.get("profile", {}).get("record_origin") or "").lower() == "demo":
        return _json_error("Demo records are excluded from assessment reports.", 403)

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


@app.get("/api/quality-check")
def api_quality_check():
    try:
        records = list_assessment_records(limit=None, audit_actor="dashboard_quality_check", source_ip=request.remote_addr)
        report = _run_quality_check_report(records, mismatches=request.args.get("mismatches", 10))
        return jsonify(report)
    except Exception as exc:
        return _json_error("Quality check could not be completed.", 500, {"error": str(exc)})


@app.get("/api/quality-check/report.pdf")
def api_quality_check_pdf():
    try:
        language = request.args.get("language", "english")
        records = list_assessment_records(limit=None, audit_actor="dashboard_quality_check_pdf", source_ip=request.remote_addr)
        report = _run_quality_check_report(records, mismatches=request.args.get("mismatches", 10))
        pdf_bytes = create_quality_check_pdf_bytes(report, language=language)
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="quality_check_report.pdf"',
            },
        )
    except Exception as exc:
        return _json_error("Quality check PDF could not be generated.", 500, {"error": str(exc)})


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
    port = int(os.environ.get("PORT", "8000"))
    simulate_save_flag = ROOT / "tools" / "simulate_save.flag"
    if os.environ.get("SIMULATE_SAVE") == "1" or simulate_save_flag.exists():
        app.config["TESTING"] = True
        app.config["PROPAGATE_EXCEPTIONS"] = True
        payload = {
            "profile": {
                "full_name": "Demo User",
                "age": 34,
                "gender": "Female",
                "village": "Demo Village",
                "phone": "1234567890",
                "assessor": "CHW",
                "language": "English",
                "consent_received": True,
                "record_origin": "test",
            },
            "questionnaire": {
                "available": True,
                "notes": "",
                "depression_score": 1,
                "anxiety_score": 1,
                "stress_score": 1,
                "sleep_disorder_score": 1,
                "burnout_score": 1,
                "loneliness_score": 1,
                "substance_abuse_score": 1,
            },
            "text_input": "Feeling okay",
        }
        with app.test_client() as client:
            response = client.post("/api/assessments", json=payload)
            print(response.status_code)
            print(response.get_data(as_text=True))
        try:
            simulate_save_flag.unlink()
        except OSError:
            pass
        raise SystemExit(0)
    app.run(host="0.0.0.0", port=port, debug=False)
