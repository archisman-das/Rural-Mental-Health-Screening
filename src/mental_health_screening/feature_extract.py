import os
import tempfile
from functools import lru_cache
import numpy as np

from .utils import normalize_score
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except ImportError:
    SentimentIntensityAnalyzer = None

try:
    import torch
except ImportError:
    torch = None

try:
    from transformers import AutoModel, AutoTokenizer, pipeline
except ImportError:
    AutoModel = None
    AutoTokenizer = None
    pipeline = None

try:
    import librosa
except ImportError:
    librosa = None

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import mediapipe as mp
except ImportError:
    mp = None

analyzer = SentimentIntensityAnalyzer() if SentimentIntensityAnalyzer is not None else None

LANGUAGE_TEXT_RULES = {
    "english": {
        "negative_words": {
            "sad", "hopeless", "worried", "anxious", "tired", "nervous", "stressed",
            "lonely", "empty", "afraid", "panic", "overwhelmed", "helpless", "worthless",
        },
        "positive_words": {"better", "hopeful", "calm", "good", "safe", "supported", "strong", "improving"},
        "distress_phrases": {
            "i cannot take this anymore",
            "i can't take this anymore",
            "my chest feels heavy",
            "i feel worn out inside",
            "i feel like i am falling apart",
            "nothing feels right anymore",
            "i am barely holding on",
            "i am not myself lately",
        },
        "distress_phrases": {
            "à¤…à¤¬ à¤”à¤° à¤¸à¤¹à¤¨ à¤¨à¤¹à¥€à¤‚ à¤¹à¥‹ à¤°à¤¹à¤¾",
            "à¤®à¤¨ à¤¬à¤¹à¥à¤¤ à¤­à¤¾à¤°à¥€ à¤¹à¥ˆ",
            "à¤¦à¤¿à¤² à¤­à¤¾à¤°à¥€ à¤²à¤— à¤°à¤¹à¤¾ à¤¹à¥ˆ",
            "à¤¸à¤¬ à¤•à¥à¤› à¤¬à¤¿à¤–à¤° à¤¸à¤¾ à¤°à¤¹à¤¾ à¤¹à¥ˆ",
            "à¤®à¥ˆà¤‚ à¤Ÿà¥‚à¤Ÿ à¤—à¤¯à¤¾ à¤¹à¥‚à¤",
            "à¤®à¥ˆà¤‚ à¤Ÿà¥‚à¤Ÿ à¤—à¤ˆ à¤¹à¥‚à¤",
            "à¤…à¤¬ à¤•à¥à¤› à¤­à¥€ à¤…à¤šà¥à¤›à¤¾ à¤¨à¤¹à¥€à¤‚ à¤²à¤— à¤°à¤¹à¤¾",
            "à¤®à¥ˆà¤‚ à¤–à¥à¤¦ à¤•à¥‹ à¤ªà¤¹à¤²à¥‡ à¤œà¥ˆà¤¸à¤¾ à¤¨à¤¹à¥€à¤‚ à¤®à¤¹à¤¸à¥‚à¤¸ à¤•à¤° à¤°à¤¹à¤¾ à¤¹à¥‚à¤",
            "à¤®à¥ˆà¤‚ à¤–à¥à¤¦ à¤•à¥‹ à¤ªà¤¹à¤²à¥‡ à¤œà¥ˆà¤¸à¥€ à¤¨à¤¹à¥€à¤‚ à¤®à¤¹à¤¸à¥‚à¤¸ à¤•à¤° à¤°à¤¹à¥€ à¤¹à¥‚à¤",
        },
        "self_harm_keywords": {
            "kill myself", "end my life", "don't want to live", "do not want to live", "suicide",
            "self harm", "harm myself", "hurt myself", "want to die", "better off dead", "no reason to live",
        },
        "emotion_keywords": {
            "sadness": {"sad", "empty", "hopeless", "crying", "down", "unhappy"},
            "fear": {"afraid", "fear", "panic", "scared", "terrified", "nervous"},
            "anger": {"angry", "irritated", "frustrated", "annoyed", "furious"},
            "joy": {"happy", "relieved", "calm", "good", "hopeful", "better"},
            "loneliness": {"alone", "isolated", "lonely", "disconnected", "abandoned"},
            "exhaustion": {"tired", "drained", "burned", "burnout", "exhausted", "sleepy"},
        },
    },
    "hindi": {
        "negative_words": {
            "उदास", "निराश", "चिंतित", "बेचैन", "थका", "थकी", "घबराहट", "तनाव", "अकेला", "अकेली",
            "डर", "खाली", "बेबस", "बेकार", "परेशान",
        },
        "positive_words": {"बेहतर", "उम्मीद", "शांत", "अच्छा", "सुरक्षित", "समर्थन", "मजबूत", "सुधार"},
        "distress_phrases": {
            "à¦†à¦° à¦¸à¦¹à§à¦¯ à¦•à¦°à¦¤à§‡ à¦ªà¦¾à¦°à¦›à¦¿ à¦¨à¦¾",
            "à¦®à¦¨à§‡ à¦–à§à¦¬ à¦­à¦¾à¦°à§€ à¦²à¦¾à¦—à¦›à§‡",
            "à¦¬à¦•à§à¦¸à¦Ÿà¦¾ à¦­à¦¾à¦°à§€ à¦²à¦¾à¦—à¦›à§‡",
            "à¦¸à¦¬à¦•à¦¿à¦›à§ à¦­à§‡à¦à§‡ à¦ªà¦¡à¦¼à¦›à§‡ à¦®à¦¨à§‡ à¦¹à¦›à§‡",
            "à¦†à¦®à¦¿ à¦†à¦° à¦†à¦—à§‡à¦° à¦®à¦¤à§‹ à¦¨à¦‡",
            "à¦®à¦¨à¦Ÿà¦¾ à¦à¦•à¦¬à¦¾à¦°à§‡ à¦­à¦¾à¦² à¦¨à¦¯à¦¼",
            "à¦à¦–à¦¨ à¦•à¦¿à¦›à§à¦‡ à¦†à¦° à¦ à¦¿à¦• à¦²à¦¾à¦—à¦›à§‡ à¦¨à¦¾",
            "à¦†à¦®à¦¿ à¦–à§à¦¬à¦‡ à¦­à§‡à¦à§‡ à¦ªà¦¡à¦¼à§‡à¦›à¦¿",
        },
        "self_harm_keywords": {
            "मर जाना चाहता", "मर जाना चाहती", "जीने का मन नहीं", "जीना नहीं चाहता", "जीना नहीं चाहती",
            "आत्महत्या", "खुद को नुकसान", "खुद को मार", "मरना चाहता", "मरना चाहती",
        },
        "emotion_keywords": {
            "sadness": {"उदास", "निराश", "रोना", "दुखी", "टूटा"},
            "fear": {"डर", "घबराहट", "चिंता", "बेचैन", "भय"},
            "anger": {"गुस्सा", "चिड़चिड़ा", "नाराज", "हताश"},
            "joy": {"खुश", "शांत", "बेहतर", "अच्छा", "उम्मीद"},
            "loneliness": {"अकेला", "अकेली", "अलग", "कटा", "तन्हा"},
            "exhaustion": {"थका", "थकी", "टूटा", "जला", "नींद"},
        },
    },
    "bengali": {
        "negative_words": {
            "দুঃখিত", "উদাস", "নিরাশ", "চিন্তিত", "উদ্বিগ্ন", "ক্লান্ত", "ভয়", "স্ট্রেস", "একাকী",
            "ফাঁকা", "অসহায়", "পanik", "ব্যর্থ", "অস্থির",
        },
        "positive_words": {"ভাল", "শান্ত", "নিরাপদ", "সমর্থন", "আশা", "উন্নতি", "ভালো", "শক্ত"},
        "self_harm_keywords": {
            "মরে যেতে চাই", "বাঁচতে চাই না", "আত্মহত্যা", "নিজেকে আঘাত", "নিজেকে মেরে ফেলতে চাই",
            "জীবন শেষ করতে চাই", "মরে যাওয়া ভালো",
        },
        "emotion_keywords": {
            "sadness": {"দুঃখিত", "উদাস", "নিরাশ", "কাঁদছি", "মন খারাপ"},
            "fear": {"ভয়", "চিন্তা", "উদ্বিগ্ন", "আতঙ্ক", "অস্থির"},
            "anger": {"রাগ", "বিরক্ত", "হতাশ", "ক্ষুব্ধ"},
            "joy": {"খুশি", "শান্ত", "ভালো", "আশা", "উন্নতি"},
            "loneliness": {"একাকী", "একলা", "বিচ্ছিন্ন", "তনহা"},
            "exhaustion": {"ক্লান্ত", "অবসাদ", "ঘুম", "শক্তিহীন"},
        },
    },
}

