import numpy as np

from .constants import PREDICTION_DOMAINS, PREDICTION_LABELS
from .feature_extract import extract_text_features, extract_audio_features, extract_image_features
from .model_features import audio_feature_vector, image_feature_vector, text_feature_vector
from .model_store import load_model_bundle
from .utils import average, normalize_score, risk_level


MODALITY_WEIGHTS = {
    "text": 0.4,
    "audio": 0.35,
    "image": 0.25,
}


def _confidence_from_feature_count(feature_count: int, max_count: int) -> float:
    return normalize_score(feature_count / max_count)


def _domain_score_agreement(score_sets: list[dict]) -> float:
    if len(score_sets) < 2:
        return 0.85

    agreements = []
    for domain in PREDICTION_DOMAINS:
        values = [normalize_score(scores.get(domain, 0.0)) for scores in score_sets]
        spread = max(values) - min(values)
        agreements.append(1.0 - spread)
    return normalize_score(average(agreements))


def _modality_result(
    modality: str,
    domain_scores: dict,
    notes: str,
    confidence: float,
    feature_snapshot: dict,
) -> dict:
    result = {
        "available": True,
        "modality": modality,
        "confidence": normalize_score(confidence),
        "notes": notes,
        "features": feature_snapshot,
    }
    for domain in PREDICTION_DOMAINS:
        result[f"{domain}_score"] = normalize_score(domain_scores.get(domain, 0.0))
    return result


def _trained_modality_result(
    modality: str,
    features: dict,
    feature_vector_fn,
    fallback_confidence: float,
    notes: str,
    feature_snapshot: dict,
    fallback_domain_scores: dict,
) -> dict | None:
    if not features.get("available"):
        return None

    bundle = load_model_bundle(modality)
    if bundle is None:
        return None

    _, vector = feature_vector_fn(features)
    domain_scores = {domain: normalize_score(fallback_domain_scores.get(domain, 0.0)) for domain in PREDICTION_DOMAINS}
    trained_domains = []
    fallback_domains = []

    if bundle.get("models"):
        for domain in PREDICTION_DOMAINS:
            model = bundle["models"].get(domain)
            if model is None:
                fallback_domains.append(domain)
                continue
            prediction = float(np.clip(model.predict([vector])[0], 0.0, 1.0))
            domain_scores[domain] = normalize_score(prediction)
            trained_domains.append(domain)
        if not trained_domains:
            return None
    elif bundle.get("model") is not None:
        prediction = bundle["model"].predict([vector])[0]
        domain_scores = {
            domain: normalize_score(prediction[index])
            for index, domain in enumerate(bundle["domains"])
        }
        trained_domains = list(bundle["domains"])
        fallback_domains = [domain for domain in PREDICTION_DOMAINS if domain not in trained_domains]
    else:
        return None

    confidence = average([fallback_confidence, float(bundle.get("confidence_hint", 0.65))])
    return _modality_result(
        modality=modality,
        domain_scores=domain_scores,
        confidence=confidence,
        notes=notes,
        feature_snapshot={
            **feature_snapshot,
            "model_source": "trained_bundle",
            "trained_samples": bundle.get("sample_count", 0),
            "trained_domains": trained_domains,
            "fallback_domains": fallback_domains,
            "domain_sample_counts": bundle.get("sample_counts", {}),
            "model_macro_r2": round(float(bundle.get("metrics", {}).get("macro_r2", 0.0)), 3),
        },
    )


