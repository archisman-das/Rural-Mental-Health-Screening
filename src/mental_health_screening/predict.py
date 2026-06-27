import numpy as np

from .constants import PREDICTION_DOMAINS, PREDICTION_LABELS
from .feature_extract import extract_text_features, extract_audio_features, extract_audio_sequence_features, extract_audio_spectrogram_features, extract_image_features, extract_passive_biomarkers
from .model_features import audio_feature_vector, image_feature_vector, text_feature_vector
from .model_store import load_model_bundle
from .utils import average, confidence_weighted_score, normalize_score, risk_level

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import shap
except ImportError:
    shap = None


MODALITY_WEIGHTS = {
    # Keep the display and backend scoring aligned with a clinically stable blend.
    "text": 0.46,
    "audio": 0.30,
    "image": 0.24,
}

ACTIVE_MODALITIES = ("text", "audio", "image")

COMORBIDITY_MODALITIES = ("text", "audio", "image")
COMORBIDITY_MODEL_NAME = "comorbidity"
COMORBIDITY_POSITIVE_THRESHOLD = 0.5
COMORBIDITY_PAIR_PRIORS = {
    ("depression", "anxiety"): 1.35,
    ("depression", "loneliness"): 1.2,
    ("anxiety", "stress"): 1.45,
    ("anxiety", "sleep_disorder"): 1.25,
    ("stress", "burnout"): 1.5,
    ("loneliness", "burnout"): 1.18,
    ("substance_abuse", "stress"): 1.12,
}

SCREENING_MIN_CONFIDENCE_FOR_AUTOMATED_TRIAGE = 0.8
SCREENING_MIN_MODALITIES_FOR_AUTOMATED_TRIAGE = 2

# Weak auxiliary bundles can add noise when they were trained on small or
# poorly performing sets. Keep them out of the final blend unless they clear a
# minimum quality floor.
MIN_BUNDLE_QUALITY = {
    "audio_sequence": 0.35,
    "audio_spectrogram": 0.55,
    "image_dl": 0.55,
    "comorbidity": 0.55,
    "passive_biomarkers": 0.60,
}
MIN_BUNDLE_SAMPLE_COUNT = {
    "audio_sequence": 500,
    "audio_spectrogram": 500,
    "image_dl": 250,
    "comorbidity": 1000,
    "passive_biomarkers": 25,
}

_SHAP_EXPLAINERS: dict[tuple[str, str, int], object] = {}


def _confidence_from_feature_count(feature_count: int, max_count: int) -> float:
    return normalize_score(feature_count / max_count)


def _bundle_quality_score(bundle: dict | None) -> float:
    if not bundle:
        return 0.0
    metrics = dict(bundle.get("metrics", {}) or {})
    candidates = [
        bundle.get("confidence_hint", 0.0),
        metrics.get("macro_f1", 0.0),
        metrics.get("macro_accuracy", 0.0),
        metrics.get("label_accuracy", 0.0),
        metrics.get("exact_match", 0.0),
        metrics.get("accuracy", 0.0),
    ]
    best_score = max(float(value or 0.0) for value in candidates)
    return normalize_score(best_score)


def _bundle_is_trusted(modality: str, bundle: dict | None) -> bool:
    if not bundle:
        return False
    min_quality = float(MIN_BUNDLE_QUALITY.get(modality, 0.5))
    min_samples = int(MIN_BUNDLE_SAMPLE_COUNT.get(modality, 0))
    sample_count = int(bundle.get("sample_count", 0) or 0)
    quality_score = _bundle_quality_score(bundle)
    return quality_score >= min_quality and sample_count >= min_samples


def _confidence_signal_from_std(prediction_std: float, scale: float | None) -> float:
    resolved_scale = float(scale or 1.0)
    if resolved_scale <= 0.0:
        resolved_scale = 1.0
    return normalize_score(1.0 - min(float(prediction_std) / resolved_scale, 1.0))


def _apply_confidence_calibrator(calibrator: dict | None, base_signal: float) -> tuple[float, str]:
    if not calibrator:
        return normalize_score(base_signal), "uncalibrated"

    method = str(calibrator.get("method", "uncalibrated"))
    model = calibrator.get("model")
    if method == "isotonic" and model is not None:
        return normalize_score(float(model.predict([base_signal])[0])), method
    if method == "platt" and model is not None:
        return normalize_score(float(model.predict_proba([[base_signal]])[0][1])), method
    if method == "constant":
        return normalize_score(float(calibrator.get("metrics", {}).get("positive_rate", 0.0))), method
    return normalize_score(base_signal), method


def _predict_calibrated_domain(model, vector: list[float], calibrator: dict | None) -> tuple[float, float, dict]:
    estimators = getattr(model, "estimators_", None)
    if hasattr(model, "predict_proba"):
        raw_proba = np.asarray(model.predict_proba([vector]), dtype=float)[0]
        raw_prediction = float(np.clip(raw_proba[-1], 0.0, 1.0))
        if estimators is not None:
            estimator_rows = []
            for estimator in np.ravel(estimators):
                if hasattr(estimator, "predict_proba"):
                    estimator_rows.append(np.asarray(estimator.predict_proba([vector]), dtype=float)[0, -1])
                else:
                    estimator_rows.append(float(np.asarray(estimator.predict([vector]), dtype=float).reshape(-1)[0]))
            tree_predictions = np.asarray(estimator_rows, dtype=float)
            prediction_std = float(np.clip(tree_predictions.std(), 0.0, 1.0))
        else:
            prediction_std = 0.0
        base_signal = _confidence_signal_from_std(
            prediction_std=prediction_std,
            scale=(calibrator or {}).get("uncertainty_scale"),
        )
    elif estimators is not None:
        tree_predictions = np.asarray(
            [float(estimator.predict([vector])[0]) for estimator in np.ravel(estimators)],
            dtype=float,
        )
        raw_prediction = float(np.clip(tree_predictions.mean(), 0.0, 1.0))
        prediction_std = float(np.clip(tree_predictions.std(), 0.0, 1.0))
        base_signal = _confidence_signal_from_std(
            prediction_std=prediction_std,
            scale=(calibrator or {}).get("uncertainty_scale"),
        )
    else:
        raw_prediction = float(np.clip(model.predict([vector])[0], 0.0, 1.0))
        prediction_std = float((calibrator or {}).get("metrics", {}).get("residual_scale", 0.0) or 0.0)
        if calibrator and str(calibrator.get("method")) == "constant":
            base_signal = normalize_score(float(calibrator.get("metrics", {}).get("positive_rate", 0.0)))
        else:
            base_signal = _confidence_signal_from_std(
                prediction_std=prediction_std,
                scale=(calibrator or {}).get("uncertainty_scale"),
            )
    calibrated_confidence, method = _apply_confidence_calibrator(calibrator, base_signal)
    return raw_prediction, calibrated_confidence, {
        "raw_uncertainty_std": round(prediction_std, 6),
        "base_confidence_signal": round(base_signal, 6),
        "confidence_calibration_method": method,
    }


def _get_shap_explainer(modality: str, domain: str, model):
    if shap is None:
        return None
    cache_key = (modality, domain, id(model))
    if cache_key in _SHAP_EXPLAINERS:
        return _SHAP_EXPLAINERS[cache_key]
    try:
        explainer = shap.TreeExplainer(model)
    except Exception:
        explainer = None
    _SHAP_EXPLAINERS[cache_key] = explainer
    return explainer


def _shape_expected_value(expected_value) -> float:
    if isinstance(expected_value, (list, tuple)):
        return float(np.asarray(expected_value).reshape(-1)[0])
    if isinstance(expected_value, np.ndarray):
        return float(expected_value.reshape(-1)[0])
    return float(expected_value)


def _shap_domain_explanation(
    modality: str,
    domain: str,
    model,
    feature_names: list[str],
    vector: list[float],
    prediction: float,
) -> dict:
    if shap is None:
        return {
            "available": False,
            "method": "shap_unavailable",
            "message": "Install the `shap` package to enable per-domain feature attribution.",
        }

    explainer = _get_shap_explainer(modality, domain, model)
    if explainer is None:
        return {
            "available": False,
            "method": "tree_explainer_failed",
            "message": "The current model could not be explained with SHAP TreeExplainer.",
        }

    try:
        shap_values = explainer.shap_values(np.asarray([vector], dtype=float))
        shap_row = np.asarray(shap_values, dtype=float)
        if shap_row.ndim == 2:
            shap_row = shap_row[0]
        else:
            shap_row = shap_row.reshape(-1)
        expected_value = _shape_expected_value(getattr(explainer, "expected_value", 0.0))
    except Exception:
        return {
            "available": False,
            "method": "shap_inference_failed",
            "message": "SHAP explanation failed for this prediction.",
        }

    contributions = []
    for index, name in enumerate(feature_names):
        contribution = float(shap_row[index]) if index < len(shap_row) else 0.0
        feature_value = float(vector[index]) if index < len(vector) else 0.0
        contributions.append(
            {
                "feature": name,
                "feature_value": round(feature_value, 6),
                "shap_value": round(contribution, 6),
                "direction": "increase" if contribution >= 0 else "decrease",
                "abs_shap": abs(contribution),
            }
        )

    ranked = sorted(contributions, key=lambda item: item["abs_shap"], reverse=True)
    top_contributors = [
        {key: value for key, value in item.items() if key != "abs_shap"}
        for item in ranked[:5]
    ]
    positive = [
        {key: value for key, value in item.items() if key != "abs_shap"}
        for item in ranked if item["shap_value"] > 0
    ][:3]
    negative = [
        {key: value for key, value in item.items() if key != "abs_shap"}
        for item in ranked if item["shap_value"] < 0
    ][:3]

    return {
        "available": True,
        "method": "tree_shap",
        "base_value": round(expected_value, 6),
        "predicted_value": round(float(prediction), 6),
        "top_contributors": top_contributors,
        "top_positive": positive,
        "top_negative": negative,
    }


def _linear_domain_explanation(
    feature_names: list[str],
    vector: list[float],
    model,
    prediction: float,
) -> dict:
    coefficients = np.asarray(getattr(model, "coef_", []), dtype=float).reshape(-1)
    intercept = float(np.asarray(getattr(model, "intercept_", [0.0]), dtype=float).reshape(-1)[0]) if getattr(model, "intercept_", None) is not None else 0.0
    if coefficients.size == 0:
        return {
            "available": False,
            "method": "linear_coefficients_missing",
            "message": "The linear federated model did not expose coefficients for explanation.",
        }
    contributions = []
    for index, name in enumerate(feature_names):
        coefficient = float(coefficients[index]) if index < len(coefficients) else 0.0
        feature_value = float(vector[index]) if index < len(vector) else 0.0
        contribution = coefficient * feature_value
        contributions.append(
            {
                "feature": name,
                "feature_value": round(feature_value, 6),
                "coefficient": round(coefficient, 6),
                "shap_value": round(contribution, 6),
                "direction": "increase" if contribution >= 0 else "decrease",
                "abs_shap": abs(contribution),
            }
        )
    ranked = sorted(contributions, key=lambda item: item["abs_shap"], reverse=True)
    top_contributors = [{key: value for key, value in item.items() if key != "abs_shap"} for item in ranked[:5]]
    positive = [{key: value for key, value in item.items() if key != "abs_shap"} for item in ranked if item["shap_value"] > 0][:3]
    negative = [{key: value for key, value in item.items() if key != "abs_shap"} for item in ranked if item["shap_value"] < 0][:3]
    return {
        "available": True,
        "method": "linear_contributions",
        "base_value": round(intercept, 6),
        "predicted_value": round(float(prediction), 6),
        "top_contributors": top_contributors,
        "top_positive": positive,
        "top_negative": negative,
    }