AGRARIAN_DISTRESS_PHRASES = {
    "english": {
        "crop_failure_phrases": {
            "crop failed",
            "crop failure",
            "lost the crop",
            "bad harvest",
            "harvest failed",
            "crop loss",
        },
        "debt_phrases": {
            "in debt",
            "loan burden",
            "cannot repay",
            "debt pressure",
            "moneylender",
            "loan due",
        },
        "food_security_phrases": {
            "food insecurity",
            "no food",
            "running out of food",
            "skip meals",
            "not enough food",
            "hunger at home",
        },
    },
    "hindi": {
        "crop_failure_phrases": {
            "फसल खराब",
            "फसल नष्ट",
            "फसल बर्बाद",
            "फसल चौपट",
            "फसल डूब गई",
        },
        "debt_phrases": {
            "कर्ज",
            "ऋण",
            "उधार",
            "कर्ज का बोझ",
            "कर्ज चुकाना",
        },
        "food_security_phrases": {
            "भोजन नहीं",
            "खाना नहीं",
            "अन्न नहीं",
            "भूखा",
            "राशन नहीं",
        },
    },
    "bengali": {
        "crop_failure_phrases": {
            "ফসল নষ্ট",
            "ফসলের ক্ষতি",
            "ফসল হারিয়েছি",
            "ফসল উঠে যায়নি",
            "ফসল নষ্ট হয়ে গেছে",
        },
        "debt_phrases": {
            "ঋণ",
            "কর্জ",
            "ধার",
            "ঋণের বোঝা",
            "কর্জ শোধ",
        },
        "food_security_phrases": {
            "খাবার নেই",
            "খাদ্য নেই",
            "খেতে পারছি না",
            "খিদে",
            "অন্ন নেই",
        },
    },
}