def score_text_features(features: dict) -> dict:
    if not features.get("available"):
        return {"available": False}

    negative_density = features["negative_word_count"] / max(1, features["word_count"])
    positive_density = features["positive_word_count"] / max(1, features["word_count"])
    short_response_penalty = 0.15 if features["word_count"] < 8 else 0.0
    sadness_score = features["emotion_scores"].get("sadness", 0.0)
    fear_score = features["emotion_scores"].get("fear", 0.0)
    anger_score = features["emotion_scores"].get("anger", 0.0)
    joy_score = features["emotion_scores"].get("joy", 0.0)
    loneliness_score_signal = features["emotion_scores"].get("loneliness", 0.0)
    exhaustion_score = features["emotion_scores"].get("exhaustion", 0.0)
    self_harm_score = features["self_harm_risk_score"]
    transformer_signal = normalize_score(abs(features["transformer_embedding_std"]) * 10.0)

    domain_scores = {
        "depression": (
        0.55
        - 0.45 * features["sentiment_compound"]
        + 1.8 * negative_density
        - 0.9 * positive_density
        + short_response_penalty
        + 0.7 * sadness_score
        + 0.9 * self_harm_score
        ),
        "anxiety": (
        0.15
        + 2.0 * negative_density
        + 1.8 * features["question_ratio"]
        + 1.2 * features["exclamation_ratio"]
        + 0.6 * fear_score
        + 0.25 * transformer_signal
        ),
        "stress": (
        0.2
        + 0.8 * features["emotion_intensity"]
        + 0.8 * negative_density
        + 0.2 * (1.0 - features["lexical_diversity"])
        + 0.35 * anger_score
        + 0.25 * transformer_signal
        ),
        "sleep_disorder": (
        0.18
        + 1.4 * negative_density
        + 0.35 * short_response_penalty
        + 0.45 * features["emotion_intensity"]
        + 0.35 * exhaustion_score
        ),
        "burnout": (
        0.2
        + 1.6 * negative_density
        + 0.55 * features["emotion_intensity"]
        + 0.25 * (1.0 - features["lexical_diversity"])
        + 0.45 * exhaustion_score
        + 0.15 * anger_score
        ),
        "loneliness": (
        0.16
        + 1.25 * negative_density
        + 0.3 * (1.0 - positive_density)
        + 0.25 * short_response_penalty
        + 0.8 * loneliness_score_signal
        ),
        "substance_abuse": (
        0.08
        + 0.85 * negative_density
        + 0.35 * features["emotion_intensity"]
        + 0.25 * anger_score
        + 0.2 * self_harm_score
        ),
    }

    confidence = _confidence_from_feature_count(min(features["word_count"], 40), 40)
    if features["transformer_available"]:
        confidence = average([confidence, 0.95])
    if features["word_count"] >= 20:
        confidence = average([confidence, 0.9])
    if features["word_count"] >= 40:
        confidence = max(confidence, 0.9)

    trained_result = _trained_modality_result(
        modality="text",
        features=features,
        feature_vector_fn=text_feature_vector,
        fallback_confidence=confidence,
        notes=(
            "Text screening used a trained text model built from labeled examples, alongside sentiment, "
            "emotion, and safety-language features extracted by the backend."
        ),
        feature_snapshot={
            "word_count": features["word_count"],
            "negative_word_count": features["negative_word_count"],
            "positive_word_count": features["positive_word_count"],
            "sentiment_compound": round(features["sentiment_compound"], 3),
            "sentiment_label": features["sentiment_label"],
            "sentiment_model": features["sentiment_model"],
            "dominant_emotion": features["dominant_emotion"],
            "emotion_model": features["emotion_model"],
            "self_harm_keyword_detected": features["self_harm_keyword_detected"],
            "self_harm_keyword_matches": features["self_harm_keyword_matches"],
            "self_harm_risk_score": round(features["self_harm_risk_score"], 3),
            "transformer_model": features["transformer_model"] or "unavailable",
        },
        fallback_domain_scores=domain_scores,
    )
    if trained_result is not None:
        return trained_result

    return _modality_result(
        modality="text",
        domain_scores=domain_scores,
        confidence=confidence,
        notes=(
            "Text screening now combines sentiment analysis, emotion detection, self-harm keyword checks, "
            "and optional DistilBERT or BERT representations. Longer and more detailed responses usually "
            "give more reliable screening clues."
        ),
        feature_snapshot={
            "word_count": features["word_count"],
            "negative_word_count": features["negative_word_count"],
            "positive_word_count": features["positive_word_count"],
            "sentiment_compound": round(features["sentiment_compound"], 3),
            "sentiment_label": features["sentiment_label"],
            "sentiment_model": features["sentiment_model"],
            "dominant_emotion": features["dominant_emotion"],
            "emotion_model": features["emotion_model"],
            "self_harm_keyword_detected": features["self_harm_keyword_detected"],
            "self_harm_keyword_matches": features["self_harm_keyword_matches"],
            "self_harm_risk_score": round(features["self_harm_risk_score"], 3),
            "transformer_model": features["transformer_model"] or "unavailable",
        },
    )


