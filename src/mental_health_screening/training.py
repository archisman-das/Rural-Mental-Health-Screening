from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.base import clone
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error, precision_recall_curve, r2_score
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import SGDRegressor
from sklearn.model_selection import train_test_split

from .constants import PREDICTION_DOMAINS
from .feature_extract import extract_audio_features, extract_image_features, extract_text_features
from .model_features import audio_feature_vector, image_feature_vector, text_feature_vector
from .model_store import save_model_bundle
from .predict import COMORBIDITY_MODEL_NAME, COMORBIDITY_MODALITIES, score_audio_features, score_image_features, score_text_features


SUPPORTED_MODALITIES = ("text", "audio", "image")
CALIBRATION_TOLERANCE = 0.15
FEDERATED_DEFAULT_ROUNDS = 6
FEDERATED_DEFAULT_LOCAL_EPOCHS = 2
COMORBIDITY_CHAIN_ENSEMBLE_SIZE = 5
COMORBIDITY_THRESHOLD_BETA = 2.0


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
        # Use lightweight bulk features during training so large public datasets remain tractable.
        features = extract_text_features(text, use_transformer=False, use_ml_pipelines=False)
        feature_names, vector = text_feature_vector(features)
        return features, feature_names, vector

    if modality == "audio":
        audio_path = _resolve_path(base_dir, record.get("audio_path"))
        if not audio_path:
            return None
        features = extract_audio_features(audio_path, include_pitch_features=False)
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


def _build_feature_cache(
    df: pd.DataFrame,
    base_dir: Path,
    modality: str,
) -> tuple[list[dict], list[str] | None]:
    cached_rows: list[dict] = []
    feature_names: list[str] | None = None

    for record in df.to_dict(orient="records"):
        extracted = _extract_feature_vector(record, base_dir, modality)
        if extracted is None:
            cached_rows.append({"record": record, "available": False, "vector": None})
            continue

        features, domain_feature_names, vector = extracted
        if feature_names is None:
            feature_names = domain_feature_names
        cached_rows.append(
            {
                "record": record,
                "available": bool(features.get("available")),
                "vector": vector,
            }
        )

    return cached_rows, feature_names


def _build_comorbidity_modality_results(record: dict, base_dir: Path) -> dict[str, dict]:
    from .predict import score_audio_features, score_image_features, score_text_features

    results: dict[str, dict] = {}

    text = str(record.get("text", "") or "")
    if text.strip():
        text_features = extract_text_features(text, use_transformer=False, use_ml_pipelines=False)
        results["text"] = score_text_features(text_features)
    else:
        results["text"] = {"available": False, "confidence": 0.0}

    audio_path = _resolve_path(base_dir, record.get("audio_path"))
    if audio_path:
        audio_features = extract_audio_features(audio_path, include_pitch_features=False)
        results["audio"] = score_audio_features(audio_features)
    else:
        results["audio"] = {"available": False, "confidence": 0.0}

    image_path = _resolve_path(base_dir, record.get("image_path"))
    if image_path:
        image_features = extract_image_features(image_path)
        results["image"] = score_image_features(image_features)
    else:
        results["image"] = {"available": False, "confidence": 0.0}

    return results


def _comorbidity_feature_vector(results: dict[str, dict]) -> tuple[list[str], list[float]]:
    feature_names: list[str] = []
    vector: list[float] = []
    available_modalities = 0.0

    for modality in COMORBIDITY_MODALITIES:
        modality_result = results.get(modality) or {}
        feature_names.extend([f"{modality}_available", f"{modality}_confidence"])
        available = 1.0 if modality_result.get("available") else 0.0
        confidence = float(modality_result.get("confidence", 0.0) or 0.0)
        vector.extend([available, confidence])
        if available > 0.0:
            available_modalities += 1.0
        for domain in PREDICTION_DOMAINS:
            feature_names.append(f"{modality}_{domain}_score")
            vector.append(float(modality_result.get(f"{domain}_score", 0.0) or 0.0))

    feature_names.append("available_modalities_count")
    vector.append(available_modalities)
    return feature_names, vector


def _comorbidity_targets(record: dict, threshold: float = 0.5) -> list[int] | None:
    targets = []
    for domain in PREDICTION_DOMAINS:
        raw_value = _parse_target_value(record.get(domain))
        if raw_value is None:
            return None
        targets.append(int(float(raw_value) >= threshold))
    return targets


def _pair_key(domain_a: str, domain_b: str) -> str:
    left, right = sorted((domain_a, domain_b))
    return f"{left}|{right}"


def _comorbidity_pairwise_lift(labels: np.ndarray) -> dict[str, float]:
    if labels.size == 0:
        return {}
    pairwise: dict[str, float] = {}
    prevalence = labels.mean(axis=0)
    for i, domain_a in enumerate(PREDICTION_DOMAINS):
        for j, domain_b in enumerate(PREDICTION_DOMAINS[i + 1 :], start=i + 1):
            joint = float(np.mean((labels[:, i] == 1) & (labels[:, j] == 1)))
            expected = float(prevalence[i] * prevalence[j])
            lift = joint / expected if expected > 1e-9 else 1.0
            pairwise[_pair_key(domain_a, domain_b)] = round(float(np.clip(lift, 0.5, 3.0)), 3)
    return pairwise