LANGUAGE_NATIVE_TRANSFORMER_CANDIDATES = {
    "english": (
        "distilbert-base-uncased",
        "bert-base-uncased",
    ),
    "hindi": (
        "google/muril-base-cased",
        "ai4bharat/IndicBERTv2-MLM-only",
    ),
    "bengali": (
        "ai4bharat/IndicBERTv2-MLM-only",
        "google/muril-base-cased",
    ),
}

LANGUAGE_NATIVE_TRANSFORMER_FAMILIES = {
    "english": "english-bert",
    "hindi": "indic-muril",
    "bengali": "indic-bert",
}

SENTIMENT_MODEL_CANDIDATES = (
    "distilbert-base-uncased-finetuned-sst-2-english",
    "textattack/bert-base-uncased-imdb",
)

EMOTION_MODEL_CANDIDATES = (
    "bhadresh-savani/distilbert-base-uncased-emotion",
    "nateraw/bert-base-uncased-emotion",
)

AUDIO_MIN_DURATION_SECONDS = 2.5
RPPG_MIN_SAMPLE_COUNT = 24
RPPG_MIN_BPM = 45.0
RPPG_MAX_BPM = 180.0


def _safe_float(value) -> float | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _face_crop_from_frame(frame) -> tuple[np.ndarray | None, str]:
    if cv2 is None or frame is None:
        return None, "vision_unavailable"

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cascade_path = getattr(cv2.data, "haarcascades", "") + "haarcascade_frontalface_default.xml"
    if cascade_path and os.path.exists(cascade_path):
        detector = cv2.CascadeClassifier(cascade_path)
        faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
        if faces is not None and len(faces) > 0:
            x, y, w, h = max(faces, key=lambda box: box[2] * box[3])
            crop = frame[y : y + h, x : x + w]
            if crop.size:
                return crop, "haar_face"

    height, width = frame.shape[:2]
    if height <= 0 or width <= 0:
        return None, "invalid_frame"
    top = int(height * 0.18)
    bottom = int(height * 0.82)
    left = int(width * 0.2)
    right = int(width * 0.8)
    crop = frame[top:bottom, left:right]
    if crop.size:
        return crop, "center_crop"
    return None, "no_face_detected"


def _estimate_heart_rate_from_signal(signal_values: list[float], fps: float) -> tuple[float | None, dict]:
    if len(signal_values) < RPPG_MIN_SAMPLE_COUNT or fps <= 0:
        return None, {"quality": 0.0, "reason": "insufficient_samples"}

    samples = np.asarray(signal_values, dtype=float)
    samples = samples - np.mean(samples)
    std = float(np.std(samples))
    if std <= 1e-8:
        return None, {"quality": 0.0, "reason": "flat_signal"}

    window = np.hanning(len(samples))
    spectrum = np.abs(np.fft.rfft(samples * window))
    frequencies = np.fft.rfftfreq(len(samples), d=1.0 / fps)
    valid = (frequencies >= (RPPG_MIN_BPM / 60.0)) & (frequencies <= (RPPG_MAX_BPM / 60.0))
    if not np.any(valid):
        return None, {"quality": 0.0, "reason": "no_valid_band"}

    valid_frequencies = frequencies[valid]
    valid_spectrum = spectrum[valid]
    peak_index = int(np.argmax(valid_spectrum))
    peak_frequency = float(valid_frequencies[peak_index])
    peak_power = float(valid_spectrum[peak_index])
    total_power = float(np.sum(valid_spectrum)) or 1.0
    quality = normalize_score(peak_power / total_power)
    bpm = peak_frequency * 60.0
    return bpm, {
        "quality": round(quality, 6),
        "peak_frequency_hz": round(peak_frequency, 6),
        "signal_std": round(std, 6),
        "sample_count": int(len(samples)),
        "reason": None,
    }