def score_audio_features(features: dict) -> dict:
    if not features.get("available"):
        return {**features, "available": False}

    slow_tempo = max(0.0, (110.0 - features["tempo"]) / 110.0)
    high_energy = normalize_score(features["rms"] * 8.0)
    unstable_pitch = normalize_score(features["pitch_std"] / 80.0)
    low_voicing = normalize_score(1.0 - features["voiced_ratio"])

    domain_scores = {
        "depression": 0.2 + 0.7 * slow_tempo + 0.4 * low_voicing,
        "anxiety": 0.15 + 0.65 * high_energy + 0.45 * unstable_pitch,
        "stress": 0.2 + 0.55 * normalize_score(features["zero_crossing_rate"] * 10.0) + 0.45 * high_energy,
        "sleep_disorder": 0.18 + 0.55 * low_voicing + 0.35 * slow_tempo + 0.2 * unstable_pitch,
        "burnout": 0.18 + 0.45 * slow_tempo + 0.35 * low_voicing + 0.25 * high_energy,
        "loneliness": 0.1 + 0.4 * low_voicing + 0.35 * slow_tempo,
        "substance_abuse": 0.1 + 0.3 * unstable_pitch + 0.35 * high_energy + 0.2 * normalize_score(features["zero_crossing_rate"] * 10.0),
    }

    duration_confidence = normalize_score(features["duration"] / 12.0)
    voiced_confidence = normalize_score(features["voiced_ratio"])
    acoustic_confidence = average([
        duration_confidence,
        voiced_confidence,
        1.0 - min(low_voicing, 0.8),
    ])
    trained_result = _trained_modality_result(
        modality="audio",
        features=features,
        feature_vector_fn=audio_feature_vector,
        fallback_confidence=acoustic_confidence,
        notes=(
            "Audio screening used a trained audio model built from labeled clips and backend acoustic "
            "features such as tempo, energy, pitch, and voicing."
        ),
        feature_snapshot={
            "duration": round(features["duration"], 2),
            "tempo": round(features["tempo"], 2),
            "rms": round(features["rms"], 4),
            "voiced_ratio": round(features["voiced_ratio"], 3),
        },
        fallback_domain_scores=domain_scores,
    )
    if trained_result is not None:
        return trained_result

    return _modality_result(
        modality="audio",
        domain_scores=domain_scores,
        confidence=acoustic_confidence,
        notes=(
            "Audio screening looks at tempo, energy, voice continuity, and pitch variability. "
            "Background noise or very short clips can reduce reliability."
        ),
        feature_snapshot={
            "duration": round(features["duration"], 2),
            "tempo": round(features["tempo"], 2),
            "rms": round(features["rms"], 4),
            "voiced_ratio": round(features["voiced_ratio"], 3),
        },
    )


def score_image_features(features: dict) -> dict:
    if not features.get("available"):
        return {**features, "available": False}

    compact_smile = normalize_score((2.2 - features["smile_ratio"]) / 2.2)
    low_eye_openness = normalize_score((0.035 - features["eye_openness"]) / 0.035)

    domain_scores = {
        "depression": 0.2 + 0.75 * compact_smile + 0.2 * low_eye_openness,
        "anxiety": 0.15 + 0.4 * compact_smile + 0.5 * low_eye_openness,
        "stress": 0.2 + 0.45 * compact_smile + 0.55 * low_eye_openness,
        "sleep_disorder": 0.16 + 0.35 * low_eye_openness + 0.25 * compact_smile,
        "burnout": 0.15 + 0.4 * low_eye_openness + 0.35 * compact_smile,
        "loneliness": 0.15 + 0.45 * compact_smile + 0.2 * low_eye_openness,
        "substance_abuse": 0.08 + 0.25 * low_eye_openness + 0.2 * compact_smile,
    }

    trained_result = _trained_modality_result(
        modality="image",
        features=features,
        feature_vector_fn=image_feature_vector,
        fallback_confidence=0.68,
        notes=(
            "Facial-cue screening used a trained image model built from labeled face examples and backend "
            "visual features such as eye openness and smile ratio."
        ),
        feature_snapshot={
            "smile_ratio": round(features["smile_ratio"], 3),
            "eye_openness": round(features["eye_openness"], 4),
            "vision_backend": features.get("vision_backend", "unknown"),
        },
        fallback_domain_scores=domain_scores,
    )
    if trained_result is not None:
        return trained_result

    return _modality_result(
        modality="image",
        domain_scores=domain_scores,
        confidence=0.68,
        notes=(
            "Facial cue screening uses simple face-mesh heuristics. It is the least reliable modality "
            "and should only be treated as supporting context."
        ),
        feature_snapshot={
            "smile_ratio": round(features["smile_ratio"], 3),
            "eye_openness": round(features["eye_openness"], 4),
            "vision_backend": features.get("vision_backend", "unknown"),
        },
    )


