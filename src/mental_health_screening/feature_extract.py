import os
import tempfile
from functools import lru_cache
import numpy as np
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

NEGATIVE_WORDS = {
    "sad",
    "hopeless",
    "worried",
    "anxious",
    "tired",
    "nervous",
    "stressed",
    "lonely",
    "empty",
    "afraid",
    "panic",
    "overwhelmed",
    "helpless",
    "worthless",
}

POSITIVE_WORDS = {
    "better",
    "hopeful",
    "calm",
    "good",
    "safe",
    "supported",
    "strong",
    "improving",
}

SELF_HARM_KEYWORDS = {
    "kill myself",
    "end my life",
    "don't want to live",
    "do not want to live",
    "suicide",
    "self harm",
    "harm myself",
    "hurt myself",
    "want to die",
    "better off dead",
    "no reason to live",
}

EMOTION_KEYWORDS = {
    "sadness": {"sad", "empty", "hopeless", "crying", "down", "unhappy"},
    "fear": {"afraid", "fear", "panic", "scared", "terrified", "nervous"},
    "anger": {"angry", "irritated", "frustrated", "annoyed", "furious"},
    "joy": {"happy", "relieved", "calm", "good", "hopeful", "better"},
    "loneliness": {"alone", "isolated", "lonely", "disconnected", "abandoned"},
    "exhaustion": {"tired", "drained", "burned", "burnout", "exhausted", "sleepy"},
}

TRANSFORMER_ENCODER_CANDIDATES = (
    "distilbert-base-uncased",
    "bert-base-uncased",
)

SENTIMENT_MODEL_CANDIDATES = (
    "distilbert-base-uncased-finetuned-sst-2-english",
    "textattack/bert-base-uncased-imdb",
)

EMOTION_MODEL_CANDIDATES = (
    "bhadresh-savani/distilbert-base-uncased-emotion",
    "nateraw/bert-base-uncased-emotion",
)

AUDIO_MIN_DURATION_SECONDS = 2.5


def save_upload_file(uploaded_file, suffix):
    suffix = suffix.replace(".", "")
    file_ext = os.path.splitext(uploaded_file.name)[1]
    fh, path = tempfile.mkstemp(suffix=f"_{suffix}{file_ext}")
    with os.fdopen(fh, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path


@lru_cache(maxsize=1)
def _load_transformer_encoder():
    if AutoTokenizer is None or AutoModel is None or torch is None:
        return None

    for model_name in TRANSFORMER_ENCODER_CANDIDATES:
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
            model = AutoModel.from_pretrained(model_name, local_files_only=True)
            model.eval()
            return {"model_name": model_name, "tokenizer": tokenizer, "model": model}
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


def _transformer_text_features(text: str) -> dict:
    bundle = _load_transformer_encoder()
    if bundle is None:
        return {
            "transformer_available": False,
            "transformer_model": None,
            "embedding_mean": 0.0,
            "embedding_std": 0.0,
            "token_count": 0,
        }

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
            "embedding_mean": float(pooled.mean().item()),
            "embedding_std": float(pooled.std().item()),
            "token_count": int(encoded["attention_mask"].sum().item()),
        }
    except Exception:
        return {
            "transformer_available": False,
            "transformer_model": None,
            "embedding_mean": 0.0,
            "embedding_std": 0.0,
            "token_count": 0,
        }


def _sentiment_features(text: str, fallback_compound: float) -> dict:
    sentiment_bundle = _load_sentiment_pipeline()
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


def _emotion_features(lowered_words: list[str], text: str) -> dict:
    emotion_bundle = _load_emotion_pipeline()
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

    counts = {
        emotion: sum(1 for word in lowered_words if word in keywords)
        for emotion, keywords in EMOTION_KEYWORDS.items()
    }
    total = sum(counts.values()) or 1
    scores = {emotion: count / total for emotion, count in counts.items()}
    dominant = max(scores, key=scores.get) if any(counts.values()) else "neutral"
    return {
        "emotion_model": "keyword_heuristic",
        "dominant_emotion": dominant,
        "emotion_scores": scores,
    }


def _self_harm_features(text: str) -> dict:
    lowered = text.lower()
    matches = [keyword for keyword in SELF_HARM_KEYWORDS if keyword in lowered]
    severity = min(1.0, len(matches) / 2.0) if matches else 0.0
    return {
        "self_harm_keyword_detected": bool(matches),
        "self_harm_keyword_matches": matches,
        "self_harm_risk_score": severity,
    }


def extract_text_features(text: str) -> dict:
    if not text:
        return {"available": False}

    if analyzer is not None:
        vader_sentiment = analyzer.polarity_scores(text)
    else:
        vader_sentiment = {"compound": 0.0}

    words = text.split()
    lowered_words = [word.strip(".,!?;:()[]{}\"'").lower() for word in words]
    negative = sum(1 for w in lowered_words if w in NEGATIVE_WORDS)
    positive = sum(1 for w in lowered_words if w in POSITIVE_WORDS)
    question_count = text.count("?")
    exclamation_count = text.count("!")
    unique_ratio = len(set(lowered_words)) / max(1, len(lowered_words))
    transformer_features = _transformer_text_features(text)
    sentiment_features = _sentiment_features(text, vader_sentiment["compound"])
    emotion_features = _emotion_features(lowered_words, text)
    self_harm_features = _self_harm_features(text)

    features = {
        "available": True,
        "word_count": len(words),
        "sentiment_compound": sentiment_features["sentiment_compound"],
        "sentiment_label": sentiment_features["sentiment_label"],
        "sentiment_confidence": sentiment_features["sentiment_confidence"],
        "sentiment_model": sentiment_features["sentiment_model"],
        "negative_word_count": negative,
        "positive_word_count": positive,
        "question_ratio": question_count / max(1, len(words)),
        "exclamation_ratio": exclamation_count / max(1, len(words)),
        "emotion_intensity": abs(sentiment_features["sentiment_compound"]),
        "lexical_diversity": unique_ratio,
        "transformer_available": transformer_features["transformer_available"],
        "transformer_model": transformer_features["transformer_model"],
        "transformer_embedding_mean": transformer_features["embedding_mean"],
        "transformer_embedding_std": transformer_features["embedding_std"],
        "transformer_token_count": transformer_features["token_count"],
        "emotion_model": emotion_features["emotion_model"],
        "dominant_emotion": emotion_features["dominant_emotion"],
        "emotion_scores": emotion_features["emotion_scores"],
        "self_harm_keyword_detected": self_harm_features["self_harm_keyword_detected"],
        "self_harm_keyword_matches": self_harm_features["self_harm_keyword_matches"],
        "self_harm_risk_score": self_harm_features["self_harm_risk_score"],
    }
    return features


def extract_audio_features(audio_path: str) -> dict:
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