def _typing_trace_features(typing_events) -> dict:
    if not typing_events:
        return {
            "available": False,
            "reason": "typing_events_missing",
        }

    if isinstance(typing_events, dict):
        if isinstance(typing_events.get("events"), list):
            typing_events = typing_events["events"]
        elif isinstance(typing_events.get("intervals_ms"), list):
            typing_events = [{"interval_ms": value} for value in typing_events["intervals_ms"]]
        else:
            typing_events = [typing_events]

    intervals_ms: list[float] = []
    timestamps_ms: list[float] = []
    total_events = 0
    backspace_events = 0
    printable_events = 0

    for event in typing_events:
        total_events += 1
        if isinstance(event, (int, float)):
            interval_value = _safe_float(event)
            if interval_value is not None and interval_value >= 0:
                intervals_ms.append(interval_value)
            continue
        if not isinstance(event, dict):
            continue

        interval_value = _safe_float(event.get("interval_ms"))
        if interval_value is not None and interval_value >= 0:
            intervals_ms.append(interval_value)

        timestamp_value = _safe_float(event.get("timestamp_ms"))
        if timestamp_value is None:
            timestamp_value = _safe_float(event.get("timestamp"))
        if timestamp_value is None:
            timestamp_value = _safe_float(event.get("t"))
        if timestamp_value is not None:
            timestamps_ms.append(timestamp_value)

        key_value = str(event.get("key") or event.get("code") or event.get("input") or "").strip().lower()
        if key_value in {"backspace", "delete", "del"}:
            backspace_events += 1
        if len(key_value) == 1 or event.get("character") is not None:
            printable_events += 1

    timestamps_ms.sort()
    if len(timestamps_ms) >= 2:
        intervals_ms.extend(float(delta) for delta in np.diff(np.asarray(timestamps_ms, dtype=float)))

    intervals_ms = [interval for interval in intervals_ms if interval >= 0]
    if not intervals_ms:
        return {
            "available": False,
            "reason": "typing_intervals_missing",
            "event_count": int(total_events),
        }

    interval_array = np.asarray(intervals_ms, dtype=float)
    mean_interval = float(np.mean(interval_array))
    std_interval = float(np.std(interval_array))
    pause_ratio = float(np.mean(interval_array >= 750.0))
    burstiness = float(std_interval / max(mean_interval, 1.0))
    speed_cpm = float(60000.0 / max(mean_interval, 1.0))
    variability = normalize_score(burstiness / 2.0)
    backspace_ratio = float(backspace_events / max(total_events, 1))
    printable_ratio = float(printable_events / max(total_events, 1))
    rhythm_score = normalize_score(
        0.45 * variability
        + 0.30 * normalize_score(pause_ratio)
        + 0.25 * normalize_score(backspace_ratio)
    )

    return {
        "available": True,
        "reason": None,
        "event_count": int(total_events),
        "interval_count": int(len(intervals_ms)),
        "mean_interval_ms": round(mean_interval, 3),
        "std_interval_ms": round(std_interval, 3),
        "burstiness": round(burstiness, 6),
        "pause_ratio": round(pause_ratio, 6),
        "backspace_ratio": round(backspace_ratio, 6),
        "printable_ratio": round(printable_ratio, 6),
        "speed_cpm": round(speed_cpm, 3),
        "rhythm_score": round(rhythm_score, 6),
    }


def _rppg_features_from_video(video_path: str) -> dict:
    if not video_path or not os.path.exists(video_path):
        return {"available": False, "reason": "video_missing"}
    if cv2 is None:
        return {"available": False, "reason": "vision_dependencies_not_installed"}

    capture = cv2.VideoCapture(video_path)
    if not capture.isOpened():
        return {"available": False, "reason": "video_unreadable"}

    fps = float(capture.get(cv2.CAP_PROP_FPS) or 30.0)
    frame_stride = max(1, int(round(fps / 8.0)))
    green_trace: list[float] = []
    frame_count = 0
    sampled_count = 0
    crop_backend = "unknown"

    try:
        while True:
            success, frame = capture.read()
            if not success or frame is None:
                break
            frame_count += 1
            if frame_count % frame_stride != 0:
                continue

            crop, backend = _face_crop_from_frame(frame)
            crop_backend = backend if crop is not None else crop_backend
            if crop is None or crop.size == 0:
                continue
            sampled_count += 1
            green_trace.append(float(np.mean(crop[:, :, 1])))
            if sampled_count >= 240:
                break
    finally:
        capture.release()

    heart_rate_bpm, signal_meta = _estimate_heart_rate_from_signal(green_trace, fps=fps / frame_stride if frame_stride else fps)
    if heart_rate_bpm is None:
        return {
            "available": False,
            "reason": signal_meta.get("reason", "rppg_unavailable"),
            "frame_count": int(frame_count),
            "sample_count": int(sampled_count),
            "fps": round(fps, 3),
            "crop_backend": crop_backend,
            "signal_quality": round(float(signal_meta.get("quality", 0.0)), 6),
        }

    quality = float(signal_meta.get("quality", 0.0))
    heart_rate_score = normalize_score((heart_rate_bpm - 58.0) / 42.0)
    return {
        "available": True,
        "reason": None,
        "frame_count": int(frame_count),
        "sample_count": int(sampled_count),
        "fps": round(fps, 3),
        "crop_backend": crop_backend,
        "heart_rate_bpm": round(float(heart_rate_bpm), 3),
        "heart_rate_score": round(heart_rate_score, 6),
        "signal_quality": round(quality, 6),
        "peak_frequency_hz": signal_meta.get("peak_frequency_hz", 0.0),
        "signal_std": signal_meta.get("signal_std", 0.0),
    }