def aggregate_scores(results: list) -> dict:
    available = [r for r in results if r.get("available")]
    if not available:
        return {
            **{domain: "unknown" for domain in PREDICTION_DOMAINS},
            "confidence": 0.0,
            "scores": {domain: 0.0 for domain in PREDICTION_DOMAINS},
        }

    weighted_results = []
    for result in available:
        weight = MODALITY_WEIGHTS.get(result["modality"], 0.33) * result["confidence"]
        weighted_results.append((result, weight))

    total_weight = sum(weight for _, weight in weighted_results) or float(len(available))
    raw_scores = {}
    for domain in PREDICTION_DOMAINS:
        score_key = f"{domain}_score"
        raw_scores[domain] = sum(r[score_key] * weight for r, weight in weighted_results) / total_weight

    coverage_score = normalize_score(
        sum(MODALITY_WEIGHTS.get(result["modality"], 0.33) for result in available)
        / sum(MODALITY_WEIGHTS.values())
    )
    weighted_confidence = sum(result["confidence"] * weight for result, weight in weighted_results) / total_weight
    agreement_confidence = _domain_score_agreement(
        [
            {domain: result.get(f"{domain}_score", 0.0) for domain in PREDICTION_DOMAINS}
            for result in available
        ]
    )
    confidence = normalize_score(
        0.55 * weighted_confidence
        + 0.25 * coverage_score
        + 0.20 * agreement_confidence
    )

    result = {
        "confidence": normalize_score(confidence),
        "scores": {domain: normalize_score(score) for domain, score in raw_scores.items()},
    }
    for domain, score in raw_scores.items():
        result[domain] = risk_level(score)
    return result


def build_recommendation(overall: dict) -> str:
    high_risks = [name for name in PREDICTION_DOMAINS if overall[name] == "high"]
    moderate_risks = [name for name in PREDICTION_DOMAINS if overall[name] == "moderate"]

    if high_risks:
        joined = ", ".join(PREDICTION_LABELS[name].lower() for name in high_risks)
        return (
            f"This prototype flagged high {joined} risk. Arrange follow-up with a mental health professional, "
            "psychiatrist, psychologist, or trained community health worker as soon as possible."
        )

    if moderate_risks:
        joined = ", ".join(PREDICTION_LABELS[name].lower() for name in moderate_risks)
        return (
            f"This prototype flagged moderate {joined} risk. A guided follow-up interview, repeat screening, "
            "and supportive check-in from a clinician or community health worker would be appropriate."
        )

    return (
        "Current multimodal signals are low risk, but this remains a prototype screening result rather than "
        "a diagnosis. Re-screen if symptoms persist or functioning worsens."
    )


def screen(text_input: str = "", audio_path: str = None, image_path: str = None) -> dict:
    text_features = extract_text_features(text_input)
    audio_features = extract_audio_features(audio_path)
    image_features = extract_image_features(image_path)

    text_result = score_text_features(text_features)
    audio_result = score_audio_features(audio_features)
    image_result = score_image_features(image_features)

    overall = aggregate_scores([text_result, audio_result, image_result])
    recommendation = build_recommendation(overall)

    return {
        "text": text_result,
        "audio": audio_result,
        "image": image_result,
        "overall": overall,
        "recommendation": recommendation,
        "disclaimer": (
            "This tool is an early-stage screening prototype. It cannot diagnose mental health conditions, "
            "and it should not replace clinical judgment or emergency care."
        ),
    }