def _fit_comorbidity_chain(
    features_x: np.ndarray,
    labels_y: np.ndarray,
    chain_order: list[int],
    random_state: int,
) -> dict:
    chain_input = np.asarray(features_x, dtype=float)
    chain_models: list[dict] = []
    order_domains = [PREDICTION_DOMAINS[index] for index in chain_order]

    for position, domain_index in enumerate(chain_order):
        domain = PREDICTION_DOMAINS[domain_index]
        target = labels_y[:, domain_index].astype(int)
        augmented = chain_input if position == 0 else np.hstack([chain_input, labels_y[:, chain_order[:position]]])
        class_counts = np.bincount(target, minlength=2)
        if int(class_counts.min()) < 2:
            model = DummyClassifier(strategy="prior")
            model.fit(augmented, target)
            chain_models.append(
                {
                    "domain": domain,
                    "domain_index": int(domain_index),
                    "model": None,
                    "constant_probability": float(np.clip(target.mean() if len(target) else 0.0, 0.0, 1.0)),
                    "train_accuracy": float(model.score(augmented, target)) if len(target) else 0.0,
                    "train_f1": float(f1_score(target, model.predict(augmented), zero_division=0)) if len(target) else 0.0,
                }
            )
            continue

        model = LogisticRegression(
            max_iter=1500,
            class_weight="balanced",
            solver="liblinear",
            random_state=random_state + position + domain_index,
        )
        model.fit(augmented, target)
        predictions = model.predict(augmented)
        chain_models.append(
            {
                "domain": domain,
                "domain_index": int(domain_index),
                "model": model,
                "constant_probability": None,
                "train_accuracy": float(accuracy_score(target, predictions)),
                "train_f1": float(f1_score(target, predictions, zero_division=0)),
            }
        )

    return {
        "chain_order": order_domains,
        "models": chain_models,
        "train_accuracy": float(np.mean([entry["train_accuracy"] for entry in chain_models])) if chain_models else 0.0,
        "train_f1": float(np.mean([entry["train_f1"] for entry in chain_models])) if chain_models else 0.0,
    }


def _build_comorbidity_chain_orders(random_state: int, ensemble_size: int = COMORBIDITY_CHAIN_ENSEMBLE_SIZE) -> list[list[int]]:
    if ensemble_size < 1:
        raise ValueError("The comorbidity ensemble must contain at least one chain.")
    rng = np.random.default_rng(random_state)
    base_order = list(range(len(PREDICTION_DOMAINS)))
    orders = [base_order]
    while len(orders) < ensemble_size:
        order = list(rng.permutation(len(PREDICTION_DOMAINS)))
        if order not in orders:
            orders.append(order)
    return orders


def _predict_comorbidity_chain_probabilities(chain_spec: dict, vector: list[float]) -> dict[str, float]:
    probabilities: dict[str, float] = {}
    chained_inputs: list[float] = []
    for model_spec in chain_spec.get("models", []):
        domain = model_spec.get("domain")
        if domain is None:
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


def _tune_comorbidity_thresholds(labels_y: np.ndarray, probabilities_y: np.ndarray) -> tuple[dict[str, float], dict[str, dict]]:
    thresholds: dict[str, float] = {}
    tuning_meta: dict[str, dict] = {}

    for index, domain in enumerate(PREDICTION_DOMAINS):
        targets = labels_y[:, index].astype(int)
        scores = np.asarray(probabilities_y[:, index], dtype=float)
        positive_rate = float(targets.mean()) if len(targets) else 0.0
        if len(np.unique(targets)) < 2:
            tuned_threshold = 0.5 if positive_rate >= 0.5 else max(0.1, positive_rate)
            thresholds[domain] = round(float(np.clip(tuned_threshold, 0.05, 0.95)), 3)
            tuning_meta[domain] = {
                "method": "constant",
                "beta": COMORBIDITY_THRESHOLD_BETA,
                "sample_count": int(len(targets)),
                "positive_rate": positive_rate,
                "best_fbeta": 0.0,
            }
            continue

        precision, recall, threshold_values = precision_recall_curve(targets, scores)
        if len(threshold_values) == 0:
            tuned_threshold = 0.5
            best_fbeta = 0.0
        else:
            precision = precision[:-1]
            recall = recall[:-1]
            beta_sq = COMORBIDITY_THRESHOLD_BETA ** 2
            numerator = (1.0 + beta_sq) * precision * recall
            denominator = (beta_sq * precision) + recall
            fbeta = np.divide(
                numerator,
                denominator,
                out=np.zeros_like(numerator, dtype=float),
                where=denominator > 1e-9,
            )
            best_index = int(np.argmax(fbeta))
            tuned_threshold = float(threshold_values[min(best_index, len(threshold_values) - 1)])
            best_fbeta = float(fbeta[best_index]) if len(fbeta) else 0.0

        thresholds[domain] = round(float(np.clip(tuned_threshold, 0.05, 0.95)), 3)
        tuning_meta[domain] = {
            "method": "precision_recall_fbeta",
            "beta": COMORBIDITY_THRESHOLD_BETA,
            "sample_count": int(len(targets)),
            "positive_rate": positive_rate,
            "best_fbeta": round(best_fbeta, 6),
            "threshold": thresholds[domain],
        }

    return thresholds, tuning_meta