def _domain_score_agreement(score_sets: list[dict]) -> float:
    agreements = []
    for domain in PREDICTION_DOMAINS:
        values = [normalize_score(scores[domain]) for scores in score_sets if domain in scores]
        if not values:
            continue
        if len(values) == 1:
            agreements.append(0.7)
            continue
        spread = max(values) - min(values)
        agreements.append(1.0 - spread)
    if not agreements:
        return 0.0
    return normalize_score(average(agreements))


def _modality_result(
    modality: str,
    domain_scores: dict,
    notes: str,
    confidence: float,
    feature_snapshot: dict,
    predicted_domains: list[str] | None = None,
    available: bool = True,
) -> dict:
    predicted_domains = list(predicted_domains or [domain for domain in PREDICTION_DOMAINS if domain in domain_scores])
    result = {
        "available": bool(available and predicted_domains),
        "modality": modality,
        "confidence": normalize_score(confidence),
        "notes": notes,
        "features": feature_snapshot,
        "predicted_domains": predicted_domains,
        "missing_domains": [domain for domain in PREDICTION_DOMAINS if domain not in predicted_domains],
    }
    for domain in PREDICTION_DOMAINS:
        raw_value = domain_scores.get(domain)
        result[f"{domain}_score"] = normalize_score(raw_value) if raw_value is not None else 0.0
    return result


def _retune_text_weak_domains(result: dict, features: dict) -> dict:
    adjusted = dict(result)
    scores = {
        domain: normalize_score(float(adjusted.get(f"{domain}_score", 0.0) or 0.0))
        for domain in PREDICTION_DOMAINS
    }
    thresholds = dict(adjusted.get("label_thresholds", {}) or {})
    emotion_scores = dict(features.get("emotion_scores", {}) or {})
    negative_word_count = float(features.get("negative_word_count", 0) or 0)
    distress_phrase_risk = float(features.get("distress_phrase_risk_score", 0.0) or 0.0)
    sentiment_compound = float(features.get("sentiment_compound", 0.0) or 0.0)
    sadness_signal = float(emotion_scores.get("sadness", 0.0) or 0.0)
    loneliness_signal = float(emotion_scores.get("loneliness", 0.0) or 0.0)
    exhaustion_signal = float(emotion_scores.get("exhaustion", 0.0) or 0.0)
    fear_signal = float(emotion_scores.get("fear", 0.0) or 0.0)
    anxiety_keyword_risk = float(features.get("anxiety_keyword_risk_score", 0.0) or 0.0)
    anxiety_keyword_count = float(features.get("anxiety_keyword_count", 0) or 0.0)
    substance_keyword_risk = float(features.get("substance_keyword_risk_score", 0.0) or 0.0)
    substance_keyword_count = float(features.get("substance_keyword_count", 0) or 0.0)
    self_harm_signal = float(features.get("self_harm_risk_score", 0.0) or 0.0)

    negative_signal = normalize_score(min(negative_word_count, 12.0) / 12.0)
    distress_signal = normalize_score(distress_phrase_risk)
    sentiment_negativity = normalize_score(max(0.0, -sentiment_compound))
    sadness_signal = normalize_score(sadness_signal)
    loneliness_signal = normalize_score(loneliness_signal)
    exhaustion_signal = normalize_score(exhaustion_signal)
    fear_signal = normalize_score(fear_signal)
    anxiety_keyword_signal = normalize_score(min(anxiety_keyword_count, 4.0) / 4.0)
    anxiety_signal = normalize_score(0.72 * normalize_score(anxiety_keyword_risk) + 0.28 * anxiety_keyword_signal)
    substance_keyword_signal = normalize_score(min(substance_keyword_count, 4.0) / 4.0)
    substance_signal = normalize_score(0.74 * normalize_score(substance_keyword_risk) + 0.26 * substance_keyword_signal)
    self_harm_signal = normalize_score(self_harm_signal)

    depression_support = normalize_score(
        0.32 * negative_signal
        + 0.26 * distress_signal
        + 0.24 * sentiment_negativity
        + 0.18 * sadness_signal
        + 0.10 * self_harm_signal
    )
    loneliness_support = normalize_score(
        0.24 * negative_signal
        + 0.24 * distress_signal
        + 0.18 * sentiment_negativity
        + 0.28 * loneliness_signal
        + 0.08 * sadness_signal
    )
    anxiety_support = normalize_score(
        0.34 * anxiety_signal
        + 0.24 * sentiment_negativity
        + 0.16 * distress_signal
        + 0.14 * negative_signal
        + 0.12 * sadness_signal
    )
    substance_support = normalize_score(
        0.42 * substance_signal
        + 0.20 * distress_signal
        + 0.16 * negative_signal
        + 0.12 * sentiment_negativity
        + 0.10 * self_harm_signal
    )
    sleep_support = normalize_score(
        0.40 * exhaustion_signal
        + 0.22 * negative_signal
        + 0.18 * distress_signal
        + 0.12 * sentiment_negativity
        + 0.08 * sadness_signal
    )
    stress_support = normalize_score(
        0.34 * fear_signal
        + 0.24 * anxiety_signal
        + 0.18 * distress_signal
        + 0.14 * negative_signal
        + 0.10 * sentiment_negativity
    )

    depression_boost = 0.0
    loneliness_boost = 0.0
    anxiety_boost = 0.0
    substance_boost = 0.0
    sleep_boost = 0.0
    stress_boost = 0.0
    if depression_support > 0.14:
        depression_boost = min(0.16, 0.015 + 0.11 * depression_support)
        scores["depression"] = normalize_score(scores["depression"] + depression_boost)
        thresholds["depression"] = float(min(float(thresholds.get("depression", 0.5)), 0.47))
    if loneliness_support > 0.12:
        loneliness_boost = min(0.15, 0.015 + 0.11 * loneliness_support)
        scores["loneliness"] = normalize_score(scores["loneliness"] + loneliness_boost)
        thresholds["loneliness"] = float(min(float(thresholds.get("loneliness", 0.5)), 0.48))
    if anxiety_support > 0.10:
        anxiety_boost = min(0.14, 0.01 + 0.10 * anxiety_support)
        scores["anxiety"] = normalize_score(scores["anxiety"] + anxiety_boost)
        thresholds["anxiety"] = float(min(float(thresholds.get("anxiety", 0.5)), 0.44))
    if substance_support > 0.10:
        substance_boost = min(0.16, 0.015 + 0.11 * substance_support)
        scores["substance_abuse"] = normalize_score(scores["substance_abuse"] + substance_boost)
        thresholds["substance_abuse"] = float(min(float(thresholds.get("substance_abuse", 0.5)), 0.46))
    if sleep_support > 0.10:
        sleep_boost = min(0.14, 0.01 + 0.10 * sleep_support)
        scores["sleep_disorder"] = normalize_score(scores["sleep_disorder"] + sleep_boost)
        thresholds["sleep_disorder"] = float(min(float(thresholds.get("sleep_disorder", 0.5)), 0.45))
    if stress_support > 0.10:
        stress_boost = min(0.16, 0.015 + 0.11 * stress_support)
        scores["stress"] = normalize_score(scores["stress"] + stress_boost)
        thresholds["stress"] = float(min(float(thresholds.get("stress", 0.5)), 0.44))

    if depression_boost or loneliness_boost or anxiety_boost or substance_boost or sleep_boost or stress_boost:
        adjusted["label_thresholds"] = thresholds
        if "binary_predictions" in adjusted:
            binary_predictions = dict(adjusted.get("binary_predictions", {}) or {})
            binary_predictions["depression"] = bool(scores["depression"] >= float(thresholds.get("depression", 0.5)))
            binary_predictions["loneliness"] = bool(scores["loneliness"] >= float(thresholds.get("loneliness", 0.5)))
            binary_predictions["anxiety"] = bool(scores["anxiety"] >= float(thresholds.get("anxiety", 0.5)))
            binary_predictions["substance_abuse"] = bool(scores["substance_abuse"] >= float(thresholds.get("substance_abuse", 0.5)))
            binary_predictions["sleep_disorder"] = bool(scores["sleep_disorder"] >= float(thresholds.get("sleep_disorder", 0.5)))
            binary_predictions["stress"] = bool(scores["stress"] >= float(thresholds.get("stress", 0.5)))
            adjusted["binary_predictions"] = binary_predictions
            adjusted["predicted_domains"] = [
                domain for domain in PREDICTION_DOMAINS if binary_predictions.get(domain, False)
            ]
        else:
            adjusted["predicted_domains"] = [
                domain for domain in PREDICTION_DOMAINS if scores[domain] >= float(thresholds.get(domain, 0.5))
            ]
        adjusted["missing_domains"] = [domain for domain in PREDICTION_DOMAINS if domain not in adjusted["predicted_domains"]]
        adjusted["available"] = bool(adjusted["predicted_domains"])
        adjusted["depression_score"] = scores["depression"]
        adjusted["loneliness_score"] = scores["loneliness"]
        adjusted["anxiety_score"] = scores["anxiety"]
        adjusted["substance_abuse_score"] = scores["substance_abuse"]
        adjusted["sleep_disorder_score"] = scores["sleep_disorder"]
        adjusted["stress_score"] = scores["stress"]
        adjusted["confidence"] = normalize_score(
            min(
                1.0,
                float(adjusted.get("confidence", 0.0) or 0.0)
                + 0.015 * (depression_boost + loneliness_boost + anxiety_boost + substance_boost + sleep_boost + stress_boost),
            )
        )
        weak_domain_signal = {
            "negative_word_count": round(negative_word_count, 3),
            "distress_phrase_risk_score": round(distress_phrase_risk, 3),
            "sentiment_compound": round(sentiment_compound, 3),
            "sadness_signal": round(sadness_signal, 3),
            "loneliness_signal": round(loneliness_signal, 3),
            "anxiety_keyword_risk_score": round(anxiety_keyword_risk, 3),
            "anxiety_keyword_count": round(anxiety_keyword_count, 3),
            "anxiety_signal": round(anxiety_signal, 3),
            "substance_keyword_risk_score": round(substance_keyword_risk, 3),
            "substance_keyword_count": round(substance_keyword_count, 3),
            "substance_signal": round(substance_signal, 3),
            "exhaustion_signal": round(exhaustion_signal, 3),
            "fear_signal": round(fear_signal, 3),
            "self_harm_risk_score": round(self_harm_signal, 3),
            "depression_boost": round(depression_boost, 3),
            "loneliness_boost": round(loneliness_boost, 3),
            "anxiety_boost": round(anxiety_boost, 3),
            "substance_boost": round(substance_boost, 3),
            "sleep_boost": round(sleep_boost, 3),
            "stress_boost": round(stress_boost, 3),
        }
        features_snapshot = dict(adjusted.get("features", {}) or {})
        features_snapshot.update(weak_domain_signal)
        adjusted["features"] = features_snapshot

    for domain in ("depression", "loneliness", "anxiety", "substance_abuse", "sleep_disorder", "stress"):
        adjusted[f"{domain}_score"] = scores[domain]
    return adjusted