def extract_passive_biomarkers(
    video_path: str | None = None,
    typing_events: list[dict] | dict | list[float] | None = None,
) -> dict:
    rppg_features = _rppg_features_from_video(video_path) if video_path else {"available": False, "reason": "video_missing"}
    typing_features = _typing_trace_features(typing_events)

    if not rppg_features.get("available") and not typing_features.get("available"):
        return {
            "available": False,
            "reason": "passive_signals_missing",
            "rppg": rppg_features,
            "typing": typing_features,
        }

    rppg_score = float(rppg_features.get("heart_rate_score", 0.0)) if rppg_features.get("available") else 0.0
    typing_score = float(typing_features.get("rhythm_score", 0.0)) if typing_features.get("available") else 0.0
    rppg_quality = float(rppg_features.get("signal_quality", 0.0)) if rppg_features.get("available") else 0.0
    typing_quality = float(typing_features.get("rhythm_score", 0.0)) if typing_features.get("available") else 0.0
    passive_anxiety_score = normalize_score(0.6 * rppg_score + 0.4 * typing_score)
    passive_stress_score = normalize_score(0.5 * rppg_score + 0.5 * typing_score)
    passive_burnout_score = normalize_score(0.25 * rppg_score + 0.75 * typing_score)
    confidence = normalize_score(0.5 * max(rppg_quality, 0.0) + 0.5 * max(typing_quality, 0.0))

    return {
        "available": True,
        "reason": None,
        "confidence": confidence,
        "rppg": rppg_features,
        "typing": typing_features,
        "heart_rate_bpm": rppg_features.get("heart_rate_bpm"),
        "typing_speed_cpm": typing_features.get("speed_cpm"),
        "typing_pause_ratio": typing_features.get("pause_ratio"),
        "typing_backspace_ratio": typing_features.get("backspace_ratio"),
        "passive_anxiety_score": passive_anxiety_score,
        "passive_stress_score": passive_stress_score,
        "passive_burnout_score": passive_burnout_score,
    }


def _normalize_language(language: str | None) -> str:
    text = str(language or "english").strip().lower()
    if text in {"hi", "hindi", "हिन्दी", "हिंदी"}:
        return "hindi"
    if text in {"bn", "bengali", "bangla", "বাংলা"}:
        return "bengali"
    return "english"


