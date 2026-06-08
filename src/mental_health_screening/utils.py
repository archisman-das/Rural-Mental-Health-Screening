from typing import Iterable


def normalize_score(value: float) -> float:
    if value is None:
        return 0.0
    return max(0.0, min(1.0, float(value)))


def risk_level(score: float) -> str:
    if score < 0.33:
        return "low"
    if score < 0.66:
        return "moderate"
    return "high"


def average(values: Iterable[float]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return sum(values) / len(values)


def confidence_weighted_score(score: float, confidence: float, neutral: float = 0.5, minimum_weight: float = 0.2) -> float:
    score = normalize_score(score)
    confidence = normalize_score(confidence)
    weight = max(minimum_weight, confidence)
    return normalize_score((score * weight) + (neutral * (1.0 - weight)))
