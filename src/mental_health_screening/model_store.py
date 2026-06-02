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
