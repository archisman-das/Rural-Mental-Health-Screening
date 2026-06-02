from __future__ import annotations

import pickle
from functools import lru_cache
from pathlib import Path


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
    return {
        "modality": modality,
        "bundle_path": str(get_model_bundle_path(modality).resolve()),
        "domains": list(bundle.get("domains", [])),
        "feature_names": list(bundle.get("feature_names", [])),
        "confidence_hint": float(bundle.get("confidence_hint", 0.0)),
        "sample_count": int(bundle.get("sample_count", 0)),
        "sample_counts": dict(bundle.get("sample_counts", {}) or {}),
        "train_counts": dict(bundle.get("train_counts", {}) or {}),
        "test_counts": dict(bundle.get("test_counts", {}) or {}),
        "manifest_path": bundle.get("manifest_path"),
        "dataset_root": bundle.get("dataset_root"),
        "trained_at": bundle.get("trained_at"),
        "macro_r2": float(metrics.get("macro_r2", 0.0)),
        "metrics": {
            key: value for key, value in metrics.items()
            if key != "macro_r2"
        },
        "skipped_domains": dict(bundle.get("skipped_domains", {}) or {}),
        "model_source": "trained_bundle",
    }


def summarize_all_bundles() -> dict[str, dict]:
    summaries: dict[str, dict] = {}
    for modality in ("text", "audio", "image"):
        summary = bundle_summary(modality)
        if summary is not None:
            summaries[modality] = summary
    return summaries