def save_upload_file(uploaded_file, suffix):
    suffix = suffix.replace(".", "")
    file_ext = os.path.splitext(uploaded_file.name)[1]
    fh, path = tempfile.mkstemp(suffix=f"_{suffix}{file_ext}")
    with os.fdopen(fh, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path


def _empty_transformer_features(reason: str | None = None) -> dict:
    return {
        "transformer_available": False,
        "transformer_model": None,
        "transformer_family": None,
        "transformer_preferred_family": None,
        "transformer_language": None,
        "transformer_reason": reason,
        "embedding_mean": 0.0,
        "embedding_std": 0.0,
        "token_count": 0,
    }


def _transformer_family(model_name: str) -> str:
    lowered = str(model_name).lower()
    if "muril" in lowered:
        return "muril"
    if "indicbert" in lowered:
        return "indic-bert"
    if "distilbert" in lowered:
        return "distilbert"
    if "bert" in lowered:
        return "bert"
    return "transformer"


def _transformer_candidates_for_language(language: str) -> tuple[str, ...]:
    normalized_language = _normalize_language(language)
    return LANGUAGE_NATIVE_TRANSFORMER_CANDIDATES.get(
        normalized_language,
        LANGUAGE_NATIVE_TRANSFORMER_CANDIDATES["english"],
    )


@lru_cache(maxsize=4)
def _load_transformer_encoder(language: str = "english"):
    if AutoTokenizer is None or AutoModel is None or torch is None:
        return None

    normalized_language = _normalize_language(language)
    candidates = _transformer_candidates_for_language(normalized_language)
    preferred_family = LANGUAGE_NATIVE_TRANSFORMER_FAMILIES.get(
        normalized_language,
        LANGUAGE_NATIVE_TRANSFORMER_FAMILIES["english"],
    )
    for model_name in candidates:
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
            model = AutoModel.from_pretrained(model_name, local_files_only=True)
            model.eval()
            return {
                "model_name": model_name,
                "model_family": _transformer_family(model_name),
                "preferred_family": preferred_family,
                "language": normalized_language,
                "tokenizer": tokenizer,
                "model": model,
            }
        except Exception:
            continue
    return None


@lru_cache(maxsize=1)
def _load_sentiment_pipeline():
    if pipeline is None:
        return None

    for model_name in SENTIMENT_MODEL_CANDIDATES:
        try:
            return {
                "model_name": model_name,
                "pipeline": pipeline(
                    "sentiment-analysis",
                    model=model_name,
                    tokenizer=model_name,
                    local_files_only=True,
                ),
            }
        except Exception:
            continue
    return None


@lru_cache(maxsize=1)
def _load_emotion_pipeline():
    if pipeline is None:
        return None

    for model_name in EMOTION_MODEL_CANDIDATES:
        try:
            return {
                "model_name": model_name,
                "pipeline": pipeline(
                    "text-classification",
                    model=model_name,
                    tokenizer=model_name,
                    top_k=None,
                    local_files_only=True,
                ),
            }
        except Exception:
            continue
    return None


def _transformer_text_features(text: str, language: str = "english") -> dict:
    normalized_language = _normalize_language(language)
    bundle = _load_transformer_encoder(normalized_language)
    if bundle is None:
        if normalized_language in {"hindi", "bengali"}:
            return _empty_transformer_features(f"{normalized_language}_native_model_not_available_locally")
        return _empty_transformer_features("english_model_not_available_locally")

    try:
        encoded = bundle["tokenizer"](
            text,
            truncation=True,
            padding=True,
            max_length=128,
            return_tensors="pt",
        )
        with torch.no_grad():
            outputs = bundle["model"](**encoded)
        hidden_state = outputs.last_hidden_state
        pooled = hidden_state.mean(dim=1).squeeze(0)
        return {
            "transformer_available": True,
            "transformer_model": bundle["model_name"],
            "transformer_family": bundle["model_family"],
            "transformer_preferred_family": bundle.get("preferred_family"),
            "transformer_language": bundle["language"],
            "transformer_reason": None,
            "embedding_mean": float(pooled.mean().item()),
            "embedding_std": float(pooled.std().item()),
            "token_count": int(encoded["attention_mask"].sum().item()),
        }
    except Exception:
        return _empty_transformer_features("transformer_inference_failed")


def _sentiment_features(text: str, fallback_compound: float, language: str = "english", use_ml_pipeline: bool = True) -> dict:
    sentiment_bundle = _load_sentiment_pipeline() if use_ml_pipeline and _normalize_language(language) == "english" else None
    if sentiment_bundle is not None:
        try:
            result = sentiment_bundle["pipeline"](text[:512])[0]
            label = str(result["label"]).lower()
            score = float(result["score"])
            compound = score if "pos" in label else -score
            return {
                "sentiment_model": sentiment_bundle["model_name"],
                "sentiment_label": "positive" if compound >= 0 else "negative",
                "sentiment_confidence": score,
                "sentiment_compound": compound,
            }
        except Exception:
            pass

    return {
        "sentiment_model": "vader" if analyzer is not None else "heuristic",
        "sentiment_label": "positive" if fallback_compound >= 0 else "negative",
        "sentiment_confidence": abs(fallback_compound),
        "sentiment_compound": fallback_compound,
    }


def _emotion_features(lowered_words: list[str], text: str, language: str = "english", use_ml_pipeline: bool = True) -> dict:
    emotion_bundle = _load_emotion_pipeline() if use_ml_pipeline and _normalize_language(language) == "english" else None
    if emotion_bundle is not None:
        try:
            raw = emotion_bundle["pipeline"](text[:512])[0]
            scores = {}
            for item in raw:
                label = str(item["label"]).lower().replace(" ", "_")
                scores[label] = float(item["score"])
            dominant = max(scores, key=scores.get) if scores else "unknown"
            return {
                "emotion_model": emotion_bundle["model_name"],
                "dominant_emotion": dominant,
                "emotion_scores": scores,
            }
        except Exception:
            pass

    language_rules = LANGUAGE_TEXT_RULES[_normalize_language(language)]
    emotion_keywords = language_rules["emotion_keywords"]
    counts = {
        emotion: sum(1 for word in lowered_words if word in keywords)
        for emotion, keywords in emotion_keywords.items()
    }
    total = sum(counts.values()) or 1
    scores = {emotion: count / total for emotion, count in counts.items()}
    dominant = max(scores, key=scores.get) if any(counts.values()) else "neutral"
    return {
        "emotion_model": "keyword_heuristic",
        "dominant_emotion": dominant,
        "emotion_scores": scores,
    }


def _self_harm_features(text: str, language: str = "english") -> dict:
    lowered = text.lower()
    language_rules = LANGUAGE_TEXT_RULES[_normalize_language(language)]
    matches = [keyword for keyword in language_rules["self_harm_keywords"] if keyword in lowered]
    severity = min(1.0, len(matches) / 2.0) if matches else 0.0
    return {
        "self_harm_keyword_detected": bool(matches),
        "self_harm_keyword_matches": matches,
        "self_harm_risk_score": severity,
    }


def _distress_phrase_features(text: str, language: str = "english") -> dict:
    lowered = text.lower()
    language_rules = LANGUAGE_TEXT_RULES[_normalize_language(language)]
    matches = [phrase for phrase in language_rules.get("distress_phrases", set()) if phrase in lowered]
    severity = min(1.0, len(matches) / 2.0) if matches else 0.0
    return {
        "distress_phrase_detected": bool(matches),
        "distress_phrase_matches": matches,
        "distress_phrase_risk_score": severity,
    }


def _agrarian_distress_features(text: str, language: str = "english") -> dict:
    lowered = text.lower()
    language_rules = AGRARIAN_DISTRESS_PHRASES[_normalize_language(language)]
    crop_matches = [phrase for phrase in language_rules.get("crop_failure_phrases", set()) if phrase in lowered]
    debt_matches = [phrase for phrase in language_rules.get("debt_phrases", set()) if phrase in lowered]
    food_matches = [phrase for phrase in language_rules.get("food_security_phrases", set()) if phrase in lowered]
    all_matches = crop_matches + debt_matches + food_matches
    crop_score = min(1.0, len(crop_matches) / 2.0) if crop_matches else 0.0
    debt_score = min(1.0, len(debt_matches) / 2.0) if debt_matches else 0.0
    food_score = min(1.0, len(food_matches) / 2.0) if food_matches else 0.0
    severity = min(1.0, (crop_score + debt_score + food_score) / 3.0)
    return {
        "agrarian_distress_detected": bool(all_matches),
        "agrarian_distress_matches": all_matches,
        "agrarian_distress_risk_score": severity,
        "crop_failure_detected": bool(crop_matches),
        "crop_failure_matches": crop_matches,
        "crop_failure_risk_score": crop_score,
        "debt_distress_detected": bool(debt_matches),
        "debt_distress_matches": debt_matches,
        "debt_distress_risk_score": debt_score,
        "food_security_detected": bool(food_matches),
        "food_security_matches": food_matches,
        "food_security_risk_score": food_score,
    }


def extract_text_features(
    text: str,
    language: str = "english",
    use_transformer: bool = True,
    use_ml_pipelines: bool = True,
) -> dict:
    if not text:
        return {"available": False}

    normalized_language = _normalize_language(language)
    language_rules = LANGUAGE_TEXT_RULES[normalized_language]

    if analyzer is not None and normalized_language == "english":
        vader_sentiment = analyzer.polarity_scores(text)
    else:
        vader_sentiment = {"compound": 0.0}

    words = text.split()
    lowered_words = [word.strip(".,!?;:()[]{}\"'").lower() for word in words]
    negative = sum(1 for w in lowered_words if w in language_rules["negative_words"])
    positive = sum(1 for w in lowered_words if w in language_rules["positive_words"])
    distress_phrase_features = _distress_phrase_features(text, language=normalized_language)
    agrarian_distress_features = _agrarian_distress_features(text, language=normalized_language)
    distress_phrase_bonus = len(distress_phrase_features["distress_phrase_matches"]) * 2
    agrarian_distress_bonus = len(agrarian_distress_features["agrarian_distress_matches"])
    heuristic_compound = np.clip(
        (positive - negative - distress_phrase_bonus - agrarian_distress_bonus) / max(1, len(lowered_words)),
        -1.0,
        1.0,
    )
    question_count = text.count("?")
    exclamation_count = text.count("!")
    unique_ratio = len(set(lowered_words)) / max(1, len(lowered_words))
    transformer_features = _transformer_text_features(text, normalized_language) if use_transformer else {
        **_empty_transformer_features("transformer_disabled"),
    }
    sentiment_features = _sentiment_features(
        text,
        vader_sentiment["compound"] if normalized_language == "english" else heuristic_compound,
        language=normalized_language,
        use_ml_pipeline=use_ml_pipelines,
    )
    emotion_features = _emotion_features(
        lowered_words,
        text,
        language=normalized_language,
        use_ml_pipeline=use_ml_pipelines,
    )
    self_harm_features = _self_harm_features(text, language=normalized_language)

    features = {
        "available": True,
        "word_count": len(words),
        "sentiment_compound": sentiment_features["sentiment_compound"],
        "sentiment_label": sentiment_features["sentiment_label"],
        "sentiment_confidence": sentiment_features["sentiment_confidence"],
        "sentiment_model": sentiment_features["sentiment_model"],
        "negative_word_count": negative,
        "positive_word_count": positive,
        "distress_phrase_count": len(distress_phrase_features["distress_phrase_matches"]),
        "distress_phrase_matches": distress_phrase_features["distress_phrase_matches"],
        "distress_phrase_detected": distress_phrase_features["distress_phrase_detected"],
        "distress_phrase_risk_score": distress_phrase_features["distress_phrase_risk_score"],
        **agrarian_distress_features,
        "question_ratio": question_count / max(1, len(words)),
        "exclamation_ratio": exclamation_count / max(1, len(words)),
        "emotion_intensity": min(1.0, abs(sentiment_features["sentiment_compound"]) + distress_phrase_features["distress_phrase_risk_score"]),
        "lexical_diversity": unique_ratio,
        "transformer_available": transformer_features["transformer_available"],
        "transformer_model": transformer_features["transformer_model"],
        "transformer_family": transformer_features["transformer_family"],
        "transformer_preferred_family": transformer_features["transformer_preferred_family"],
        "transformer_language": transformer_features["transformer_language"],
        "transformer_reason": transformer_features["transformer_reason"],
        "transformer_embedding_mean": transformer_features["embedding_mean"],
        "transformer_embedding_std": transformer_features["embedding_std"],
        "transformer_token_count": transformer_features["token_count"],
        "emotion_model": emotion_features["emotion_model"],
        "dominant_emotion": emotion_features["dominant_emotion"],
        "emotion_scores": emotion_features["emotion_scores"],
        "language": normalized_language,
        "self_harm_keyword_detected": self_harm_features["self_harm_keyword_detected"],
        "self_harm_keyword_matches": self_harm_features["self_harm_keyword_matches"],
        "self_harm_risk_score": self_harm_features["self_harm_risk_score"],
    }
    return features


def extract_audio_features(audio_path: str, include_pitch_features: bool = True) -> dict:
    if not audio_path or not os.path.exists(audio_path):
        return {"available": False}
    if librosa is None:
        return {"available": False, "reason": "librosa_not_installed"}

    try:
        signal, sr = librosa.load(audio_path, sr=16000, mono=True)
    except Exception:
        return {"available": False}

    duration = float(len(signal)) / sr
    if duration <= 0:
        return {"available": False, "reason": "audio_invalid_duration", "duration": duration}
    if duration < AUDIO_MIN_DURATION_SECONDS:
        return {
            "available": False,
            "reason": "audio_too_short",
            "duration": duration,
            "minimum_duration": AUDIO_MIN_DURATION_SECONDS,
        }

    amplitude = np.abs(signal)
    energy = float(np.mean(amplitude))
    tempo, _ = librosa.beat.beat_track(y=signal, sr=sr)
    zcr = float(np.mean(librosa.feature.zero_crossing_rate(signal)))
    rms = float(np.mean(librosa.feature.rms(y=signal)))
    if include_pitch_features:
        try:
            pitch, voiced_flags, _ = librosa.pyin(
                signal,
                sr=sr,
                fmin=librosa.note_to_hz("C2"),
                fmax=librosa.note_to_hz("C7"),
            )
            valid_pitch = pitch[~np.isnan(pitch)] if pitch is not None else np.array([])
            voiced_ratio = float(np.mean(voiced_flags)) if voiced_flags is not None else 0.0
            pitch_mean = float(np.mean(valid_pitch)) if valid_pitch.size else 0.0
            pitch_std = float(np.std(valid_pitch)) if valid_pitch.size else 0.0
        except Exception:
            voiced_ratio = 0.0
            pitch_mean = 0.0
            pitch_std = 0.0
    else:
        voiced_ratio = 0.0
        pitch_mean = 0.0
        pitch_std = 0.0

    return {
        "available": True,
        "duration": duration,
        "tempo": float(tempo),
        "zero_crossing_rate": zcr,
        "rms": rms,
        "energy": energy,
        "pitch_mean": pitch_mean,
        "pitch_std": pitch_std,
        "voiced_ratio": voiced_ratio,
    }


def extract_image_features(image_path: str) -> dict:
    if not image_path or not os.path.exists(image_path):
        return {"available": False}
    if cv2 is None:
        return {"available": False, "reason": "vision_dependencies_not_installed"}

    image = cv2.imread(image_path)
    if image is None:
        return {"available": False, "reason": "image_unreadable"}

    def opencv_face_fallback() -> dict:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cascade_path = getattr(cv2.data, "haarcascades", "") + "haarcascade_frontalface_default.xml"
        if not cascade_path or not os.path.exists(cascade_path):
            return {"available": False, "reason": "no_face_detected"}

        detector = cv2.CascadeClassifier(cascade_path)
        faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
        if faces is None or len(faces) == 0:
            return {"available": False, "reason": "no_face_detected"}

        x, y, w, h = max(faces, key=lambda box: box[2] * box[3])
        face_crop = gray[y : y + h, x : x + w]
        if face_crop.size == 0:
            return {"available": False, "reason": "no_face_detected"}

        upper_band = face_crop[int(h * 0.18) : int(h * 0.42), :]
        lower_band = face_crop[int(h * 0.58) : int(h * 0.85), :]
        eye_signal = float(np.std(upper_band) / 255.0) if upper_band.size else 0.0
        mouth_signal = float(np.std(lower_band) / 255.0) if lower_band.size else 0.0
        smile_ratio = float(np.clip((w / max(h, 1)) + mouth_signal, 0.8, 3.0))
        eye_openness = float(np.clip(0.01 + eye_signal * 0.08, 0.005, 0.06))

        return {
            "available": True,
            "face_detected": True,
            "smile_ratio": smile_ratio,
            "mouth_width": float(w),
            "mouth_height": float(max(1.0, h * 0.35)),
            "eye_openness": eye_openness,
            "face_height": float(h),
            "face_width": float(w),
            "vision_backend": "opencv_haar_fallback",
        }

    if mp is None or not hasattr(mp, "solutions"):
        return opencv_face_fallback()

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_face = mp.solutions.face_mesh
    with mp_face.FaceMesh(static_image_mode=True, max_num_faces=1) as face_mesh:
        results = face_mesh.process(image_rgb)
        if not results.multi_face_landmarks:
            return opencv_face_fallback()

        face = results.multi_face_landmarks[0]
        landmarks = [(lm.x, lm.y) for lm in face.landmark]

    left_mouth = landmarks[61]
    right_mouth = landmarks[291]
    top_mouth = landmarks[13]
    bottom_mouth = landmarks[14]
    left_eye_top = landmarks[159]
    left_eye_bottom = landmarks[145]
    right_eye_top = landmarks[386]
    right_eye_bottom = landmarks[374]
    brow_center = landmarks[9]
    chin = landmarks[152]

    mouth_width = np.linalg.norm(np.subtract(right_mouth, left_mouth))
    mouth_height = np.linalg.norm(np.subtract(bottom_mouth, top_mouth))
    smile_ratio = mouth_width / max(1e-6, mouth_height)
    left_eye_open = np.linalg.norm(np.subtract(left_eye_bottom, left_eye_top))
    right_eye_open = np.linalg.norm(np.subtract(right_eye_bottom, right_eye_top))
    eye_openness = float((left_eye_open + right_eye_open) / 2.0)
    face_height = np.linalg.norm(np.subtract(chin, brow_center))

    return {
        "available": True,
        "face_detected": True,
        "smile_ratio": float(smile_ratio),
        "mouth_width": float(mouth_width),
        "mouth_height": float(mouth_height),
        "eye_openness": eye_openness,
        "face_height": float(face_height),
        "vision_backend": "mediapipe_face_mesh",
    }
