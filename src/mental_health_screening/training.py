from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from .constants import PREDICTION_DOMAINS
from .feature_extract import extract_audio_features, extract_image_features, extract_text_features
from .model_features import audio_feature_vector, image_feature_vector, text_feature_vector
from .model_store import save_model_bundle


SUPPORTED_MODALITIES = ("text", "audio", "image")


def _load_manifest(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Training manifest not found: {path}")
    if path.suffix.lower() == ".jsonl":
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        return pd.DataFrame(rows)
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        return pd.DataFrame(payload)
    return pd.read_csv(path)


def _resolve_path(base_dir: Path, raw_value: str | None) -> str | None:
    if not raw_value or not str(raw_value).strip():
        return None
    path = Path(str(raw_value))
    if path.is_absolute():
        return str(path)
    return str((base_dir / path).resolve())


def _parse_target_value(value) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _extract_feature_vector(record: dict, base_dir: Path, modality: str) -> tuple[dict, list[str], list[float]] | None:
    if modality == "text":
        text = str(record.get("text", "") or "")
        if not text.strip():
            return None
        features = extract_text_features(text)
        feature_names, vector = text_feature_vector(features)
        return features, feature_names, vector

    if modality == "audio":
        audio_path = _resolve_path(base_dir, record.get("audio_path"))
        if not audio_path:
            return None
        features = extract_audio_features(audio_path)
        feature_names, vector = audio_feature_vector(features)
        return features, feature_names, vector

    if modality == "image":
        image_path = _resolve_path(base_dir, record.get("image_path"))
        if not image_path:
            return None
        features = extract_image_features(image_path)
        feature_names, vector = image_feature_vector(features)
        return features, feature_names, vector

    raise ValueError(f"Unsupported modality: {modality}")


def _extract_domain_training_rows(
    df: pd.DataFrame,
    base_dir: Path,
    modality: str,
    domain: str,
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    rows_x: list[list[float]] = []
    rows_y: list[float] = []
    feature_names: list[str] | None = None

    for record in df.to_dict(orient="records"):
        target_value = _parse_target_value(record.get(domain))
        if target_value is None:
            continue

        extracted = _extract_feature_vector(record, base_dir, modality)
        if extracted is None:
            continue

        features, feature_names, vector = extracted
        if not features.get("available"):
            continue

        rows_x.append(vector)
        rows_y.append(float(np.clip(target_value, 0.0, 1.0)))

    if not rows_x or feature_names is None:
        raise ValueError(f"No usable labeled rows found for modality '{modality}' and domain '{domain}'.")

    return np.asarray(rows_x, dtype=float), np.asarray(rows_y, dtype=float), feature_names


def _fit_domain_model(
    features_x: np.ndarray,
    targets_y: np.ndarray,
    random_state: int,
    test_size: float,
) -> tuple[RandomForestRegressor, dict, int, int]:
    x_train, x_test, y_train, y_test = train_test_split(
        features_x,
        targets_y,
        test_size=min(test_size, 0.4) if len(features_x) > 6 else 0.2,
        random_state=random_state,
    )

    model = RandomForestRegressor(
        n_estimators=240,
        random_state=random_state,
        min_samples_leaf=2,
        n_jobs=-1,
    )
    model.fit(x_train, y_train)
    predictions = np.clip(model.predict(x_test), 0.0, 1.0)
    metrics = {
        "mse": float(mean_squared_error(y_test, predictions)),
        "r2": float(r2_score(y_test, predictions)),
    }
    return model, metrics, int(len(x_train)), int(len(x_test))


def train_modality_model(
    manifest_path: str | Path,
    modality: str,
    dataset_root: str | Path | None = None,
    test_size: float = 0.2,
    random_state: int = 42,
    domains: list[str] | tuple[str, ...] | None = None,
    min_samples_per_domain: int = 5,
) -> dict:
    modality = modality.lower().strip()
    if modality not in SUPPORTED_MODALITIES:
        raise ValueError(f"Unsupported modality '{modality}'. Expected one of {SUPPORTED_MODALITIES}.")

    requested_domains = list(domains or PREDICTION_DOMAINS)
    unknown_domains = [domain for domain in requested_domains if domain not in PREDICTION_DOMAINS]
    if unknown_domains:
        raise ValueError(f"Unsupported domains requested: {unknown_domains}")

    manifest_path = Path(manifest_path)
    base_dir = Path(dataset_root) if dataset_root else manifest_path.parent
    df = _load_manifest(manifest_path)

    models: dict[str, RandomForestRegressor] = {}
    metrics: dict[str, dict] = {}
    sample_counts: dict[str, int] = {}
    train_counts: dict[str, int] = {}
    test_counts: dict[str, int] = {}
    feature_names: list[str] | None = None
    skipped_domains: dict[str, str] = {}

    for domain in requested_domains:
        try:
            features_x, targets_y, domain_feature_names = _extract_domain_training_rows(df, base_dir, modality, domain)
        except Exception as error:
            skipped_domains[domain] = str(error)
            continue

        if len(features_x) < min_samples_per_domain:
            skipped_domains[domain] = (
                f"At least {min_samples_per_domain} usable labeled rows are required to train "
                f"the {modality} {domain} model."
            )
            continue

        model, domain_metrics, train_count, test_count = _fit_domain_model(
            features_x=features_x,
            targets_y=targets_y,
            random_state=random_state,
            test_size=test_size,
        )
        models[domain] = model
        metrics[domain] = domain_metrics
        sample_counts[domain] = int(len(features_x))
        train_counts[domain] = train_count
        test_counts[domain] = test_count
        if feature_names is None:
            feature_names = domain_feature_names

    if not models or feature_names is None:
        raise ValueError(
            f"No trainable domains were found for modality '{modality}'. Details: "
            f"{'; '.join(f'{domain}: {reason}' for domain, reason in skipped_domains.items()) or 'no usable labels'}"
        )

    trained_domains = list(models.keys())
    macro_r2 = float(np.mean([metrics[domain]["r2"] for domain in trained_domains]))
    confidence_hint = float(np.clip((macro_r2 + 1.0) / 2.0, 0.2, 0.95))

    bundle = {
        "modality": modality,
        "domains": trained_domains,
        "feature_names": feature_names,
        "models": models,
        "metrics": {
            **metrics,
            "macro_r2": macro_r2,
        },
        "confidence_hint": confidence_hint,
        "sample_count": int(sum(sample_counts.values())),
        "sample_counts": sample_counts,
        "train_counts": train_counts,
        "test_counts": test_counts,
        "manifest_path": str(manifest_path.resolve()),
        "dataset_root": str(base_dir.resolve()),
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "skipped_domains": skipped_domains,
    }
    save_model_bundle(modality, bundle)
    return bundle


def train_all_models(
    manifest_path: str | Path,
    dataset_root: str | Path | None = None,
    domains: list[str] | tuple[str, ...] | None = None,
    min_samples_per_domain: int = 5,
) -> dict:
    results = {}
    for modality in SUPPORTED_MODALITIES:
        try:
            results[modality] = {
                "status": "trained",
                "bundle": train_modality_model(
                    manifest_path=manifest_path,
                    modality=modality,
                    dataset_root=dataset_root,
                    domains=domains,
                    min_samples_per_domain=min_samples_per_domain,
                ),
            }
        except Exception as error:
            results[modality] = {"status": "skipped", "error": str(error)}
    return results


def _parse_domains_argument(raw_value: str | None) -> list[str] | None:
    if raw_value is None:
        return None
    domains = [value.strip() for value in raw_value.split(",") if value.strip()]
    return domains or None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train modality models for rural mental health screening from labeled manifests."
    )
    parser.add_argument("manifest", help="Path to CSV, JSON, or JSONL manifest with labeled examples.")
    parser.add_argument(
        "--dataset-root",
        dest="dataset_root",
        default=None,
        help="Base directory used to resolve audio_path/image_path values.",
    )
    parser.add_argument(
        "--modality",
        choices=(*SUPPORTED_MODALITIES, "all"),
        default="all",
        help="Train one modality or all supported modalities.",
    )
    parser.add_argument(
        "--domains",
        default=None,
        help="Optional comma-separated subset of domains to train, for example: depression,stress",
    )
    parser.add_argument(
        "--min-samples-per-domain",
        dest="min_samples_per_domain",
        type=int,
        default=5,
        help="Minimum usable labeled rows required before a domain model is trained.",
    )
    args = parser.parse_args()

    selected_domains = _parse_domains_argument(args.domains)
    if args.modality == "all":
        result = train_all_models(
            manifest_path=args.manifest,
            dataset_root=args.dataset_root,
            domains=selected_domains,
            min_samples_per_domain=args.min_samples_per_domain,
        )
    else:
        result = {
            args.modality: {
                "status": "trained",
                "bundle": train_modality_model(
                    manifest_path=args.manifest,
                    modality=args.modality,
                    dataset_root=args.dataset_root,
                    domains=selected_domains,
                    min_samples_per_domain=args.min_samples_per_domain,
                ),
            }
        }

    printable = {}
    for key, value in result.items():
        printable[key] = {
            inner_key: inner_value
            for inner_key, inner_value in value.items()
            if inner_key != "bundle"
        }
        if "bundle" in value:
            bundle = value["bundle"]
            printable[key]["trained_domains"] = bundle["domains"]
            printable[key]["sample_counts"] = bundle["sample_counts"]
            printable[key]["macro_r2"] = bundle["metrics"]["macro_r2"]
            printable[key]["skipped_domains"] = bundle.get("skipped_domains", {})
    print(json.dumps(printable, indent=2))


if __name__ == "__main__":
    main()