def _modality_quality_signal(result: dict) -> float:
    feature_snapshot = result.get("features", {}) or {}
    metrics = result.get("metrics", {}) or {}
    for candidate in (
        feature_snapshot.get("model_macro_f1"),
        metrics.get("macro_f1"),
        metrics.get("macro_accuracy"),
        feature_snapshot.get("confidence"),
    ):
        if candidate is not None:
            return normalize_score(float(candidate))
    return normalize_score(float(result.get("confidence", 0.0)))


def _effective_modality_weight(result: dict) -> float:
    if result.get("modality") == "passive_biomarkers":
        return 0.0
    base_weight = float(MODALITY_WEIGHTS.get(result.get("modality"), 0.25))
    quality_signal = _modality_quality_signal(result)
    quality_multiplier = 0.7 + 0.3 * quality_signal
    if result.get("modality") == "comorbidity":
        # The comorbidity head is useful, but keep it secondary until it is
        # retrained on stronger upstream modality signals.
        quality_multiplier *= 0.93
    return base_weight * quality_multiplier


def _screening_bundle_metadata(modality: str) -> dict:
    bundle = load_model_bundle(modality)
    if bundle is None:
        return {
            "available": False,
            "trained_at": None,
            "sample_count": 0,
            "metrics": {},
            "model_type": None,
            "model_families": {},
            "source_datasets": [],
            "label_sources": [],
        }

    metrics = dict(bundle.get("metrics", {}) or {})
    return {
        "available": True,
        "trained_at": bundle.get("trained_at"),
        "sample_count": int(bundle.get("sample_count", 0) or 0),
        "metrics": {
            "macro_f1": float(metrics.get("macro_f1", 0.0) or 0.0),
            "macro_accuracy": float(metrics.get("macro_accuracy", 0.0) or 0.0),
            "label_accuracy": float(metrics.get("label_accuracy", 0.0) or 0.0),
            "exact_match": float(metrics.get("exact_match", 0.0) or 0.0),
        },
        "model_type": bundle.get("model_type"),
        "model_families": dict(bundle.get("model_families", {}) or {}),
        "source_datasets": list(bundle.get("source_datasets", [])),
        "label_sources": list(bundle.get("label_sources", [])),
    }


def _screening_governance_snapshot(
    text_result: dict,
    audio_result: dict,
    image_result: dict,
    overall: dict,
    comorbidity: dict | None = None,
) -> dict:
    available_modalities = [
        modality
        for modality, result in (
            ("text", text_result),
            ("audio", audio_result),
            ("image", image_result),
        )
        if result.get("available")
    ]
    confidence = normalize_score(float(overall.get("confidence", 0.0) or 0.0))
    high_risks = [domain for domain in PREDICTION_DOMAINS if overall.get(domain) == "high"]
    moderate_risks = [domain for domain in PREDICTION_DOMAINS if overall.get(domain) == "moderate"]
    comorbidity_confidence = normalize_score(float((comorbidity or {}).get("confidence", 0.0) or 0.0))

    review_required = bool(
        confidence < SCREENING_MIN_CONFIDENCE_FOR_AUTOMATED_TRIAGE
        or len(available_modalities) < SCREENING_MIN_MODALITIES_FOR_AUTOMATED_TRIAGE
        or high_risks
        or moderate_risks
    )
    screening_mode = "human_review_required" if review_required else "screening_only"

    return {
        "screening_mode": screening_mode,
        "review_required": review_required,
        "confidence_threshold": SCREENING_MIN_CONFIDENCE_FOR_AUTOMATED_TRIAGE,
        "minimum_modalities": SCREENING_MIN_MODALITIES_FOR_AUTOMATED_TRIAGE,
        "available_modalities": available_modalities,
        "available_modalities_count": len(available_modalities),
        "risk_flags": {
            "high": high_risks,
            "moderate": moderate_risks,
        },
        "confidence_band": "low" if confidence < 0.55 else "moderate" if confidence < 0.75 else "high",
        "comorbidity_confidence": comorbidity_confidence,
        "bundles": {
            modality: _screening_bundle_metadata(modality)
            for modality in ("text", "audio", "image", "comorbidity")
        },
    }


def _unavailable_modality_result(modality: str, notes: str, feature_snapshot: dict) -> dict:
    return _modality_result(
        modality=modality,
        domain_scores={},
        notes=notes,
        confidence=0.0,
        feature_snapshot=feature_snapshot,
        predicted_domains=[],
        available=False,
    )


def _trained_modality_result(
    modality: str,
    features: dict,
    feature_vector_fn,
    base_confidence: float,
    notes: str,
    feature_snapshot: dict,
    require_label_source: str | None = None,
) -> dict:
    if not features.get("available"):
        return _unavailable_modality_result(
            modality=modality,
            notes=f"{modality.title()} features were unavailable, so no trained classifier could run.",
            feature_snapshot=feature_snapshot,
        )

    bundle = load_model_bundle(modality)
    if bundle is None:
        return _unavailable_modality_result(
            modality=modality,
            notes=f"No trained {modality} model bundle is available yet for backend screening.",
            feature_snapshot={**feature_snapshot, "model_source": "missing_bundle"},
        )

    bundle_label_sources = list(bundle.get("label_sources", []))
    if require_label_source and require_label_source not in bundle_label_sources:
        return _unavailable_modality_result(
            modality=modality,
            notes=(
                f"The available {modality} bundle is present, but it uses alternate label sources, so the "
                "dashboard is showing its bundle metadata instead of using it in the core score."
            ),
            feature_snapshot={
                **feature_snapshot,
                "model_source": "bundle_label_source_mismatch",
                "model_type": bundle.get("model_type"),
                "trained_samples": bundle.get("sample_count", 0),
                "training_strategy": bundle.get("training_strategy", "centralized"),
                "source_datasets": list(bundle.get("source_datasets", [])),
                "label_sources": bundle_label_sources,
                "model_families": dict(bundle.get("model_families", {}) or {}),
                "model_selection": dict(bundle.get("model_selection", {}) or {}),
                "trained_domains": list(bundle.get("domains", [])),
            },
        )

    _, vector = feature_vector_fn(features)
    domain_scores: dict[str, float] = {}
    domain_confidences: dict[str, float] = {}
    domain_uncertainty: dict[str, dict] = {}
    domain_explanations: dict[str, dict] = {}
    trained_domains = []
    confidence_calibrators = bundle.get("confidence_calibrators", {}) or {}
    feature_names = list(bundle.get("feature_names", []))
    label_thresholds = dict(bundle.get("label_thresholds", {}) or {})

    if bundle.get("models"):
        for domain in PREDICTION_DOMAINS:
            model = bundle["models"].get(domain)
            if model is None:
                continue
            prediction, calibrated_domain_confidence, uncertainty_snapshot = _predict_calibrated_domain(
                model=model,
                vector=vector,
                calibrator=confidence_calibrators.get(domain),
            )
            domain_scores[domain] = normalize_score(prediction)
            domain_confidences[domain] = normalize_score(calibrated_domain_confidence)
            domain_uncertainty[domain] = uncertainty_snapshot
            domain_explanations[domain] = _shap_domain_explanation(
                modality=modality,
                domain=domain,
                model=model,
                feature_names=feature_names,
                vector=vector,
                prediction=prediction,
            )
            if not domain_explanations[domain].get("available") and getattr(model, "coef_", None) is not None:
                domain_explanations[domain] = _linear_domain_explanation(
                    feature_names=feature_names,
                    vector=vector,
                    model=model,
                    prediction=prediction,
                )
            trained_domains.append(domain)
        if not trained_domains:
            return _unavailable_modality_result(
                modality=modality,
                notes=f"The trained {modality} bundle did not contain any usable per-domain models.",
                feature_snapshot={**feature_snapshot, "model_source": "empty_trained_bundle"},
            )
    elif bundle.get("model") is not None:
        prediction = bundle["model"].predict([vector])[0]
        domain_scores = {
            domain: normalize_score(prediction[index])
            for index, domain in enumerate(bundle["domains"])
        }
        trained_domains = list(bundle["domains"])
        domain_confidences = {
            domain: normalize_score(float(bundle.get("confidence_hint", base_confidence)))
            for domain in trained_domains
        }
        domain_explanations = {
            domain: {
                "available": False,
                "method": "legacy_bundle_no_shap",
                "message": "This legacy bundle does not expose a per-domain SHAP explanation path.",
            }
            for domain in trained_domains
        }
    else:
        return _unavailable_modality_result(
            modality=modality,
            notes=f"The stored {modality} bundle did not expose any supported model format.",
            feature_snapshot={**feature_snapshot, "model_source": "unsupported_bundle_format"},
        )

    binary_predictions = {
        domain: bool(domain_scores.get(domain, 0.0) >= float(label_thresholds.get(domain, 0.5)))
        for domain in trained_domains
    }
    predicted_domains = [domain for domain, is_positive in binary_predictions.items() if is_positive]

    domain_coverage = normalize_score(len(trained_domains) / max(1, len(PREDICTION_DOMAINS)))
    calibrated_reliability = average(list(domain_confidences.values())) if domain_confidences else 0.0
    confidence = normalize_score(
        0.65 * calibrated_reliability
        + 0.25 * base_confidence
        + 0.10 * domain_coverage
    )
    return _modality_result(
        modality=modality,
        domain_scores=domain_scores,
        confidence=confidence,
        notes=notes,
        predicted_domains=predicted_domains,
        feature_snapshot={
            **feature_snapshot,
            "model_source": "trained_bundle",
            "trained_samples": bundle.get("sample_count", 0),
            "trained_domains": trained_domains,
            "label_thresholds": {domain: round(float(value), 3) for domain, value in label_thresholds.items()},
            "missing_domains": [domain for domain in PREDICTION_DOMAINS if domain not in trained_domains],
            "domain_sample_counts": bundle.get("sample_counts", {}),
            "model_families": dict(bundle.get("model_families", {}) or {}),
            "model_selection": dict(bundle.get("model_selection", {}) or {}),
            "model_macro_accuracy": round(float(bundle.get("metrics", {}).get("macro_accuracy", 0.0)), 3),
            "model_macro_precision": round(float(bundle.get("metrics", {}).get("macro_precision", 0.0)), 3),
            "model_macro_recall": round(float(bundle.get("metrics", {}).get("macro_recall", 0.0)), 3),
            "model_macro_f1": round(float(bundle.get("metrics", {}).get("macro_f1", 0.0)), 3),
            "model_macro_r2": round(float(bundle.get("metrics", {}).get("macro_r2", 0.0)), 3),
            "calibration_quality": round(float(bundle.get("metrics", {}).get("calibration_quality", 0.0)), 3),
            "domain_confidences": {domain: round(value, 3) for domain, value in domain_confidences.items()},
            "domain_uncertainty": domain_uncertainty,
            "domain_explanations": domain_explanations,
            "label_sources": bundle_label_sources,
            "source_datasets": list(bundle.get("source_datasets", [])),
            "training_strategy": bundle.get("training_strategy", "centralized"),
            "federated": bundle.get("federated"),
        },
    )


