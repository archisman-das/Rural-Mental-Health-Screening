from __future__ import annotations

import json
import pickle
import importlib
import sys
from functools import lru_cache
from pathlib import Path

try:
    import shap
except ImportError:
    shap = None


MODEL_DIR = Path(__file__).resolve().parents[2] / "models" / "mental_health_screening"
TMP_MODEL_DIR = Path(__file__).resolve().parents[2] / "tmp_datasets"
ONNX_DIR = MODEL_DIR / "onnx"

RECOMMENDED_REQUIREMENTS = {
    "audio_sequence": {"min_samples": 500, "target_quality": 0.55},
    "audio_spectrogram": {"min_samples": 500, "target_quality": 0.55},
    "image_dl": {"min_samples": 250, "target_quality": 0.55},
    "comorbidity": {"min_samples": 1000, "target_quality": 0.55},
    "passive_biomarkers": {"min_samples": 25, "target_quality": 0.60},
}


def _ensure_legacy_module_alias() -> None:
    if "mental_health_screening" in sys.modules:
        return
    try:
        sys.modules["mental_health_screening"] = importlib.import_module("src.mental_health_screening")
    except Exception:
        pass


def ensure_model_dir() -> Path:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    return MODEL_DIR


def get_model_bundle_path(modality: str) -> Path:
    if modality in {"text_transformer", "audio_sequence", "audio_spectrogram", "image_dl", "passive_biomarkers"}:
        TMP_MODEL_DIR.mkdir(parents=True, exist_ok=True)
        return TMP_MODEL_DIR / f"{modality}_bundle.pkl"
    return ensure_model_dir() / f"{modality}_bundle.pkl"


def get_onnx_bundle_dir() -> Path:
    ONNX_DIR.mkdir(parents=True, exist_ok=True)
    return ONNX_DIR


def get_onnx_manifest_path() -> Path:
    return get_onnx_bundle_dir() / "manifest.json"


def _json_safe(value):
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def _best_candidate_metrics(candidate_metrics: dict | None) -> dict:
    if not isinstance(candidate_metrics, dict):
        return {}
    best_candidate = {}
    best_score = (-1.0, -1.0, -1.0, -1.0, -1.0)
    for candidate in candidate_metrics.values():
        if not isinstance(candidate, dict):
            continue
        score = (
            float(candidate.get("best_fbeta", candidate.get("f1", 0.0)) or 0.0),
            float(candidate.get("f1", 0.0) or 0.0),
            float(candidate.get("precision", 0.0) or 0.0),
            float(candidate.get("accuracy", 0.0) or 0.0),
            float(candidate.get("recall", 0.0) or 0.0),
        )
        if score > best_score:
            best_score = score
            best_candidate = candidate
    return dict(best_candidate)


def _synthesize_macro_metrics(bundle: dict, metrics: dict) -> dict:
    resolved = dict(metrics)
    required_keys = {"macro_accuracy", "macro_precision", "macro_recall", "macro_f1", "macro_r2"}
    if required_keys.intersection(resolved.keys()) or {"exact_match", "label_accuracy"}.intersection(resolved.keys()):
        return resolved

    model_selection = bundle.get("model_selection", {}) or {}
    selected_metrics = [
        _best_candidate_metrics(candidate_metrics)
        for candidate_metrics in model_selection.values()
        if isinstance(candidate_metrics, dict)
    ]
    selected_metrics = [candidate for candidate in selected_metrics if candidate]
    if not selected_metrics:
        return resolved

    def _mean_metric(*keys: str) -> float | None:
        values = []
        for candidate in selected_metrics:
            for key in keys:
                value = candidate.get(key)
                if value is not None and value != "":
                    try:
                        numeric = float(value)
                    except (TypeError, ValueError):
                        continue
                    values.append(numeric)
                    break
        if not values:
            return None
        return float(sum(values) / len(values))

    for target_key, source_keys in (
        ("macro_accuracy", ("accuracy", "macro_accuracy")),
        ("macro_precision", ("precision", "macro_precision")),
        ("macro_recall", ("recall", "macro_recall")),
        ("macro_f1", ("f1", "macro_f1")),
        ("macro_r2", ("r2", "macro_r2")),
    ):
        mean_value = _mean_metric(*source_keys)
        if mean_value is not None:
            resolved[target_key] = mean_value

    return resolved


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
    return max(0.0, min(1.0, float(best_score)))


def _bundle_improvement_requirements(modality: str, bundle: dict) -> dict:
    requirement = dict(RECOMMENDED_REQUIREMENTS.get(modality, {}))
    if not requirement:
        return {}
    current_sample_count = int(bundle.get("sample_count", 0) or 0)
    current_quality = _bundle_quality_score(bundle)
    min_samples = int(requirement.get("min_samples", 0) or 0)
    target_quality = float(requirement.get("target_quality", 0.0) or 0.0)
    return {
        "current_sample_count": current_sample_count,
        "required_min_samples": min_samples,
        "sample_gap": max(0, min_samples - current_sample_count),
        "current_quality": round(float(current_quality), 6),
        "target_quality": target_quality,
        "quality_gap": round(max(0.0, target_quality - current_quality), 6),
        "ready_for_trusted_use": bool(current_sample_count >= min_samples and current_quality >= target_quality),
    }


def save_model_bundle(modality: str, bundle: dict) -> Path:
    path = get_model_bundle_path(modality)
    with path.open("wb") as handle:
        pickle.dump(bundle, handle)
    load_model_bundle.cache_clear()
    return path


@lru_cache(maxsize=8)
def load_model_bundle(modality: str) -> dict | None:
    path = get_model_bundle_path(modality)
    if not path.exists():
        return None
    _ensure_legacy_module_alias()
    with path.open("rb") as handle:
        return pickle.load(handle)