def _fit_comorbidity_probability_calibrators(
    labels_y: np.ndarray,
    probabilities_y: np.ndarray,
    random_state: int,
) -> tuple[dict[str, dict], dict[str, dict]]:
    calibrators: dict[str, dict] = {}
    meta: dict[str, dict] = {}

    for index, domain in enumerate(PREDICTION_DOMAINS):
        targets = labels_y[:, index].astype(int)
        scores = np.clip(np.asarray(probabilities_y[:, index], dtype=float), 0.0, 1.0)
        positive_rate = float(targets.mean()) if len(targets) else 0.0
        if len(np.unique(targets)) < 2 or len(targets) < 8:
            calibrators[domain] = {
                "method": "constant",
                "model": None,
                "positive_rate": positive_rate,
            }
            meta[domain] = {
                "method": "constant",
                "sample_count": int(len(targets)),
                "positive_rate": positive_rate,
                "calibrated_brier": float(np.mean((np.full_like(scores, positive_rate) - targets) ** 2)) if len(targets) else 0.0,
            }
            continue

        if len(targets) >= 25 and int(np.bincount(targets, minlength=2).min()) >= 5:
            calibrator_model = IsotonicRegression(out_of_bounds="clip")
            calibrator_model.fit(scores, targets)
            calibrated = np.clip(calibrator_model.predict(scores), 0.0, 1.0)
            method = "isotonic"
        else:
            calibrator_model = LogisticRegression(random_state=random_state + index, solver="lbfgs")
            calibrator_model.fit(scores.reshape(-1, 1), targets)
            calibrated = np.clip(calibrator_model.predict_proba(scores.reshape(-1, 1))[:, 1], 0.0, 1.0)
            method = "platt"

        calibrators[domain] = {
            "method": method,
            "model": calibrator_model,
            "positive_rate": positive_rate,
        }
        meta[domain] = {
            "method": method,
            "sample_count": int(len(targets)),
            "positive_rate": positive_rate,
            "calibrated_brier": float(np.mean((calibrated - targets) ** 2)),
        }

    return calibrators, meta


