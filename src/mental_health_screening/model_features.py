from __future__ import annotations

from .constants import PREDICTION_DOMAINS


TEXT_EMOTION_KEYS = ("sadness", "fear", "anger", "joy", "loneliness", "exhaustion")
TEXT_EMOTION_PROXY_MASK = {"loneliness", "exhaustion"}


def text_feature_vector(features: dict) -> tuple[list[str], list[float]]:
    names = [
        "word_count",
        "sentiment_compound",
        "sentiment_confidence",
        "negative_word_count",
        "positive_word_count",
        "question_ratio",
        "exclamation_ratio",
        "emotion_intensity",
        "lexical_diversity",
        "transformer_embedding_mean",
        "transformer_embedding_std",
        "transformer_token_count",
        "self_harm_risk_score",
        "anxiety_keyword_count",
        "anxiety_keyword_risk_score",
        "substance_keyword_count",
        "substance_keyword_risk_score",
    ]
    values = [
        float(features.get("word_count", 0.0)),
        float(features.get("sentiment_compound", 0.0)),
        float(features.get("sentiment_confidence", 0.0)),
        float(features.get("negative_word_count", 0.0)),
        float(features.get("positive_word_count", 0.0)),
        float(features.get("question_ratio", 0.0)),
        float(features.get("exclamation_ratio", 0.0)),
        float(features.get("emotion_intensity", 0.0)),
        float(features.get("lexical_diversity", 0.0)),
        float(features.get("transformer_embedding_mean", 0.0)),
        float(features.get("transformer_embedding_std", 0.0)),
        float(features.get("transformer_token_count", 0.0)),
        float(features.get("self_harm_risk_score", 0.0)),
        float(features.get("anxiety_keyword_count", 0.0)),
        float(features.get("anxiety_keyword_risk_score", 0.0)),
        float(features.get("substance_keyword_count", 0.0)),
        float(features.get("substance_keyword_risk_score", 0.0)),
    ]
    emotion_scores = features.get("emotion_scores", {}) or {}
    for key in TEXT_EMOTION_KEYS:
        names.append(f"emotion_{key}")
        raw_value = float(emotion_scores.get(key, 0.0))
        # Keep the raw extractor available for analytics, but mask the most
        # label-adjacent emotion cues during model training/inference so the
        # text bundle doesn't overfit to proxy targets like loneliness or burnout.
        values.append(0.0 if key in TEXT_EMOTION_PROXY_MASK else raw_value)
    names.append("transformer_available")
    values.append(1.0 if features.get("transformer_available") else 0.0)
    names.append("self_harm_keyword_detected")
    values.append(1.0 if features.get("self_harm_keyword_detected") else 0.0)
    return names, values


def audio_feature_vector(features: dict) -> tuple[list[str], list[float]]:
    names = [
        "duration",
        "tempo",
        "zero_crossing_rate",
        "rms",
        "energy",
        "spectral_centroid",
        "spectral_bandwidth",
        "spectral_rolloff",
        "spectral_flatness",
        "pitch_mean",
        "pitch_std",
        "voiced_ratio",
        "mfcc_mean_1",
        "mfcc_mean_2",
        "mfcc_mean_3",
        "mfcc_mean_4",
        "mfcc_mean_5",
        "mfcc_mean_6",
        "mfcc_std_1",
        "mfcc_std_2",
        "mfcc_std_3",
        "mfcc_std_4",
        "mfcc_std_5",
        "mfcc_std_6",
    ]
    values = [float(features.get(name, 0.0)) for name in names]
    return names, values


def image_feature_vector(features: dict) -> tuple[list[str], list[float]]:
    names = [
        "smile_ratio",
        "mouth_width",
        "mouth_height",
        "eye_openness",
        "face_height",
        "face_width",
        "mouth_aspect_ratio",
        "eye_to_face_ratio",
        "mouth_to_face_ratio",
        "brow_chin_ratio",
    ]
    values = [float(features.get(name, 0.0)) for name in names]
    return names, values


def target_vector(row: dict) -> list[float]:
    return [float(row.get(domain, 0.0)) for domain in PREDICTION_DOMAINS]