def score_text_features(features: dict) -> dict:
    if not features.get("available"):
        return {"available": False}

    from .model_store import load_model_bundle
    import torch

    transformer_bundle = load_model_bundle("text_transformer")
    if transformer_bundle is not None and str(transformer_bundle.get("model_type")) == "text_transformer_multilabel":
        raw_text = str(features.get("raw_text", "") or "").strip()
        model = transformer_bundle.get("model")
        tokenizer = transformer_bundle.get("tokenizer")
        if raw_text and model is not None and tokenizer is not None:
            model.eval()
            encoded = tokenizer(
                raw_text,
                truncation=True,
                padding=True,
                max_length=128,
                return_tensors="pt",
            )
            with torch.no_grad():
                logits = model(encoded["input_ids"], encoded["attention_mask"])
                probabilities = torch.sigmoid(logits).cpu().numpy()[0]
            thresholds = dict(transformer_bundle.get("label_thresholds", {}) or {})
            anxiety_keyword_risk = float(features.get("anxiety_keyword_risk_score", 0.0) or 0.0)
            anxiety_keyword_count = int(features.get("anxiety_keyword_count", 0) or 0)
            substance_keyword_risk = float(features.get("substance_keyword_risk_score", 0.0) or 0.0)
            substance_keyword_count = int(features.get("substance_keyword_count", 0) or 0)

            # The transformer is the primary scorer, but we let strong domain keywords
            # nudge the probability upward so obvious anxiety/substance cues are less
            # likely to be missed on short texts.
            if anxiety_keyword_risk > 0.0:
                anxiety_boost = min(0.16, 0.08 * anxiety_keyword_risk + 0.02 * min(anxiety_keyword_count, 4))
                probabilities[PREDICTION_DOMAINS.index("anxiety")] = float(
                    np.clip(probabilities[PREDICTION_DOMAINS.index("anxiety")] + anxiety_boost, 0.0, 1.0)
                )
                thresholds["anxiety"] = float(min(float(thresholds.get("anxiety", 0.5)), 0.42))
            if substance_keyword_risk > 0.0:
                substance_boost = min(0.28, 0.16 * substance_keyword_risk + 0.04 * min(substance_keyword_count, 4))
                probabilities[PREDICTION_DOMAINS.index("substance_abuse")] = float(
                    np.clip(probabilities[PREDICTION_DOMAINS.index("substance_abuse")] + substance_boost, 0.0, 1.0)
                )
                thresholds["substance_abuse"] = float(min(float(thresholds.get("substance_abuse", 0.5)), 0.5))
            binary_predictions = {
                domain: bool(probabilities[index] >= float(thresholds.get(domain, 0.5)))
                for index, domain in enumerate(PREDICTION_DOMAINS)
            }
            predicted_domains = [domain for domain, is_positive in binary_predictions.items() if is_positive]
            text_result = _modality_result(
                modality="text",
                domain_scores={domain: float(probabilities[index]) for index, domain in enumerate(PREDICTION_DOMAINS)},
                notes="Text screening used the transformer-finetuned multilabel classifier.",
                confidence=normalize_score(float(np.mean(probabilities)) if len(probabilities) else 0.0),
                feature_snapshot={
                    "word_count": features.get("word_count", 0),
                    "model_macro_f1": round(float(transformer_bundle.get("metrics", {}).get("macro_f1", 0.0)), 3),
                    "transformer_model": transformer_bundle.get("transformer", {}).get("model_name"),
                    "transformer_family": transformer_bundle.get("transformer", {}).get("model_family"),
                    "transformer_language": transformer_bundle.get("transformer", {}).get("language"),
                    "transformer_available": True,
                },
                predicted_domains=predicted_domains,
                available=bool(predicted_domains),
            )
            text_result.update(
                {
                    "model_type": "text_transformer_multilabel",
                    "binary_predictions": binary_predictions,
                    "label_thresholds": thresholds,
                    "transformer": dict(transformer_bundle.get("transformer", {}) or {}),
                    "metrics": dict(transformer_bundle.get("metrics", {}) or {}),
                }
            )
            return _retune_text_weak_domains(text_result, features)

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
        base_confidence=confidence,
        notes=(
            "Text screening used trained per-domain classifiers supervised with DAIC-WOZ PHQ-derived targets "
            "and backend language features such as sentiment, emotion, safety-language cues, and multilingual "
            "transformer context from English BERT-family models or language-native MuRIL/Indic-BERT for Hindi and Bengali, "
            "including culturally adapted distress idioms per language."
        ),
        feature_snapshot={
            "word_count": features["word_count"],
            "negative_word_count": features["negative_word_count"],
            "positive_word_count": features["positive_word_count"],
            "distress_phrase_count": features.get("distress_phrase_count", 0),
            "distress_phrase_matches": features.get("distress_phrase_matches", []),
            "distress_phrase_detected": features.get("distress_phrase_detected", False),
            "distress_phrase_risk_score": round(features.get("distress_phrase_risk_score", 0.0), 3),
            "agrarian_distress_detected": features.get("agrarian_distress_detected", False),
            "agrarian_distress_matches": features.get("agrarian_distress_matches", []),
            "agrarian_distress_risk_score": round(features.get("agrarian_distress_risk_score", 0.0), 3),
            "crop_failure_detected": features.get("crop_failure_detected", False),
            "crop_failure_matches": features.get("crop_failure_matches", []),
            "crop_failure_risk_score": round(features.get("crop_failure_risk_score", 0.0), 3),
            "debt_distress_detected": features.get("debt_distress_detected", False),
            "debt_distress_matches": features.get("debt_distress_matches", []),
            "debt_distress_risk_score": round(features.get("debt_distress_risk_score", 0.0), 3),
            "food_security_detected": features.get("food_security_detected", False),
            "food_security_matches": features.get("food_security_matches", []),
            "food_security_risk_score": round(features.get("food_security_risk_score", 0.0), 3),
            "sentiment_compound": round(features["sentiment_compound"], 3),
            "sentiment_label": features["sentiment_label"],
            "sentiment_model": features["sentiment_model"],
            "dominant_emotion": features["dominant_emotion"],
            "emotion_model": features["emotion_model"],
            "language": features.get("language", "english"),
            "self_harm_keyword_detected": features["self_harm_keyword_detected"],
            "self_harm_keyword_matches": features["self_harm_keyword_matches"],
            "self_harm_risk_score": round(features["self_harm_risk_score"], 3),
            "transformer_model": features["transformer_model"] or "unavailable",
            "transformer_family": features.get("transformer_family") or "unavailable",
            "transformer_preferred_family": features.get("transformer_preferred_family") or "unavailable",
            "transformer_language": features.get("transformer_language") or features.get("language", "english"),
            "transformer_reason": features.get("transformer_reason"),
        },
        require_label_source="daic_woz_phq_domain_mapping",
    )
    return _retune_text_weak_domains(trained_result, features)