def _extract_domain_training_rows(
    cached_rows: list[dict],
    modality: str,
    domain: str,
    feature_names: list[str] | None,
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    rows_x: list[list[float]] = []
    rows_y: list[float] = []

    for item in cached_rows:
        target_value = _parse_target_value(item["record"].get(domain))
        if target_value is None or not item.get("available") or item.get("vector") is None:
            continue
        rows_x.append(item["vector"])
        rows_y.append(float(np.clip(target_value, 0.0, 1.0)))

    if not rows_x or feature_names is None:
        raise ValueError(f"No usable labeled rows found for modality '{modality}' and domain '{domain}'.")

    return np.asarray(rows_x, dtype=float), np.asarray(rows_y, dtype=float), feature_names


def _fit_domain_model(
    features_x: np.ndarray,
    targets_y: np.ndarray,
    random_state: int,
    test_size: float,
) -> tuple[RandomForestRegressor, dict, int, int, dict]:
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
    predictions, prediction_std = _forest_prediction_stats(model, x_test)
    metrics = {
        "mse": float(mean_squared_error(y_test, predictions)),
        "r2": float(r2_score(y_test, predictions)),
    }
    calibrator = _fit_confidence_calibrator(
        predictions=predictions,
        prediction_std=prediction_std,
        targets_y=y_test,
        tolerance=CALIBRATION_TOLERANCE,
        random_state=random_state,
    )
    metrics["confidence_brier"] = float(calibrator["metrics"]["calibrated_brier"])
    metrics["confidence_accuracy"] = float(calibrator["metrics"]["calibrated_accuracy"])
    return model, metrics, int(len(x_train)), int(len(x_test)), calibrator


def _forest_prediction_stats(model: RandomForestRegressor, features_x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    tree_predictions = np.asarray([estimator.predict(features_x) for estimator in model.estimators_], dtype=float)
    mean_prediction = np.clip(tree_predictions.mean(axis=0), 0.0, 1.0)
    prediction_std = np.clip(tree_predictions.std(axis=0), 0.0, 1.0)
    return mean_prediction, prediction_std


def _confidence_signal_from_std(prediction_std: np.ndarray, scale: float | None = None) -> tuple[np.ndarray, float]:
    resolved_scale = float(scale) if scale is not None else float(np.percentile(prediction_std, 90))
    if not np.isfinite(resolved_scale) or resolved_scale <= 0.0:
        resolved_scale = 1.0
    signal = np.clip(1.0 - (prediction_std / resolved_scale), 0.0, 1.0)
    return signal, resolved_scale


def _fit_confidence_calibrator(
    predictions: np.ndarray,
    prediction_std: np.ndarray,
    targets_y: np.ndarray,
    tolerance: float,
    random_state: int,
) -> dict:
    correctness = (np.abs(predictions - targets_y) <= tolerance).astype(int)
    base_signal, uncertainty_scale = _confidence_signal_from_std(prediction_std)
    base_brier = float(np.mean((base_signal - correctness) ** 2))
    base_accuracy = float(np.mean((base_signal >= 0.5) == correctness))

    class_counts = np.bincount(correctness, minlength=2)
    if int(class_counts.min()) >= 5 and len(correctness) >= 25:
        calibrator_model = IsotonicRegression(out_of_bounds="clip")
        calibrator_model.fit(base_signal, correctness)
        calibrated = np.clip(calibrator_model.predict(base_signal), 0.0, 1.0)
        method = "isotonic"
    elif int(class_counts.min()) >= 2 and len(correctness) >= 8:
        calibrator_model = LogisticRegression(random_state=random_state, solver="lbfgs")
        calibrator_model.fit(base_signal.reshape(-1, 1), correctness)
        calibrated = np.clip(calibrator_model.predict_proba(base_signal.reshape(-1, 1))[:, 1], 0.0, 1.0)
        method = "platt"
    else:
        calibrator_model = None
        calibrated = np.full_like(base_signal, fill_value=float(correctness.mean()), dtype=float)
        method = "constant"

    calibrated_brier = float(np.mean((calibrated - correctness) ** 2))
    calibrated_accuracy = float(np.mean((calibrated >= 0.5) == correctness))
    return {
        "method": method,
        "model": calibrator_model,
        "uncertainty_scale": float(uncertainty_scale),
        "tolerance": float(tolerance),
        "metrics": {
            "sample_count": int(len(correctness)),
            "positive_rate": float(correctness.mean()),
            "base_brier": base_brier,
            "calibrated_brier": calibrated_brier,
            "base_accuracy": base_accuracy,
            "calibrated_accuracy": calibrated_accuracy,
        },
    }


def _init_federated_regressor(feature_count: int, random_state: int) -> SGDRegressor:
    model = SGDRegressor(
        loss="squared_error",
        penalty="l2",
        alpha=0.0005,
        random_state=random_state,
        learning_rate="invscaling",
        eta0=0.01,
        power_t=0.25,
        max_iter=1,
        tol=None,
        warm_start=True,
        shuffle=False,
    )
    model.coef_ = np.zeros(feature_count, dtype=float)
    model.intercept_ = np.zeros(1, dtype=float)
    model.t_ = 1.0
    model.n_features_in_ = feature_count
    return model


def _clone_linear_model(model: SGDRegressor, random_state: int) -> SGDRegressor:
    cloned = clone(model)
    cloned.random_state = random_state
    cloned.coef_ = np.asarray(model.coef_, dtype=float).copy()
    cloned.intercept_ = np.asarray(model.intercept_, dtype=float).copy()
    cloned.t_ = float(getattr(model, "t_", 1.0))
    cloned.n_features_in_ = int(getattr(model, "n_features_in_", len(cloned.coef_)))
    return cloned


def _aggregate_linear_models(local_models: list[tuple[SGDRegressor, int]], random_state: int) -> SGDRegressor:
    if not local_models:
        raise ValueError("No local models were provided for federated aggregation.")
    feature_count = len(local_models[0][0].coef_)
    global_model = _init_federated_regressor(feature_count, random_state)
    total_weight = float(sum(weight for _, weight in local_models))
    if total_weight <= 0:
        total_weight = float(len(local_models))
    global_model.coef_ = sum(model.coef_ * weight for model, weight in local_models) / total_weight
    global_model.intercept_ = sum(model.intercept_ * weight for model, weight in local_models) / total_weight
    global_model.t_ = max(float(getattr(model, "t_", 1.0)) for model, _ in local_models)
    return global_model


def _derive_center_id(manifest_path: Path, frame: pd.DataFrame, ordinal: int) -> str:
    for column in ("health_centre", "health_center", "centre_id", "center_id", "site", "clinic"):
        if column in frame.columns:
            values = [str(value).strip() for value in frame[column].dropna().tolist() if str(value).strip()]
            if values:
                return values[0]
    return f"{manifest_path.stem or 'centre'}_{ordinal + 1}"


def _federated_manifest_cache(
    manifest_paths: list[str | Path],
    modality: str,
) -> tuple[list[dict], list[str] | None]:
    centers: list[dict] = []
    feature_names: list[str] | None = None
    for index, raw_path in enumerate(manifest_paths):
        manifest_path = Path(raw_path)
        df = _load_manifest(manifest_path)
        base_dir = manifest_path.parent
        cached_rows, center_feature_names = _build_feature_cache(df, base_dir, modality)
        if feature_names is None:
            feature_names = center_feature_names
        elif center_feature_names is not None and feature_names != center_feature_names:
            raise ValueError(f"Feature mismatch detected across federated manifests for modality '{modality}'.")
        centers.append(
            {
                "manifest_path": str(manifest_path.resolve()),
                "dataset_root": str(base_dir.resolve()),
                "center_id": _derive_center_id(manifest_path, df, index),
                "frame": df,
                "cached_rows": cached_rows,
            }
        )
    return centers, feature_names


def _extract_center_domain_rows(
    centers: list[dict],
    modality: str,
    domain: str,
    feature_names: list[str] | None,
    min_center_samples: int,
) -> tuple[list[dict], list[str]]:
    usable_centers: list[dict] = []
    for center in centers:
        try:
            features_x, targets_y, domain_feature_names = _extract_domain_training_rows(
                cached_rows=center["cached_rows"],
                modality=modality,
                domain=domain,
                feature_names=feature_names,
            )
        except Exception:
            continue
        if len(features_x) < min_center_samples:
            continue
        usable_centers.append(
            {
                "center_id": center["center_id"],
                "manifest_path": center["manifest_path"],
                "dataset_root": center["dataset_root"],
                "x": features_x,
                "y": targets_y,
            }
        )
        if feature_names is None:
            feature_names = domain_feature_names

    if not usable_centers or feature_names is None:
        raise ValueError(f"No federated centres had enough usable rows for modality '{modality}' and domain '{domain}'.")
    return usable_centers, feature_names


def _fit_federated_domain_model(
    centers: list[dict],
    feature_count: int,
    random_state: int,
    rounds: int,
    local_epochs: int,
    tolerance: float,
) -> tuple[SGDRegressor, dict, dict]:
    global_model = _init_federated_regressor(feature_count, random_state)
    round_history = []

    for round_index in range(rounds):
        local_models: list[tuple[SGDRegressor, int]] = []
        round_sizes = {}
        for center_index, center in enumerate(centers):
            local_model = _clone_linear_model(global_model, random_state + round_index + center_index + 1)
            for _epoch in range(local_epochs):
                local_model.partial_fit(center["x"], center["y"])
            sample_count = int(len(center["x"]))
            round_sizes[center["center_id"]] = sample_count
            local_models.append((local_model, sample_count))

        global_model = _aggregate_linear_models(local_models, random_state=random_state + round_index + 101)
        round_history.append(
            {
                "round": round_index + 1,
                "participating_centres": len(local_models),
                "sample_counts": round_sizes,
            }
        )

    mse_values = []
    r2_values = []
    center_metrics = []
    correct_within_tolerance = 0
    total_predictions = 0
    absolute_errors = []

    for center in centers:
        predictions = np.clip(global_model.predict(center["x"]), 0.0, 1.0)
        mse = float(mean_squared_error(center["y"], predictions))
        r2 = float(r2_score(center["y"], predictions))
        mse_values.append((mse, len(center["x"])))
        r2_values.append((r2, len(center["x"])))
        absolute_error = np.abs(predictions - center["y"])
        absolute_errors.extend(absolute_error.tolist())
        correct_within_tolerance += int(np.sum(absolute_error <= tolerance))
        total_predictions += int(len(center["x"]))
        center_metrics.append(
            {
                "center_id": center["center_id"],
                "sample_count": int(len(center["x"])),
                "mse": mse,
                "r2": r2,
            }
        )

    total_weight = float(sum(weight for _, weight in mse_values)) or 1.0
    weighted_mse = float(sum(value * weight for value, weight in mse_values) / total_weight)
    weighted_r2 = float(sum(value * weight for value, weight in r2_values) / total_weight)
    residual_scale = float(np.percentile(np.asarray(absolute_errors, dtype=float), 75)) if absolute_errors else 0.25
    if not np.isfinite(residual_scale) or residual_scale <= 0.0:
        residual_scale = 0.25
    calibrator = {
        "method": "constant",
        "model": None,
        "uncertainty_scale": float(residual_scale),
        "tolerance": float(tolerance),
        "metrics": {
            "sample_count": int(total_predictions),
            "positive_rate": float(correct_within_tolerance / max(total_predictions, 1)),
            "base_brier": 0.0,
            "calibrated_brier": 0.0,
            "base_accuracy": 0.0,
            "calibrated_accuracy": float(correct_within_tolerance / max(total_predictions, 1)),
            "residual_scale": float(residual_scale),
        },
    }
    metrics = {
        "mse": weighted_mse,
        "r2": weighted_r2,
        "federated_rounds": int(rounds),
        "federated_centres": int(len(centers)),
    }
    return global_model, metrics, {
        "round_history": round_history,
        "center_metrics": center_metrics,
        "calibrator": calibrator,
    }


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
    cached_rows, cached_feature_names = _build_feature_cache(df, base_dir, modality)
    source_datasets = sorted({str(value).strip() for value in df.get("source_dataset", pd.Series(dtype=str)).dropna().tolist() if str(value).strip()})
    label_sources = sorted({str(value).strip() for value in df.get("label_source", pd.Series(dtype=str)).dropna().tolist() if str(value).strip()})

    models: dict[str, RandomForestRegressor] = {}
    metrics: dict[str, dict] = {}
    confidence_calibrators: dict[str, dict] = {}
    sample_counts: dict[str, int] = {}
    train_counts: dict[str, int] = {}
    test_counts: dict[str, int] = {}
    feature_names: list[str] | None = None
    skipped_domains: dict[str, str] = {}

    for domain in requested_domains:
        try:
            features_x, targets_y, domain_feature_names = _extract_domain_training_rows(
                cached_rows=cached_rows,
                modality=modality,
                domain=domain,
                feature_names=cached_feature_names,
            )
        except Exception as error:
            skipped_domains[domain] = str(error)
            continue

        if len(features_x) < min_samples_per_domain:
            skipped_domains[domain] = (
                f"At least {min_samples_per_domain} usable labeled rows are required to train "
                f"the {modality} {domain} model."
            )
            continue

        model, domain_metrics, train_count, test_count, calibrator = _fit_domain_model(
            features_x=features_x,
            targets_y=targets_y,
            random_state=random_state,
            test_size=test_size,
        )
        models[domain] = model
        metrics[domain] = domain_metrics
        confidence_calibrators[domain] = calibrator
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
    calibration_quality = float(
        np.mean([
            confidence_calibrators[domain]["metrics"]["calibrated_accuracy"]
            for domain in trained_domains
        ])
    )
    confidence_hint = float(np.clip(0.35 * ((macro_r2 + 1.0) / 2.0) + 0.65 * calibration_quality, 0.05, 0.99))

    bundle = {
        "modality": modality,
        "domains": trained_domains,
        "feature_names": feature_names,
        "models": models,
        "confidence_calibrators": confidence_calibrators,
        "metrics": {
            **metrics,
            "macro_r2": macro_r2,
            "calibration_quality": calibration_quality,
        },
        "confidence_hint": confidence_hint,
        "sample_count": int(sum(sample_counts.values())),
        "sample_counts": sample_counts,
        "train_counts": train_counts,
        "test_counts": test_counts,
        "manifest_path": str(manifest_path.resolve()),
        "dataset_root": str(base_dir.resolve()),
        "source_datasets": source_datasets,
        "label_sources": label_sources,
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
    try:
        results[COMORBIDITY_MODEL_NAME] = {
            "status": "trained",
            "bundle": train_comorbidity_model(
                manifest_path=manifest_path,
                dataset_root=dataset_root,
            ),
        }
    except Exception as error:
        results[COMORBIDITY_MODEL_NAME] = {"status": "skipped", "error": str(error)}
    return results


def train_comorbidity_model(
    manifest_path: str | Path,
    dataset_root: str | Path | None = None,
    random_state: int = 42,
    min_samples: int = 12,
) -> dict:
    manifest_path = Path(manifest_path)
    base_dir = Path(dataset_root) if dataset_root else manifest_path.parent
    df = _load_manifest(manifest_path)
    records = df.to_dict(orient="records")

    feature_rows: list[list[float]] = []
    label_rows: list[list[int]] = []
    feature_names: list[str] | None = None
    source_datasets = sorted({str(value).strip() for value in df.get("source_dataset", pd.Series(dtype=str)).dropna().tolist() if str(value).strip()})
    label_sources = sorted({str(value).strip() for value in df.get("label_source", pd.Series(dtype=str)).dropna().tolist() if str(value).strip()})

    for record in records:
        labels = _comorbidity_targets(record)
        if labels is None:
            continue

        modality_results = _build_comorbidity_modality_results(record, base_dir)
        current_feature_names, vector = _comorbidity_feature_vector(modality_results)
        if feature_names is None:
            feature_names = current_feature_names
        feature_rows.append(vector)
        label_rows.append(labels)

    if len(feature_rows) < min_samples:
        raise ValueError(f"At least {min_samples} labeled rows are required to train the comorbidity model.")

    features_x = np.asarray(feature_rows, dtype=float)
    labels_y = np.asarray(label_rows, dtype=int)

    chain_orders = _build_comorbidity_chain_orders(random_state=random_state)
    chain_ensemble = [
        _fit_comorbidity_chain(
            features_x=features_x,
            labels_y=labels_y,
            chain_order=chain_order,
            random_state=random_state + chain_index * 31,
        )
        for chain_index, chain_order in enumerate(chain_orders)
    ]
    pairwise_lift = _comorbidity_pairwise_lift(labels_y)

    raw_probability_rows = []
    for row in features_x:
        chain_probabilities = []
        for chain_spec in chain_ensemble:
            probabilities = _predict_comorbidity_chain_probabilities(chain_spec, list(row))
            chain_probabilities.append([probabilities.get(domain, 0.0) for domain in PREDICTION_DOMAINS])
        raw_probability_rows.append(np.mean(np.asarray(chain_probabilities, dtype=float), axis=0).tolist())

    raw_probabilities_y = np.asarray(raw_probability_rows, dtype=float)
    label_thresholds, threshold_tuning = _tune_comorbidity_thresholds(labels_y, raw_probabilities_y)
    probability_calibrators, probability_calibration_meta = _fit_comorbidity_probability_calibrators(
        labels_y=labels_y,
        probabilities_y=raw_probabilities_y,
        random_state=random_state,
    )

    calibrated_probability_rows = []
    for row in raw_probabilities_y:
        calibrated_row = []
        for index, domain in enumerate(PREDICTION_DOMAINS):
            calibrator = probability_calibrators.get(domain, {})
            score = float(row[index])
            method = str(calibrator.get("method", "constant"))
            model = calibrator.get("model")
            if method == "isotonic" and model is not None:
                calibrated_score = float(model.predict([score])[0])
            elif method == "platt" and model is not None:
                calibrated_score = float(model.predict_proba([[score]])[0][1])
            else:
                calibrated_score = float(calibrator.get("positive_rate", 0.0))
            calibrated_row.append(float(np.clip(calibrated_score, 0.0, 1.0)))
        calibrated_probability_rows.append(calibrated_row)

    calibrated_probabilities_y = np.asarray(calibrated_probability_rows, dtype=float)
    predicted_labels = np.asarray([
        [
            int(calibrated_probabilities_y[row_index, domain_index] >= float(label_thresholds[PREDICTION_DOMAINS[domain_index]]))
            for domain_index in range(len(PREDICTION_DOMAINS))
        ]
        for row_index in range(len(calibrated_probabilities_y))
    ], dtype=int)
    exact_match = float(np.mean(np.all(predicted_labels == labels_y, axis=1)))
    macro_f1 = float(np.mean([
        f1_score(labels_y[:, index], predicted_labels[:, index], zero_division=0)
        for index in range(labels_y.shape[1])
    ]))
    label_accuracy = float(np.mean([
        accuracy_score(labels_y[:, index], predicted_labels[:, index])
        for index in range(labels_y.shape[1])
    ]))

    bundle = {
        "model_type": "classifier_chain_ensemble",
        "domains": list(PREDICTION_DOMAINS),
        "feature_names": feature_names or [],
        "models": chain_ensemble,
        "chain_order": chain_ensemble[0]["chain_order"] if chain_ensemble else list(PREDICTION_DOMAINS),
        "chain_orders": [chain_spec["chain_order"] for chain_spec in chain_ensemble],
        "ensemble_size": int(len(chain_ensemble)),
        "label_thresholds": label_thresholds,
        "label_prevalence": {domain: round(float(value), 3) for domain, value in zip(PREDICTION_DOMAINS, labels_y.mean(axis=0))},
        "pairwise_lift": pairwise_lift,
        "probability_calibrators": probability_calibrators,
        "metrics": {
            "exact_match": exact_match,
            "macro_f1": macro_f1,
            "label_accuracy": label_accuracy,
            "sample_count": int(len(feature_rows)),
            "ensemble_train_accuracy": float(np.mean([chain_spec["train_accuracy"] for chain_spec in chain_ensemble])) if chain_ensemble else 0.0,
            "ensemble_train_f1": float(np.mean([chain_spec["train_f1"] for chain_spec in chain_ensemble])) if chain_ensemble else 0.0,
        },
        "sample_count": int(len(feature_rows)),
        "sample_counts": {domain: int(np.sum(labels_y[:, index])) for index, domain in enumerate(PREDICTION_DOMAINS)},
        "train_counts": {},
        "test_counts": {},
        "manifest_path": str(manifest_path.resolve()),
        "dataset_root": str(base_dir.resolve()),
        "source_datasets": source_datasets,
        "label_sources": label_sources,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "skipped_domains": {},
        "training_strategy": "classifier_chain_ensemble",
        "joint_prediction": {
            "model_type": "classifier_chain_ensemble",
            "ensemble_size": int(len(chain_ensemble)),
            "chain_orders": [chain_spec["chain_order"] for chain_spec in chain_ensemble],
            "label_thresholds": label_thresholds,
            "prediction_rule": "average_probabilities_across_randomized_label_orders",
            "probability_calibration": probability_calibration_meta,
            "threshold_tuning": threshold_tuning,
        },
    }
    save_model_bundle(COMORBIDITY_MODEL_NAME, bundle)
    return bundle


def train_federated_modality_model(
    manifest_paths: list[str | Path],
    modality: str,
    random_state: int = 42,
    domains: list[str] | tuple[str, ...] | None = None,
    min_center_samples: int = 4,
    rounds: int = FEDERATED_DEFAULT_ROUNDS,
    local_epochs: int = FEDERATED_DEFAULT_LOCAL_EPOCHS,
) -> dict:
    modality = modality.lower().strip()
    if modality not in SUPPORTED_MODALITIES:
        raise ValueError(f"Unsupported modality '{modality}'. Expected one of {SUPPORTED_MODALITIES}.")
    if len(manifest_paths) < 2:
        raise ValueError("Federated training requires at least two centre manifests.")

    requested_domains = list(domains or PREDICTION_DOMAINS)
    centers, cached_feature_names = _federated_manifest_cache(manifest_paths, modality)
    source_datasets = sorted({
        str(value).strip()
        for center in centers
        for value in center["frame"].get("source_dataset", pd.Series(dtype=str)).dropna().tolist()
        if str(value).strip()
    })
    label_sources = sorted({
        str(value).strip()
        for center in centers
        for value in center["frame"].get("label_source", pd.Series(dtype=str)).dropna().tolist()
        if str(value).strip()
    })

    models: dict[str, SGDRegressor] = {}
    metrics: dict[str, dict] = {}
    confidence_calibrators: dict[str, dict] = {}
    feature_names: list[str] | None = None
    sample_counts: dict[str, int] = {}
    centre_participation: dict[str, list[dict]] = {}
    skipped_domains: dict[str, str] = {}

    for domain in requested_domains:
        try:
            domain_centers, domain_feature_names = _extract_center_domain_rows(
                centers=centers,
                modality=modality,
                domain=domain,
                feature_names=cached_feature_names,
                min_center_samples=min_center_samples,
            )
        except Exception as error:
            skipped_domains[domain] = str(error)
            continue

        model, domain_metrics, federated_meta = _fit_federated_domain_model(
            centers=domain_centers,
            feature_count=len(domain_feature_names),
            random_state=random_state,
            rounds=rounds,
            local_epochs=local_epochs,
            tolerance=CALIBRATION_TOLERANCE,
        )
        models[domain] = model
        metrics[domain] = domain_metrics
        confidence_calibrators[domain] = federated_meta["calibrator"]
        sample_counts[domain] = int(sum(center["sample_count"] for center in federated_meta["center_metrics"]))
        centre_participation[domain] = federated_meta["center_metrics"]
        if feature_names is None:
            feature_names = domain_feature_names

    if not models or feature_names is None:
        raise ValueError(
            f"No federated domains were trainable for modality '{modality}'. Details: "
            f"{'; '.join(f'{domain}: {reason}' for domain, reason in skipped_domains.items()) or 'no usable centres'}"
        )

    trained_domains = list(models.keys())
    macro_r2 = float(np.mean([metrics[domain]["r2"] for domain in trained_domains]))
    calibration_quality = float(
        np.mean([confidence_calibrators[domain]["metrics"]["calibrated_accuracy"] for domain in trained_domains])
    )
    confidence_hint = float(np.clip(0.3 * ((macro_r2 + 1.0) / 2.0) + 0.7 * calibration_quality, 0.05, 0.99))

    bundle = {
        "modality": modality,
        "domains": trained_domains,
        "feature_names": feature_names,
        "models": models,
        "confidence_calibrators": confidence_calibrators,
        "metrics": {
            **metrics,
            "macro_r2": macro_r2,
            "calibration_quality": calibration_quality,
        },
        "confidence_hint": confidence_hint,
        "sample_count": int(sum(sample_counts.values())),
        "sample_counts": sample_counts,
        "train_counts": {},
        "test_counts": {},
        "manifest_path": None,
        "dataset_root": None,
        "source_datasets": source_datasets,
        "label_sources": label_sources,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "skipped_domains": skipped_domains,
        "training_strategy": "federated",
        "federated": {
            "rounds": int(rounds),
            "local_epochs": int(local_epochs),
            "centre_count": int(len(centers)),
            "centres": [
                {
                    "center_id": center["center_id"],
                    "manifest_path": center["manifest_path"],
                    "dataset_root": center["dataset_root"],
                    "row_count": int(len(center["frame"])),
                }
                for center in centers
            ],
            "domain_participation": centre_participation,
            "privacy": {
                "raw_data_shared": False,
                "aggregation": "weighted_fedavg",
                "shared_artifacts": ["model_parameters", "sample_counts", "aggregate_metrics"],
            },
        },
    }
    save_model_bundle(modality, bundle)
    return bundle


def train_all_federated_models(
    manifest_paths: list[str | Path],
    domains: list[str] | tuple[str, ...] | None = None,
    min_center_samples: int = 4,
    rounds: int = FEDERATED_DEFAULT_ROUNDS,
    local_epochs: int = FEDERATED_DEFAULT_LOCAL_EPOCHS,
) -> dict:
    results = {}
    for modality in SUPPORTED_MODALITIES:
        try:
            results[modality] = {
                "status": "trained",
                "bundle": train_federated_modality_model(
                    manifest_paths=manifest_paths,
                    modality=modality,
                    domains=domains,
                    min_center_samples=min_center_samples,
                    rounds=rounds,
                    local_epochs=local_epochs,
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


def _parse_manifest_list(raw_value: str | None) -> list[str]:
    if not raw_value:
        return []
    return [value.strip() for value in raw_value.split(",") if value.strip()]


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
        choices=(*SUPPORTED_MODALITIES, "comorbidity", "all"),
        default="all",
        help="Train one modality, the joint comorbidity head, or all supported modalities.",
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
    parser.add_argument(
        "--federated-manifests",
        default=None,
        help="Optional comma-separated manifest list, one per health centre, to train using federated averaging.",
    )
    parser.add_argument(
        "--federated-rounds",
        dest="federated_rounds",
        type=int,
        default=FEDERATED_DEFAULT_ROUNDS,
        help="Number of federated communication rounds.",
    )
    parser.add_argument(
        "--local-epochs",
        dest="local_epochs",
        type=int,
        default=FEDERATED_DEFAULT_LOCAL_EPOCHS,
        help="Number of local epochs each centre runs per federated round.",
    )
    parser.add_argument(
        "--min-center-samples",
        dest="min_center_samples",
        type=int,
        default=4,
        help="Minimum usable rows a health centre must contribute for a domain in federated learning.",
    )
    args = parser.parse_args()

    selected_domains = _parse_domains_argument(args.domains)
    federated_manifests = _parse_manifest_list(args.federated_manifests)
    if federated_manifests:
        if args.modality == "all":
            result = train_all_federated_models(
                manifest_paths=federated_manifests,
                domains=selected_domains,
                min_center_samples=args.min_center_samples,
                rounds=args.federated_rounds,
                local_epochs=args.local_epochs,
            )
        else:
            result = {
                args.modality: {
                    "status": "trained",
                    "bundle": train_federated_modality_model(
                        manifest_paths=federated_manifests,
                        modality=args.modality,
                        domains=selected_domains,
                        min_center_samples=args.min_center_samples,
                        rounds=args.federated_rounds,
                        local_epochs=args.local_epochs,
                    ),
                }
            }
    elif args.modality == "comorbidity":
        result = {
            COMORBIDITY_MODEL_NAME: {
                "status": "trained",
                "bundle": train_comorbidity_model(
                    manifest_path=args.manifest,
                    dataset_root=args.dataset_root,
                ),
            }
        }
    elif args.modality == "all":
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
            printable[key]["sample_counts"] = bundle.get("sample_counts", {})
            printable[key]["macro_r2"] = bundle["metrics"].get("macro_r2")
            printable[key]["calibration_quality"] = bundle["metrics"].get("calibration_quality")
            printable[key]["exact_match"] = bundle["metrics"].get("exact_match")
            printable[key]["macro_f1"] = bundle["metrics"].get("macro_f1")
            printable[key]["label_accuracy"] = bundle["metrics"].get("label_accuracy")
            printable[key]["skipped_domains"] = bundle.get("skipped_domains", {})
            printable[key]["training_strategy"] = bundle.get("training_strategy", "centralized")
            printable[key]["federated"] = bundle.get("federated")
    print(json.dumps(printable, indent=2))


if __name__ == "__main__":
    main()
