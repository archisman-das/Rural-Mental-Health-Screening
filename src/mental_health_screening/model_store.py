from __future__ import annotations

import pickle
from functools import lru_cache
from pathlib import Path

try:
    import shap
except ImportError:
    shap = None


MODEL_DIR = Path(__file__).resolve().parents[2] / "models" / "mental_health_screening"


def ensure_model_dir() -> Path:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    return MODEL_DIR


def get_model_bundle_path(modality: str) -> Path:
    return ensure_model_dir() / f"{modality}_bundle.pkl"


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
    with path.open("rb") as handle:
        return pickle.load(handle)


def bundle_summary(modality: str) -> dict | None:
    bundle = load_model_bundle(modality)
    if bundle is None:
        return None
    metrics = bundle.get("metrics", {}) or {}
    summary = {
        "modality": modality,
        "bundle_path": str(get_model_bundle_path(modality).resolve()),
        "domains": list(bundle.get("domains", [])),
        "feature_names": list(bundle.get("feature_names", [])),
        "training_strategy": bundle.get("training_strategy", "centralized"),
        "federated": dict(bundle.get("federated", {}) or {}),
        "confidence_hint": float(bundle.get("confidence_hint", 0.0)),
        "sample_count": int(bundle.get("sample_count", 0)),
        "sample_counts": dict(bundle.get("sample_counts", {}) or {}),
        "train_counts": dict(bundle.get("train_counts", {}) or {}),
        "test_counts": dict(bundle.get("test_counts", {}) or {}),
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
        "model_source": "trained_bundle",
    }
    if modality == "comorbidity" or str(bundle.get("model_type", "")).startswith("classifier_chain"):
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
        summary["metrics"] = {
            **summary["metrics"],
            "exact_match": float(metrics.get("exact_match", 0.0)),
            "macro_f1": float(metrics.get("macro_f1", 0.0)),
            "label_accuracy": float(metrics.get("label_accuracy", 0.0)),
        }
    return summary


def summarize_all_bundles() -> dict[str, dict]:
    summaries: dict[str, dict] = {}
    for modality in ("text", "audio", "image", "comorbidity"):
        summary = bundle_summary(modality)
        if summary is not None:
            summaries[modality] = summary
    return summaries