def bundle_summary(modality: str) -> dict | None:
    bundle = load_model_bundle(modality)
    if bundle is None:
        return None
    metrics = _synthesize_macro_metrics(bundle, bundle.get("metrics", {}) or {})
    summary = {
        "modality": modality,
        "bundle_path": str(get_model_bundle_path(modality).resolve()),
        "domains": list(bundle.get("domains", [])),
        "feature_names": list(bundle.get("feature_names", [])),
        "training_strategy": bundle.get("training_strategy", "centralized"),
        "federated": dict(bundle.get("federated", {}) or {}),
        "confidence_hint": float(bundle.get("confidence_hint", 0.0)),
        "label_thresholds": dict(bundle.get("label_thresholds", {}) or {}),
        "sample_count": int(bundle.get("sample_count", 0)),
        "sample_counts": dict(bundle.get("sample_counts", {}) or {}),
        "train_counts": dict(bundle.get("train_counts", {}) or {}),
        "test_counts": dict(bundle.get("test_counts", {}) or {}),
        "model_families": dict(bundle.get("model_families", {}) or {}),
        "model_selection": dict(bundle.get("model_selection", {}) or {}),
        "manifest_path": bundle.get("manifest_path"),
        "dataset_root": bundle.get("dataset_root"),
        "source_datasets": list(bundle.get("source_datasets", [])),
        "label_sources": list(bundle.get("label_sources", [])),
        "trained_at": bundle.get("trained_at"),
        "macro_r2": float(metrics.get("macro_r2", 0.0)),
        "calibration_quality": float(metrics.get("calibration_quality", 0.0)),
        "explainability": {
            "library": "shap",
            "available": shap is not None,
            "supported_domains": list(bundle.get("domains", [])) if shap is not None else [],
        },
        "confidence_calibration": {
            domain: {
                "method": (bundle.get("confidence_calibrators", {}) or {}).get(domain, {}).get("method", "none"),
                "uncertainty_scale": float(((bundle.get("confidence_calibrators", {}) or {}).get(domain, {}) or {}).get("uncertainty_scale", 0.0)),
                "metrics": dict((((bundle.get("confidence_calibrators", {}) or {}).get(domain, {}) or {}).get("metrics", {}) or {})),
            }
            for domain in bundle.get("domains", [])
        },
        "metrics": {
            key: value for key, value in metrics.items()
            if key not in {"macro_r2", "calibration_quality"}
        },
        "skipped_domains": dict(bundle.get("skipped_domains", {}) or {}),
        "improvement_requirements": _bundle_improvement_requirements(modality, bundle),
        "metric_source": "bundle_metrics" if bundle.get("metrics") else "synthesized_from_model_selection",
        "model_source": "trained_bundle",
    }
    onnx_manifest_path = get_onnx_manifest_path()
    if onnx_manifest_path.exists():
        try:
            manifest = json.loads(onnx_manifest_path.read_text(encoding="utf-8"))
            summary["onnx_artifacts"] = manifest.get(modality, {})
        except Exception:
            summary["onnx_artifacts"] = {}
    if modality in {"comorbidity", "text_transformer"} or str(bundle.get("model_type", "")).startswith("classifier_chain") or str(bundle.get("model_type", "")).startswith("text_transformer"):
        joint_prediction = dict(bundle.get("joint_prediction", {}) or {})
        if not joint_prediction:
            joint_prediction = {
                "model_type": bundle.get("model_type", "classifier_chain"),
                "chain_order": list(bundle.get("chain_order", bundle.get("domains", []))),
                "label_prevalence": dict(bundle.get("label_prevalence", {}) or {}),
                "pairwise_lift": dict(bundle.get("pairwise_lift", {}) or {}),
                "label_thresholds": dict(bundle.get("label_thresholds", {}) or {}),
            }
        if bundle.get("chain_orders"):
            joint_prediction["chain_orders"] = list(bundle.get("chain_orders", []))
        if bundle.get("ensemble_size") is not None:
            joint_prediction["ensemble_size"] = int(bundle.get("ensemble_size", 0))
        summary["joint_prediction"] = {
            **joint_prediction,
        }
        if bundle.get("probability_calibrators"):
            summary["joint_prediction"]["probability_calibration"] = {
                domain: {
                    "method": (bundle.get("probability_calibrators", {}) or {}).get(domain, {}).get("method", "none"),
                    "positive_rate": float((bundle.get("probability_calibrators", {}) or {}).get(domain, {}).get("positive_rate", 0.0)),
                }
                for domain in bundle.get("domains", [])
            }
        if bundle.get("joint_prediction", {}).get("threshold_tuning") or bundle.get("joint_prediction", {}).get("probability_calibration"):
            summary["joint_prediction"].setdefault("threshold_tuning", dict(bundle.get("joint_prediction", {}).get("threshold_tuning", {}) or {}))
        if bundle.get("chain_model_families"):
            summary["joint_prediction"]["chain_model_families"] = dict(bundle.get("chain_model_families", {}) or {})
        summary["metrics"] = {
            **summary["metrics"],
            "exact_match": float(metrics.get("exact_match", 0.0)),
            "macro_f1": float(metrics.get("macro_f1", 0.0)),
            "label_accuracy": float(metrics.get("label_accuracy", 0.0)),
        }
    return _json_safe(summary)


def summarize_all_bundles() -> dict[str, dict]:
    summaries: dict[str, dict] = {}
    for modality in ("text", "text_transformer", "audio", "audio_sequence", "audio_spectrogram", "image", "image_dl", "comorbidity", "passive_biomarkers"):
        summary = bundle_summary(modality)
        if summary is not None:
            summaries[modality] = summary
    return summaries