def score_audio_features(features: dict) -> dict:
    if not features.get("available"):
        return {**features, "available": False}

    from .model_store import load_model_bundle
    import torch

    audio_bundle = load_model_bundle("audio")
    sequence_bundle = load_model_bundle("audio_sequence")
    spectrogram_bundle = load_model_bundle("audio_spectrogram")
    audio_path = str(features.get("audio_path", "") or "").strip()
    sequence_macro_f1 = float((sequence_bundle or {}).get("metrics", {}).get("macro_f1", 0.0) or 0.0)
    audio_macro_f1 = float((audio_bundle or {}).get("metrics", {}).get("macro_f1", 0.0) or 0.0)
    spectrogram_macro_f1 = float((spectrogram_bundle or {}).get("metrics", {}).get("macro_f1", 0.0) or 0.0)
    sequence_result = None
    spectrogram_result = None
    if (
        sequence_bundle is not None
        and str(sequence_bundle.get("model_type")) == "audio_bilstm_multilabel"
        and audio_path
        and _bundle_is_trusted("audio_sequence", sequence_bundle)
    ):
        try:
            sequence_config = dict(sequence_bundle.get("sequence_config", {}) or {})
            sequence_features = extract_audio_sequence_features(
                audio_path,
                max_frames=int(sequence_config.get("max_frames", 160)),
                include_mfcc=str(sequence_config.get("feature_mode", "full")).lower() != "fast",
            )
            model = sequence_bundle.get("model")
            if sequence_features.get("available") and model is not None:
                normalization = dict(sequence_bundle.get("sequence_normalization", {}) or {})
                mean = np.asarray(normalization.get("mean", []), dtype=np.float32)
                std = np.asarray(normalization.get("std", []), dtype=np.float32)
                sequence_array = np.asarray(sequence_features["sequence_features"], dtype=np.float32)
                if mean.size == sequence_array.shape[1] and std.size == sequence_array.shape[1]:
                    std = np.where(std < 1e-6, 1.0, std)
                    sequence_array = (sequence_array - mean) / std
                model.eval()
                sequence_tensor = torch.tensor(sequence_array, dtype=torch.float32).unsqueeze(0)
                lengths = torch.tensor([sequence_tensor.shape[1]], dtype=torch.long)
                with torch.no_grad():
                    logits = model(sequence_tensor, lengths)
                    probabilities = torch.sigmoid(logits).cpu().numpy()[0]
                thresholds = dict(sequence_bundle.get("label_thresholds", {}) or {})
                binary_predictions = {
                    domain: bool(probabilities[index] >= float(thresholds.get(domain, 0.5)))
                    for index, domain in enumerate(PREDICTION_DOMAINS)
                }
                predicted_domains = [domain for domain, is_positive in binary_predictions.items() if is_positive]
                sequence_result = {
                    **_modality_result(
                        modality="audio",
                        domain_scores={domain: float(probabilities[index]) for index, domain in enumerate(PREDICTION_DOMAINS)},
                        notes="Audio screening used the chunk-sequence BiLSTM classifier.",
                        confidence=normalize_score(float(np.mean(probabilities)) if len(probabilities) else 0.0),
                        feature_snapshot={
                            "audio_path": audio_path,
                            "duration": round(float(sequence_features.get("duration", 0.0)), 2),
                            "frame_count": int(sequence_features.get("frame_count", 0)),
                            "feature_count": int(sequence_features.get("feature_count", 0)),
                            "sequence_model": sequence_bundle.get("model_type"),
                            "sequence_features": list(sequence_bundle.get("feature_names", [])),
                            "sequence_available": True,
                        },
                        predicted_domains=predicted_domains,
                        available=bool(predicted_domains),
                    ),
                    "model_type": "audio_bilstm_multilabel",
                    "binary_predictions": binary_predictions,
                    "label_thresholds": thresholds,
                    "sequence_config": dict(sequence_bundle.get("sequence_config", {}) or {}),
                    "metrics": dict(sequence_bundle.get("metrics", {}) or {}),
                }
        except Exception:
            sequence_result = None

    if (
        spectrogram_bundle is not None
        and str(spectrogram_bundle.get("model_type")) == "audio_spectrogram_cnn_multilabel"
        and audio_path
        and _bundle_is_trusted("audio_spectrogram", spectrogram_bundle)
    ):
        try:
            spectrogram_config = dict(spectrogram_bundle.get("spectrogram_config", {}) or {})
            spectrogram_features = extract_audio_spectrogram_features(
                audio_path,
                max_frames=int(spectrogram_config.get("max_frames", 128)),
            )
            model = spectrogram_bundle.get("model")
            if spectrogram_features.get("available") and model is not None:
                model.eval()
                spectrogram_array = np.asarray(spectrogram_features["spectrogram"], dtype=np.float32)
                spectrogram_tensor = torch.tensor(spectrogram_array, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
                with torch.no_grad():
                    logits = model(spectrogram_tensor)
                    probabilities = torch.sigmoid(logits).cpu().numpy()[0]
                thresholds = dict(spectrogram_bundle.get("label_thresholds", {}) or {})
                binary_predictions = {
                    domain: bool(probabilities[index] >= float(thresholds.get(domain, 0.5)))
                    for index, domain in enumerate(PREDICTION_DOMAINS)
                }
                predicted_domains = [domain for domain, is_positive in binary_predictions.items() if is_positive]
                spectrogram_result = {
                    **_modality_result(
                        modality="audio",
                        domain_scores={domain: float(probabilities[index]) for index, domain in enumerate(PREDICTION_DOMAINS)},
                        notes="Audio screening used the spectrogram CNN classifier.",
                        confidence=normalize_score(float(np.mean(probabilities)) if len(probabilities) else 0.0),
                        feature_snapshot={
                            "audio_path": audio_path,
                            "duration": round(float(spectrogram_features.get("duration", 0.0)), 2),
                            "spectrogram_shape": list(spectrogram_features.get("shape", (0, 0))),
                            "spectrogram_model": spectrogram_bundle.get("model_type"),
                            "spectrogram_available": True,
                        },
                        predicted_domains=predicted_domains,
                        available=bool(predicted_domains),
                    ),
                    "model_type": "audio_spectrogram_cnn_multilabel",
                    "binary_predictions": binary_predictions,
                    "label_thresholds": thresholds,
                    "spectrogram_config": spectrogram_config,
                    "metrics": dict(spectrogram_bundle.get("metrics", {}) or {}),
                }
        except Exception:
            spectrogram_result = None

    duration_confidence = normalize_score(features["duration"] / 12.0)
    voiced_confidence = normalize_score(features["voiced_ratio"])
    acoustic_confidence = average([
        duration_confidence,
        voiced_confidence,
        1.0 - min(normalize_score(1.0 - features["voiced_ratio"]), 0.8),
    ])
    trained_result = _trained_modality_result(
        modality="audio",
        features=features,
        feature_vector_fn=audio_feature_vector,
        base_confidence=acoustic_confidence,
        notes=(
            "Audio screening used trained per-domain classifiers supervised with DAIC-WOZ PHQ-derived targets "
            "and backend acoustic features such as tempo, energy, pitch, and voicing."
        ),
        feature_snapshot={
            "duration": round(features["duration"], 2),
            "tempo": round(features["tempo"], 2),
            "rms": round(features["rms"], 4),
            "voiced_ratio": round(features["voiced_ratio"], 3),
        },
        require_label_source="daic_woz_phq_domain_mapping",
    )

    # Voice patterns that skew flat, low-energy, and low-variability often carry
    # more depression/loneliness signal than the base acoustic bundle captures.
    pitch_std = float(features.get("pitch_std", 0.0) or 0.0)
    voiced_ratio = float(features.get("voiced_ratio", 0.0) or 0.0)
    tempo = float(features.get("tempo", 0.0) or 0.0)
    rms = float(features.get("rms", 0.0) or 0.0)
    spectral_flatness = float(features.get("spectral_flatness", 0.0) or 0.0)
    low_energy_signal = normalize_score((0.18 - rms) / 0.18)
    flat_voice_signal = normalize_score((0.10 - pitch_std / 500.0) / 0.10)
    low_voicing_signal = normalize_score((0.72 - voiced_ratio) / 0.72)
    slow_tempo_signal = normalize_score((78.0 - tempo) / 78.0)
    dull_timbre_signal = normalize_score((spectral_flatness - 0.12) / 0.28)
    depression_support = normalize_score(
        0.34 * low_energy_signal
        + 0.26 * flat_voice_signal
        + 0.20 * slow_tempo_signal
        + 0.10 * dull_timbre_signal
        + 0.10 * low_voicing_signal
    )
    loneliness_support = normalize_score(
        0.32 * low_voicing_signal
        + 0.24 * low_energy_signal
        + 0.18 * flat_voice_signal
        + 0.16 * slow_tempo_signal
        + 0.10 * dull_timbre_signal
    )
    anxiety_support = normalize_score(
        0.34 * slow_tempo_signal
        + 0.22 * low_voicing_signal
        + 0.20 * flat_voice_signal
        + 0.14 * low_energy_signal
        + 0.10 * dull_timbre_signal
    )
    sleep_support = normalize_score(
        0.38 * low_energy_signal
        + 0.26 * slow_tempo_signal
        + 0.16 * dull_timbre_signal
        + 0.12 * flat_voice_signal
        + 0.08 * low_voicing_signal
    )
    burnout_support = normalize_score(
        0.34 * low_energy_signal
        + 0.24 * dull_timbre_signal
        + 0.18 * slow_tempo_signal
        + 0.14 * flat_voice_signal
        + 0.10 * low_voicing_signal
    )
    mood_signal = max(depression_support, loneliness_support, anxiety_support, sleep_support, burnout_support)
    depression_lift = min(0.18, 0.02 + 0.11 * depression_support)
    loneliness_lift = min(0.16, 0.02 + 0.10 * loneliness_support)
    anxiety_lift = min(0.12, 0.015 + 0.085 * anxiety_support)
    sleep_lift = min(0.10, 0.015 + 0.08 * sleep_support)
    burnout_lift = min(0.16, 0.02 + 0.10 * burnout_support)
    for domain, lift in (
        ("depression", depression_lift),
        ("loneliness", loneliness_lift),
        ("anxiety", anxiety_lift),
        ("sleep_disorder", sleep_lift),
        ("burnout", burnout_lift),
    ):
        if lift > 0.0:
            trained_result[f"{domain}_score"] = float(np.clip(float(trained_result.get(f"{domain}_score", 0.0)) + lift, 0.0, 1.0))
            if "domain_scores" in trained_result:
                trained_result["domain_scores"][domain] = trained_result[f"{domain}_score"]
            if "scores" in trained_result:
                trained_result["scores"][domain] = trained_result[f"{domain}_score"]
    thresholds = dict(trained_result.get("label_thresholds", {}) or {})
    if depression_support > 0.12:
        thresholds["depression"] = float(min(float(thresholds.get("depression", 0.5)), 0.46))
    if loneliness_support > 0.11:
        thresholds["loneliness"] = float(min(float(thresholds.get("loneliness", 0.5)), 0.47))
    if anxiety_support > 0.10:
        thresholds["anxiety"] = float(min(float(thresholds.get("anxiety", 0.5)), 0.45))
    if sleep_support > 0.10:
        thresholds["sleep_disorder"] = float(min(float(thresholds.get("sleep_disorder", 0.5)), 0.46))
    if burnout_support > 0.10:
        thresholds["burnout"] = float(min(float(thresholds.get("burnout", 0.5)), 0.44))
    if thresholds:
        trained_result["label_thresholds"] = thresholds
        trained_result["binary_predictions"] = {
            domain: bool(trained_result.get(f"{domain}_score", 0.0) >= float(thresholds.get(domain, 0.5)))
            for domain in PREDICTION_DOMAINS
        }
        trained_result["predicted_domains"] = [
            domain for domain in PREDICTION_DOMAINS if trained_result["binary_predictions"].get(domain, False)
        ]
        trained_result["available"] = bool(trained_result["predicted_domains"])
        trained_result["missing_domains"] = [domain for domain in PREDICTION_DOMAINS if domain not in trained_result["predicted_domains"]]
        features.setdefault("audio_mood_support", {})
        features["audio_mood_support"].update(
            {
                "depression_support": round(depression_support, 3),
                "loneliness_support": round(loneliness_support, 3),
                "anxiety_support": round(anxiety_support, 3),
                "sleep_support": round(sleep_support, 3),
                "burnout_support": round(burnout_support, 3),
                "mood_signal": round(mood_signal, 3),
            }
        )

    candidate_results: list[tuple[str, dict, float]] = [("audio", trained_result, audio_macro_f1)]
    if sequence_result is not None and sequence_result.get("available"):
        candidate_results.append(("audio_sequence", sequence_result, sequence_macro_f1))
    if spectrogram_result is not None and spectrogram_result.get("available"):
        candidate_results.append(("audio_spectrogram", spectrogram_result, spectrogram_macro_f1))

    if len(candidate_results) == 1:
        trained_result["notes"] = (
            "Audio screening used the main acoustic bundle; weak auxiliary audio bundles were excluded "
            "because their saved quality was below the trust threshold."
        )
        return trained_result

    weights = [max(score, 0.05) for _, _, score in candidate_results]
    if len(candidate_results) >= 2:
        # Keep the main audio bundle in front; the auxiliary models stay
        # secondary signals unless they clearly outperform it.
        weights[0] = max(weights[0] * 1.25, 0.05)
        for index in range(1, len(weights)):
            weights[index] = max(weights[index] * 0.78, 0.05)
        if len(candidate_results) == 3:
            # Favor the spectrogram branch slightly over the sequence branch.
            weights[2] = max(weights[2] * 1.05, weights[1] * 0.95, 0.05)
    total_weight = float(sum(weights)) or 1.0
    normalized_weights = [weight / total_weight for weight in weights]

    blended_scores = {
        domain: float(
            np.clip(
                sum(
                    weight * float(result.get(f"{domain}_score", 0.0) or 0.0)
                    for weight, (_, result, _) in zip(normalized_weights, candidate_results, strict=False)
                ),
                0.0,
                1.0,
            )
        )
        for domain in PREDICTION_DOMAINS
    }
    thresholds = dict(trained_result.get("label_thresholds", {}) or {})
    binary_predictions = {
        domain: bool(blended_scores[domain] >= float(thresholds.get(domain, 0.5)))
        for domain in PREDICTION_DOMAINS
    }
    predicted_domains = [domain for domain, is_positive in binary_predictions.items() if is_positive]
    blended_confidence = normalize_score(
        sum(
            weight * float(result.get("confidence", 0.0) or 0.0)
            for weight, (_, result, _) in zip(normalized_weights, candidate_results, strict=False)
        )
    )
    ensemble_features = {
        name: {
            "weight": round(float(weight), 3),
            "available": bool(result.get("available")),
            "confidence": round(float(result.get("confidence", 0.0) or 0.0), 3),
        }
        for weight, (name, result, _) in zip(normalized_weights, candidate_results, strict=False)
    }
    features_snapshot = {
        **dict(trained_result.get("features", {}) or {}),
        "audio_ensemble": ensemble_features,
    }
    if sequence_result is not None and sequence_result.get("available"):
        features_snapshot["audio_sequence_ensemble"] = dict(sequence_result.get("features", {}) or {})
    if spectrogram_result is not None and spectrogram_result.get("available"):
        features_snapshot["audio_spectrogram_ensemble"] = dict(spectrogram_result.get("features", {}) or {})
    features_snapshot["audio_primary_model"] = "audio"
    features_snapshot["audio_auxiliary_bundles"] = {
        "audio_sequence_trusted": bool(sequence_result is not None and sequence_result.get("available")),
        "audio_spectrogram_trusted": bool(spectrogram_result is not None and spectrogram_result.get("available")),
        "audio_sequence_quality": round(_bundle_quality_score(sequence_bundle), 3),
        "audio_spectrogram_quality": round(_bundle_quality_score(spectrogram_bundle), 3),
    }
    return {
        **trained_result,
        "confidence": blended_confidence,
        "predicted_domains": predicted_domains,
        "available": bool(predicted_domains),
        "binary_predictions": binary_predictions,
        "domain_scores": blended_scores,
        "scores": blended_scores,
        **{f"{domain}_score": blended_scores[domain] for domain in PREDICTION_DOMAINS},
        "features": features_snapshot,
        "notes": "Audio screening blended the main acoustic classifier with trusted auxiliary sequence and spectrogram models.",
    }


def score_image_features(features: dict) -> dict:
    feature_snapshot = {
        "smile_ratio": round(features.get("smile_ratio", 0.0), 3),
        "eye_openness": round(features.get("eye_openness", 0.0), 4),
        "vision_backend": features.get("vision_backend", "unknown"),
        "image_path": features.get("image_path"),
    }
    image_bundle = load_model_bundle("image")
    image_dl_bundle = load_model_bundle("image_dl")
    image_path = str(features.get("image_path", "") or "").strip()
    image_dl_trusted = _bundle_is_trusted("image_dl", image_dl_bundle)

    classical_result = None
    if features.get("available"):
        image_confidence = average([
            normalize_score(float(features.get("smile_ratio", 0.0)) / 2.5),
            normalize_score(float(features.get("eye_openness", 0.0)) / 0.05),
            normalize_score(float(features.get("face_width", 0.0)) / max(float(features.get("face_height", 1.0) or 1.0), 1.0)),
        ])
        classical_result = _trained_modality_result(
            modality="image",
            features=features,
            feature_vector_fn=image_feature_vector,
            base_confidence=image_confidence,
            notes=(
                "Image screening used the trained face bundle built from RAVDESS proxy labels and face-derived "
                "features such as smile ratio and eye openness."
            ),
            feature_snapshot=feature_snapshot,
        )
        if image_bundle is None:
            classical_result["notes"] = "Image screening used face-derived heuristics because the trained image bundle was unavailable."

    dl_result = None
    if (
        image_dl_bundle is not None
        and str(image_dl_bundle.get("model_type")) == "image_cnn_multilabel"
        and image_path
        and cv2 is not None
        and image_dl_trusted
    ):
        image_config = dict(image_dl_bundle.get("image_config", {}) or {})
        image_size = int(image_config.get("image_size", 128))
        raw_image = cv2.imread(image_path)
        if raw_image is not None:
            raw_image = cv2.cvtColor(raw_image, cv2.COLOR_BGR2RGB)
            raw_image = cv2.resize(raw_image, (image_size, image_size), interpolation=cv2.INTER_AREA)
            image_tensor = (raw_image.astype(np.float32) / 255.0).transpose(2, 0, 1)
            model = image_dl_bundle.get("model")
            if model is not None:
                import torch

                model.eval()
                image_views = [image_tensor]
                image_views.append(np.flip(image_tensor, axis=2).copy())
                with torch.no_grad():
                    view_probs = []
                    for view in image_views:
                        logits = model(torch.tensor(view, dtype=torch.float32).unsqueeze(0))
                        view_probs.append(torch.sigmoid(logits).cpu().numpy()[0])
                    probabilities = np.mean(np.asarray(view_probs, dtype=np.float32), axis=0)
                thresholds = dict(image_dl_bundle.get("label_thresholds", {}) or {})
                binary_predictions = {
                    domain: bool(probabilities[index] >= float(thresholds.get(domain, 0.5)))
                    for index, domain in enumerate(PREDICTION_DOMAINS)
                }
                predicted_domains = [domain for domain, is_positive in binary_predictions.items() if is_positive]
                dl_result = {
                    **_modality_result(
                        modality="image",
                        domain_scores={domain: float(probabilities[index]) for index, domain in enumerate(PREDICTION_DOMAINS)},
                        notes="Image screening used the image CNN classifier.",
                        confidence=normalize_score(float(np.mean(probabilities)) if len(probabilities) else 0.0),
                        feature_snapshot={
                            **feature_snapshot,
                            "image_size": image_size,
                            "image_model": image_dl_bundle.get("model_type"),
                            "image_available": True,
                        },
                        predicted_domains=predicted_domains,
                        available=bool(predicted_domains),
                    ),
                    "model_type": "image_cnn_multilabel",
                    "binary_predictions": binary_predictions,
                    "label_thresholds": thresholds,
                    "image_config": image_config,
                    "metrics": dict(image_dl_bundle.get("metrics", {}) or {}),
                }

    if classical_result is None and dl_result is None:
        return _unavailable_modality_result(
            modality="image",
            notes="Image features were unavailable or the image CNN bundle did not clear the quality floor.",
            feature_snapshot=feature_snapshot,
        )
    if classical_result is None:
        return dl_result
    if dl_result is None:
        return classical_result

    candidate_results: list[tuple[str, dict, float]] = [
        ("image", classical_result, float((image_bundle or {}).get("metrics", {}).get("macro_f1", 0.0) or 0.0)),
        ("image_dl", dl_result, float((image_dl_bundle or {}).get("metrics", {}).get("macro_f1", 0.0) or 0.0)),
    ]
    weights = [max(score, 0.05) for _, _, score in candidate_results]
    if len(candidate_results) == 2 and dl_result is not None:
        classical_weight, dl_weight = weights
        # Let the DL model lead while preserving the classical bundle as a
        # stabilizer when both are available.
        weights[0] = max(classical_weight * 0.92, 0.05)
        weights[1] = max(dl_weight * 1.18, classical_weight * 1.10, 0.05)
    total_weight = float(sum(weights)) or 1.0
    normalized_weights = [weight / total_weight for weight in weights]
    blended_scores = {
        domain: float(
            np.clip(
                sum(
                    weight * float(result.get(f"{domain}_score", 0.0) or 0.0)
                    for weight, (_, result, _) in zip(normalized_weights, candidate_results, strict=False)
                ),
                0.0,
                1.0,
            )
        )
        for domain in PREDICTION_DOMAINS
    }
    thresholds = dict(classical_result.get("label_thresholds", {}) or {})
    binary_predictions = {
        domain: bool(blended_scores[domain] >= float(thresholds.get(domain, 0.5)))
        for domain in PREDICTION_DOMAINS
    }
    predicted_domains = [domain for domain, is_positive in binary_predictions.items() if is_positive]
    blended_confidence = normalize_score(
        sum(
            weight * float(result.get("confidence", 0.0) or 0.0)
            for weight, (_, result, _) in zip(normalized_weights, candidate_results, strict=False)
        )
    )
    features_snapshot = {
        **feature_snapshot,
        "image_ensemble": {
            name: {
                "weight": round(float(weight), 3),
                "available": bool(result.get("available")),
                "confidence": round(float(result.get("confidence", 0.0) or 0.0), 3),
            }
            for weight, (name, result, _) in zip(normalized_weights, candidate_results, strict=False)
        },
    }
    features_snapshot["image_primary_model"] = "image_dl" if dl_result is not None else "image"
    features_snapshot["image_dl_trusted"] = bool(image_dl_trusted and dl_result is not None)
    features_snapshot["image_dl_quality"] = round(_bundle_quality_score(image_dl_bundle), 3)
    return {
        **classical_result,
        "confidence": blended_confidence,
        "predicted_domains": predicted_domains,
        "available": bool(predicted_domains),
        "binary_predictions": binary_predictions,
        "domain_scores": blended_scores,
        "scores": blended_scores,
        **{f"{domain}_score": blended_scores[domain] for domain in PREDICTION_DOMAINS},
        "features": features_snapshot,
        "notes": "Image screening blended the classical face bundle with the image CNN only when the CNN bundle cleared the quality floor.",
    }


def _passive_feature_vector(features: dict) -> tuple[list[str], list[float]]:
    rppg = dict(features.get("rppg", {}) or {})
    typing = dict(features.get("typing", {}) or {})
    feature_names = [
        "confidence",
        "heart_rate_bpm",
        "heart_rate_score",
        "signal_quality",
        "typing_speed_cpm",
        "typing_pause_ratio",
        "typing_backspace_ratio",
        "typing_rhythm_score",
        "rppg_available",
        "typing_available",
    ]
    vector = [
        float(features.get("confidence", 0.0) or 0.0),
        float(features.get("heart_rate_bpm", 0.0) or 0.0),
        float(rppg.get("heart_rate_score", features.get("heart_rate_score", 0.0)) or 0.0),
        float(rppg.get("signal_quality", features.get("signal_quality", 0.0)) or 0.0),
        float(features.get("typing_speed_cpm", 0.0) or 0.0),
        float(features.get("typing_pause_ratio", 0.0) or 0.0),
        float(features.get("typing_backspace_ratio", 0.0) or 0.0),
        float(typing.get("rhythm_score", features.get("typing_rhythm_score", 0.0)) or 0.0),
        1.0 if rppg.get("available") else 0.0,
        1.0 if typing.get("available") else 0.0,
    ]
    return feature_names, vector


def score_passive_biomarkers(features: dict) -> dict:
    feature_snapshot = {
        "available": bool(features.get("available")),
        "reason": features.get("reason"),
        "confidence": round(float(features.get("confidence", 0.0)), 3),
        "heart_rate_bpm": features.get("heart_rate_bpm"),
        "typing_speed_cpm": features.get("typing_speed_cpm"),
        "typing_pause_ratio": features.get("typing_pause_ratio"),
        "typing_backspace_ratio": features.get("typing_backspace_ratio"),
        "rppg": features.get("rppg", {}),
        "typing": features.get("typing", {}),
    }
    if not features.get("available"):
        return _unavailable_modality_result(
            modality="passive_biomarkers",
            notes=(
                "Passive biomarkers were unavailable, so no zero-hardware inference could run from phone camera "
                "or typing rhythm signals."
            ),
            feature_snapshot=feature_snapshot,
        )

    passive_bundle = load_model_bundle("passive_biomarkers")
    passive_bundle_trusted = bool(passive_bundle is not None and _bundle_is_trusted("passive_biomarkers", passive_bundle))
    if passive_bundle_trusted and passive_bundle.get("models"):
        feature_names, vector = _passive_feature_vector(features)
        per_domain_scores = {}
        binary_predictions = {}
        predicted_domains = []
        confidence_inputs = []
        thresholds = dict(passive_bundle.get("label_thresholds", {}) or {})
        calibrators = dict(passive_bundle.get("confidence_calibrators", {}) or {})
        for domain in PREDICTION_DOMAINS:
            model = (passive_bundle.get("models") or {}).get(domain)
            if model is None:
                continue
            raw_probability, calibrated_confidence, _ = _predict_calibrated_domain(
                model,
                vector,
                calibrators.get(domain),
            )
            per_domain_scores[domain] = normalize_score(raw_probability)
            binary_predictions[domain] = bool(per_domain_scores[domain] >= float(thresholds.get(domain, 0.5)))
            if binary_predictions[domain]:
                predicted_domains.append(domain)
            confidence_inputs.append(float(calibrated_confidence or 0.0))
        if per_domain_scores:
            confidence = normalize_score(
                average([
                    float(passive_bundle.get("confidence_hint", 0.0) or 0.0),
                    average(confidence_inputs) if confidence_inputs else 0.0,
                ])
            )
            feature_snapshot.update(
                {
                    "bundle_feature_names": feature_names,
                    "bundle_model_source": passive_bundle.get("training_strategy", "trained_bundle"),
                    "bundle_quality": round(_bundle_quality_score(passive_bundle), 3),
                }
            )
            return _modality_result(
                modality="passive_biomarkers",
                domain_scores=per_domain_scores,
                confidence=confidence,
                notes="Passive biomarkers used the trained passive bundle from saved assessment data.",
                feature_snapshot=feature_snapshot,
                predicted_domains=predicted_domains,
                available=bool(predicted_domains),
            )

    heart_rate_bpm = float(features.get("heart_rate_bpm") or 0.0)
    typing_speed_cpm = float(features.get("typing_speed_cpm") or 0.0)
    typing_pause_ratio = float(features.get("typing_pause_ratio") or 0.0)
    typing_backspace_ratio = float(features.get("typing_backspace_ratio") or 0.0)

    heart_rate_signal = normalize_score((heart_rate_bpm - 58.0) / 42.0) if heart_rate_bpm > 0 else 0.5
    typing_signal = normalize_score(
        0.45 * normalize_score(typing_pause_ratio)
        + 0.35 * normalize_score(typing_backspace_ratio)
        + 0.20 * normalize_score((typing_speed_cpm - 180.0) / 220.0)
    )
    confidence = normalize_score(float(features.get("confidence", 0.0)))
    if not confidence:
        confidence = average([
            float(features.get("rppg", {}).get("signal_quality", 0.0)),
            float(features.get("typing", {}).get("rhythm_score", 0.0)),
        ])

    rppg_quality = float(features.get("rppg", {}).get("signal_quality", 0.0) or 0.0)
    typing_quality = float(features.get("typing", {}).get("rhythm_score", 0.0) or 0.0)
    if confidence < 0.45 or max(rppg_quality, typing_quality) < 0.35:
        return _unavailable_modality_result(
            modality="passive_biomarkers",
            notes=(
                "Passive biomarker data reached the backend, but the signal quality was too weak to use it "
                "for scoring, so it stayed as metadata only."
            ),
            feature_snapshot=feature_snapshot,
        )

    return _modality_result(
        modality="passive_biomarkers",
        domain_scores={
            "anxiety": normalize_score(0.6 * heart_rate_signal + 0.4 * typing_signal),
            "stress": normalize_score(0.5 * heart_rate_signal + 0.5 * typing_signal),
            "burnout": normalize_score(0.3 * heart_rate_signal + 0.7 * typing_signal),
        },
        confidence=confidence,
        notes=(
            "Passive biomarkers combined phone-camera rPPG-style heart-rate estimation with typing rhythm "
            "signals to provide a zero-hardware adjunct anxiety and stress signal."
        ),
        feature_snapshot=feature_snapshot,
        predicted_domains=["anxiety", "stress", "burnout"],
    )


def aggregate_scores(results: list) -> dict:
    available = [r for r in results if r.get("available") and r.get("modality") in ACTIVE_MODALITIES]
    if not available:
        return {
            **{domain: "unknown" for domain in PREDICTION_DOMAINS},
            "confidence": 0.0,
            "evidence_strength": 0.0,
            "scores": {domain: 0.0 for domain in PREDICTION_DOMAINS},
        }

    weighted_results = []
    for result in available:
        weight = _effective_modality_weight(result)
        weighted_results.append((result, weight))

    total_weight = sum(weight for _, weight in weighted_results) or float(len(available))
    raw_scores = {}
    for domain in PREDICTION_DOMAINS:
        domain_results = [
            (result, weight)
            for result, weight in weighted_results
            if domain in result.get("predicted_domains", [])
        ]
        if not domain_results:
            raw_scores[domain] = None
            continue
        domain_total_weight = sum(weight for _, weight in domain_results) or float(len(domain_results))
        score_key = f"{domain}_score"
        raw_scores[domain] = sum(result[score_key] * weight for result, weight in domain_results) / domain_total_weight

    coverage_score = normalize_score(
        sum(MODALITY_WEIGHTS.get(result["modality"], 0.25) for result in available)
        / sum(MODALITY_WEIGHTS.values())
    )
    modality_count_score = normalize_score(len(available) / float(len(ACTIVE_MODALITIES)))
    weighted_confidence = sum(result["confidence"] * weight for result, weight in weighted_results) / total_weight
    agreement_confidence = _domain_score_agreement(
        [
            {
                domain: result.get(f"{domain}_score", 0.0)
                for domain in result.get("predicted_domains", [])
            }
            for result in available
        ]
    )
    confidence = normalize_score(
        0.48 * weighted_confidence
        + 0.16 * coverage_score
        + 0.10 * modality_count_score
        + 0.26 * agreement_confidence
    )
    evidence_strength = normalize_score(
        0.86 * confidence + 0.14 * max(coverage_score, modality_count_score)
    )

    result = {
        "confidence": evidence_strength,
        "evidence_strength": evidence_strength,
        "scores": {
            domain: confidence_weighted_score(score, evidence_strength) if score is not None else 0.0
            for domain, score in raw_scores.items()
        },
    }
    for domain, score in raw_scores.items():
        adjusted_score = result["scores"].get(domain, 0.0)
        result[domain] = "unknown" if score is None else risk_level(adjusted_score)
    return result


def _comorbidity_feature_names() -> list[str]:
    feature_names: list[str] = []
    for modality in COMORBIDITY_MODALITIES:
        feature_names.extend(
            [
                f"{modality}_available",
                f"{modality}_confidence",
            ]
        )
        feature_names.extend([f"{modality}_{domain}_score" for domain in PREDICTION_DOMAINS])
    feature_names.append("available_modalities_count")
    return feature_names


def _comorbidity_feature_vector(modality_results: dict[str, dict]) -> tuple[list[str], list[float]]:
    vector: list[float] = []
    available_modalities = 0.0
    for modality in COMORBIDITY_MODALITIES:
        result = modality_results.get(modality) or {}
        available = 1.0 if result.get("available") else 0.0
        confidence = normalize_score(result.get("confidence", 0.0))
        vector.extend([available, confidence])
        if available:
            available_modalities += 1.0
        for domain in PREDICTION_DOMAINS:
            vector.append(normalize_score(result.get(f"{domain}_score", 0.0)))
    vector.append(available_modalities)
    return _comorbidity_feature_names(), vector


def _pair_key(domain_a: str, domain_b: str) -> str:
    left, right = sorted((domain_a, domain_b))
    return f"{left}|{right}"


def _comorbidity_pairwise_summary(probabilities: dict[str, float], pairwise_lift: dict | None = None) -> list[dict]:
    pairwise_lift = pairwise_lift or {}
    scored_pairs: list[dict] = []
    for index, domain_a in enumerate(PREDICTION_DOMAINS):
        for domain_b in PREDICTION_DOMAINS[index + 1 :]:
            lift = float(pairwise_lift.get(_pair_key(domain_a, domain_b), 1.0) or 1.0)
            base_joint = float(probabilities.get(domain_a, 0.0)) * float(probabilities.get(domain_b, 0.0))
            joint_probability = normalize_score(base_joint * lift)
            scored_pairs.append(
                {
                    "domains": [domain_a, domain_b],
                    "probability": round(joint_probability, 6),
                    "lift": round(lift, 6),
                    "base_probability": round(base_joint, 6),
                }
            )
    scored_pairs.sort(key=lambda item: (item["probability"], item["lift"]), reverse=True)
    return scored_pairs[:5]


def _heuristic_comorbidity_result(overall: dict) -> dict:
    probabilities = {
        domain: normalize_score(float(overall.get("scores", {}).get(domain, 0.0) or 0.0))
        for domain in PREDICTION_DOMAINS
    }
    pairwise = _comorbidity_pairwise_summary(probabilities, COMORBIDITY_PAIR_PRIORS)
    confidence = normalize_score(
        0.45 * max(probabilities.values(), default=0.0)
        + 0.25 * average(list(probabilities.values()) or [0.0])
        + 0.20 * (pairwise[0]["probability"] if pairwise else 0.0)
        + 0.10 * 0.65
    )
    binary_predictions = {
        domain: probabilities[domain] >= COMORBIDITY_POSITIVE_THRESHOLD
        for domain in PREDICTION_DOMAINS
    }
    positive_domains = [domain for domain, value in binary_predictions.items() if value]
    dominant_pair = pairwise[0] if pairwise else None
    return {
        "available": bool(positive_domains),
        "model_type": "heuristic_joint_risk",
        "probabilities": probabilities,
        "predicted_domains": positive_domains,
        "binary_predictions": binary_predictions,
        "confidence": confidence,
        "top_pairs": pairwise,
        "dominant_pair": dominant_pair,
        "notes": "Joint comorbidity estimates were derived from the aggregated multimodal domain scores because no trained comorbidity bundle was available.",
    }


def _predict_chain_domain_probabilities(chain_spec: dict, vector: list[float]) -> dict[str, float]:
    probabilities: dict[str, float] = {}
    chained_inputs: list[float] = []
    for model_spec in chain_spec.get("models", []):
        domain = model_spec.get("domain")
        if not domain:
            continue
        model = model_spec.get("model")
        constant_probability = model_spec.get("constant_probability")
        if constant_probability is not None:
            probability = float(constant_probability)
        else:
            augmented = np.asarray([vector + chained_inputs], dtype=float)
            if hasattr(model, "predict_proba"):
                probability = float(model.predict_proba(augmented)[0][1])
            else:
                prediction = model.predict(augmented)[0]
                probability = float(np.clip(prediction, 0.0, 1.0))
        probability = float(np.clip(probability, 0.0, 1.0))
        probabilities[str(domain)] = probability
        chained_inputs.append(probability)
    return probabilities


def _apply_comorbidity_probability_calibrator(calibrator: dict | None, score: float) -> tuple[float, str]:
    if not calibrator:
        return float(np.clip(score, 0.0, 1.0)), "uncalibrated"

    method = str(calibrator.get("method", "constant"))
    model = calibrator.get("model")
    if method == "isotonic" and model is not None:
        calibrated = float(model.predict([score])[0])
    elif method == "platt" and model is not None:
        calibrated = float(model.predict_proba([[score]])[0][1])
    else:
        calibrated = float(calibrator.get("positive_rate", 0.0))
    return float(np.clip(calibrated, 0.0, 1.0)), method


def _comorbidity_upstream_blend(modality_results: dict[str, dict]) -> tuple[dict[str, float], float]:
    blended_scores: dict[str, float] = {}
    modality_weights: dict[str, float] = {}

    for modality in ("text", "audio", "image"):
        result = modality_results.get(modality) or {}
        if not result.get("available"):
            continue
        quality = _modality_quality_signal(result)
        effective_weight = max(_effective_modality_weight(result) * (0.75 + 0.25 * quality), 0.01)
        modality_weights[modality] = effective_weight

    for domain in PREDICTION_DOMAINS:
        values = []
        for modality in ("text", "audio", "image"):
            result = modality_results.get(modality) or {}
            if not result.get("available"):
                continue
            score = float(result.get(f"{domain}_score", 0.0) or 0.0)
            if score <= 0.0:
                continue
            values.append((score, modality_weights.get(modality, 0.01)))

        if not values:
            blended_scores[domain] = 0.0
            continue

        total_weight = float(sum(weight for _, weight in values)) or 1.0
        weighted_mean = float(sum(score * weight for score, weight in values) / total_weight)
        weighted_peak = float(max(score for score, _ in values))
        blended_scores[domain] = normalize_score(0.7 * weighted_mean + 0.3 * weighted_peak)

    consensus_strength = normalize_score(
        0.55 * average(list(modality_weights.values()) or [0.0])
        + 0.45 * normalize_score(float(len(modality_weights)) / 3.0)
    )
    return blended_scores, consensus_strength


def _score_comorbidity_from_bundle(modality_results: dict[str, dict]) -> dict | None:
    bundle = load_model_bundle(COMORBIDITY_MODEL_NAME)
    if bundle is None:
        return None
    if not _bundle_is_trusted(COMORBIDITY_MODEL_NAME, bundle):
        return None

    feature_names, vector = _comorbidity_feature_vector(modality_results)
    raw_chain_ensemble = list(bundle.get("chain_ensemble") or [])
    if raw_chain_ensemble:
        chain_ensemble = raw_chain_ensemble
    else:
        legacy_models = list(bundle.get("models", []))
        if legacy_models and isinstance(legacy_models[0], dict) and "models" not in legacy_models[0]:
            chain_ensemble = [
                {
                    "chain_order": list(bundle.get("chain_order", PREDICTION_DOMAINS)),
                    "models": legacy_models,
                }
            ]
        else:
            chain_ensemble = legacy_models
    if not chain_ensemble:
        return None

    thresholds = dict(bundle.get("label_thresholds", {}))
    probability_calibrators = dict(bundle.get("probability_calibrators", {}) or {})
    pairwise_lift = dict(bundle.get("pairwise_lift", {}))
    ensemble_size = int(bundle.get("ensemble_size") or len(chain_ensemble) or 1)
    upstream_blend, upstream_consensus = _comorbidity_upstream_blend(modality_results)

    per_chain_probabilities: list[dict[str, float]] = []
    for chain_spec in chain_ensemble:
        chain_probabilities = _predict_chain_domain_probabilities(chain_spec, vector)
        if chain_probabilities:
            per_chain_probabilities.append(chain_probabilities)

    if not per_chain_probabilities:
        return None

    raw_probabilities: dict[str, float] = {}
    probabilities: dict[str, float] = {}
    calibration_methods: dict[str, str] = {}
    ensemble_agreement_scores: list[float] = []
    for domain in PREDICTION_DOMAINS:
        domain_values = [chain_probabilities.get(domain, 0.0) for chain_probabilities in per_chain_probabilities]
        if domain_values:
            raw_probability = float(np.clip(np.mean(domain_values), 0.0, 1.0))
            if len(domain_values) > 1:
                ensemble_agreement_scores.append(float(np.clip(1.0 - (max(domain_values) - min(domain_values)), 0.0, 1.0)))
        else:
            raw_probability = 0.0
        raw_probabilities[domain] = raw_probability
        calibrated_probability, method = _apply_comorbidity_probability_calibrator(
            probability_calibrators.get(domain),
            raw_probability,
        )
        probabilities[domain] = normalize_score(
            0.66 * calibrated_probability + 0.34 * float(upstream_blend.get(domain, 0.0) or 0.0)
        )
        calibration_methods[domain] = method

    chain_order = list(chain_ensemble[0].get("chain_order", bundle.get("chain_order", PREDICTION_DOMAINS)))
    binary_predictions: dict[str, bool] = {
        domain: probabilities[domain] >= float(thresholds.get(domain, COMORBIDITY_POSITIVE_THRESHOLD))
        for domain in PREDICTION_DOMAINS
    }

    top_pairs = _comorbidity_pairwise_summary(probabilities, pairwise_lift)
    positive_domains = [domain for domain, value in binary_predictions.items() if value]
    peak_probability = max(probabilities.values(), default=0.0)
    mean_probability = average(list(probabilities.values()) or [0.0])
    pair_probability = top_pairs[0]["probability"] if top_pairs else 0.0
    ensemble_agreement = average(ensemble_agreement_scores) if ensemble_agreement_scores else 0.68
    confidence = normalize_score(
        0.34 * peak_probability
        + 0.22 * mean_probability
        + 0.18 * pair_probability
        + 0.12 * ensemble_agreement
        + 0.14 * upstream_consensus
    )
    return {
        "available": bool(positive_domains or top_pairs),
        "model_type": str(bundle.get("model_type", "classifier_chain_ensemble")),
        "feature_names": feature_names,
        "chain_order": chain_order,
        "ensemble_size": ensemble_size,
        "chain_orders": [list(chain_spec.get("chain_order", [])) for chain_spec in chain_ensemble],
        "raw_probabilities": raw_probabilities,
        "probabilities": probabilities,
        "predicted_domains": positive_domains,
        "binary_predictions": binary_predictions,
        "top_pairs": top_pairs,
        "dominant_pair": top_pairs[0] if top_pairs else None,
        "pairwise_lift": pairwise_lift,
        "label_thresholds": thresholds,
        "probability_calibration_methods": calibration_methods,
        "confidence": confidence,
        "confidence_breakdown": {
            "peak_probability": round(float(peak_probability), 6),
            "mean_probability": round(float(mean_probability), 6),
            "pair_probability": round(float(pair_probability), 6),
            "ensemble_agreement": round(float(ensemble_agreement), 6),
            "upstream_consensus": round(float(upstream_consensus), 6),
        },
        "metrics": dict(bundle.get("metrics", {}) or {}),
        "notes": "Joint comorbidity probabilities combine the classifier-chain ensemble with upstream text, audio, and image consensus scores.",
    }


def score_comorbidity(modality_results: dict[str, dict], overall: dict | None = None) -> dict:
    result = _score_comorbidity_from_bundle(modality_results)
    if result is not None:
        return result
    return _heuristic_comorbidity_result(overall or {"scores": {}})


def build_recommendation(overall: dict, language: str = "english", *, review_required: bool = False) -> str:
    language = str(language or "english").strip().lower()
    high_risks = [name for name in PREDICTION_DOMAINS if overall[name] == "high"]
    moderate_risks = [name for name in PREDICTION_DOMAINS if overall[name] == "moderate"]

    if language == "hindi":
        if high_risks:
            joined = ", ".join(PREDICTION_LABELS[name].lower() for name in high_risks)
            return f"{joined} के लिए उच्च जोखिम संकेत मिला। जल्द से जल्द मानसिक स्वास्थ्य विशेषज्ञ या प्रशिक्षित स्वास्थ्यकर्मी से फॉलो-अप कराएँ।"
        if moderate_risks:
            joined = ", ".join(PREDICTION_LABELS[name].lower() for name in moderate_risks)
            return f"{joined} के लिए मध्यम जोखिम संकेत मिला। फॉलो-अप बातचीत, दोबारा स्क्रीनिंग, और सहायक जाँच की सलाह दी जाती है।"
        return "वर्तमान बहु-मोड संकेत कम जोखिम दिखाते हैं, लेकिन लक्षण बने रहें या बढ़ें तो दोबारा स्क्रीनिंग करें।"

    if language == "bengali":
        if high_risks:
            joined = ", ".join(PREDICTION_LABELS[name].lower() for name in high_risks)
            return f"{joined} এর জন্য উচ্চ ঝুঁকির ইঙ্গিত পাওয়া গেছে। যত দ্রুত সম্ভব মানসিক স্বাস্থ্য বিশেষজ্ঞ বা প্রশিক্ষিত স্বাস্থ্যকর্মীর ফলো-আপ প্রয়োজন।"
        if moderate_risks:
            joined = ", ".join(PREDICTION_LABELS[name].lower() for name in moderate_risks)
            return f"{joined} এর জন্য মাঝারি ঝুঁকির ইঙ্গিত পাওয়া গেছে। ফলো-আপ আলোচনা, পুনরায় স্ক্রিনিং, এবং সহায়ক পর্যবেক্ষণ প্রয়োজন।"
        return "বর্তমান বহুমাত্রিক সংকেত কম ঝুঁকি দেখাচ্ছে, তবে উপসর্গ থাকলে বা বাড়লে আবার স্ক্রিনিং করুন।"

    if review_required and high_risks:
        joined = ", ".join(PREDICTION_LABELS[name].lower() for name in high_risks)
        return (
            f"Screening-only result: high {joined} risk. Please arrange clinician review or trained community "
            "health worker follow-up as soon as possible. This is not a diagnosis."
        )

    if review_required and moderate_risks:
        joined = ", ".join(PREDICTION_LABELS[name].lower() for name in moderate_risks)
        return (
            f"Screening-only result: moderate {joined} risk. Please schedule guided follow-up review, repeat "
            "screening if needed, and supportive check-in from a clinician or trained community health worker. "
            "This is not a diagnosis."
        )

    if review_required:
        return (
            "Screening-only result: the multimodal evidence is uncertain or incomplete, so clinician review "
            "is recommended before any decision. This is not a diagnosis."
        )

    return (
        "Screening-only result: current multimodal signals are low risk. Continue routine monitoring and "
        "re-screen if symptoms persist or functioning worsens."
    )


def screen(
    text_input: str = "",
    audio_path: str = None,
    image_path: str = None,
    passive_video_path: str | None = None,
    typing_events: list[dict] | dict | list[float] | None = None,
    language: str = "english",
) -> dict:
    text_features = extract_text_features(text_input, language=language)
    audio_features = extract_audio_features(audio_path)
    image_features = extract_image_features(image_path)
    passive_features = extract_passive_biomarkers(passive_video_path, typing_events)

    text_result = score_text_features(text_features)
    audio_result = score_audio_features(audio_features)
    image_result = score_image_features(image_features)
    passive_result = score_passive_biomarkers(passive_features)

    overall = aggregate_scores([text_result, audio_result, image_result])
    comorbidity = score_comorbidity(
        {
            "text": text_result,
            "audio": audio_result,
            "image": image_result,
        },
        overall=overall,
    )
    if comorbidity.get("available"):
        overall["confidence"] = normalize_score(
            0.72 * float(overall.get("confidence", 0.0) or 0.0)
            + 0.28 * float(comorbidity.get("confidence", 0.0) or 0.0)
        )
    governance = _screening_governance_snapshot(text_result, audio_result, image_result, overall, comorbidity)
    recommendation = build_recommendation(
        overall,
        language=language,
        review_required=bool(governance["review_required"]),
    )
    disclaimer = (
        "This tool is for screening support only. It does not diagnose mental health conditions, and it "
        "should not replace clinician review, emergency care, or local referral pathways."
    )
    if str(language).strip().lower() == "hindi":
        disclaimer = "यह उपकरण प्रारंभिक स्क्रीनिंग प्रोटोटाइप है। यह निदान नहीं करता और न ही चिकित्सकीय निर्णय या आपातकालीन देखभाल का विकल्प है।"
    elif str(language).strip().lower() == "bengali":
        disclaimer = "এই টুলটি একটি প্রাথমিক স্ক্রিনিং প্রোটোটাইপ। এটি রোগ নির্ণয় করে না এবং চিকিৎসকের সিদ্ধান্ত বা জরুরি সেবার বিকল্প নয়।"

    return {
        "text": text_result,
        "audio": audio_result,
        "image": image_result,
        "passive": passive_result,
        "overall": overall,
        "comorbidity": comorbidity,
        "screening_mode": governance["screening_mode"],
        "review_required": governance["review_required"],
        "screening_governance": governance,
        "model_stats": {
            "screening_governance": governance,
        },
        "recommendation": recommendation,
        "disclaimer": disclaimer,
    }
