from __future__ import annotations

import argparse
import json
import importlib
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.ensemble import ExtraTreesClassifier, GradientBoostingClassifier
from sklearn.base import clone
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error, precision_recall_curve, precision_score, recall_score, r2_score
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.utils import resample
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler

try:
    import cv2
except ImportError:
    cv2 = None

if __name__ == "__main__":
    package = sys.modules.get("src.mental_health_screening")
    if package is None:
        package = importlib.import_module("src.mental_health_screening")
    sys.modules.setdefault("mental_health_screening", package)
    sys.modules["mental_health_screening.training"] = sys.modules[__name__]

from .constants import PREDICTION_DOMAINS
from .feature_extract import extract_audio_features, extract_audio_sequence_features, extract_audio_spectrogram_features, extract_image_features, extract_text_features
from .model_features import audio_feature_vector, image_feature_vector, text_feature_vector
from .model_store import load_model_bundle, save_model_bundle
from .predict import COMORBIDITY_MODEL_NAME, COMORBIDITY_MODALITIES, score_audio_features, score_image_features, score_text_features


SUPPORTED_MODALITIES = ("text", "audio", "image", "passive_biomarkers")
CALIBRATION_TOLERANCE = 0.15
FEDERATED_DEFAULT_ROUNDS = 6
FEDERATED_DEFAULT_LOCAL_EPOCHS = 2
COMORBIDITY_CHAIN_ENSEMBLE_SIZE = 1
COMORBIDITY_THRESHOLD_BETA = 2.0
THRESHOLD_CENTER = 0.5
THRESHOLD_CENTER_PENALTY = 0.08
THRESHOLD_MIN = 0.30
THRESHOLD_MAX = 0.70
THRESHOLD_STEP = 0.05
AUDIO_THRESHOLD_BETA = 0.9
AUDIO_DOMAIN_TUNING = {
    "depression": {"beta": 1.80, "min_precision": 0.50},
    "anxiety": {"beta": 1.20, "min_precision": 0.55},
    "stress": {"beta": 0.95, "min_precision": None},
    "sleep_disorder": {"beta": 1.15, "min_precision": 0.55},
    "burnout": {"beta": 1.15, "min_precision": 0.58},
    "loneliness": {"beta": 1.80, "min_precision": 0.50},
    "substance_abuse": {"beta": 1.05, "min_precision": 0.62},
}
PASSIVE_TRAINING_MANIFEST = Path(__file__).resolve().parents[2] / "tmp_datasets" / "passive_training_manifest.jsonl"
PASSIVE_AUTOTRAIN_MIN_NEW_ROWS = 10
PASSIVE_AUTOTRAIN_MIN_TOTAL_ROWS = 25


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
        if path.exists():
            return str(path)
        raw_text = str(path)
        legacy_markers = (
            "Rural Mental Heath Screening AI",
            "Rural Mental Health Screening AI",
        )
        for marker in legacy_markers:
            marker_index = raw_text.lower().find(marker.lower())
            if marker_index != -1:
                relative_tail = raw_text[marker_index + len(marker):].lstrip("\\/")
                candidate = (Path(__file__).resolve().parents[2] / relative_tail).resolve()
                if candidate.exists():
                    return str(candidate)
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


def _load_saved_assessment_records() -> list[dict]:
    data_dir = Path(__file__).resolve().parents[2] / "data"
    records: list[dict] = []
    results_file = data_dir / "screening_results.json"
    if results_file.exists():
        try:
            payload = json.loads(results_file.read_text(encoding="utf-8"))
            if isinstance(payload, list):
                records.extend([record for record in payload if isinstance(record, dict)])
        except Exception:
            records = []
    if records:
        return records

    legacy_db = data_dir / "screening_results.db"
    if not legacy_db.exists():
        return []
    try:
        with sqlite3.connect(legacy_db) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT assessment_id, created_at, profile_json, questionnaire_json, multimodal_json
                FROM assessments
                ORDER BY datetime(created_at) DESC
                """
            ).fetchall()
    except Exception:
        return []

    for row in rows:
        profile = json.loads(row["profile_json"])
        records.append(
            {
                "assessment_id": row["assessment_id"],
                "created_at": row["created_at"],
                "profile": profile,
                "questionnaire": json.loads(row["questionnaire_json"]),
                "multimodal": json.loads(row["multimodal_json"]),
                "patient_key": profile.get("patient_key"),
                "record_origin": profile.get("record_origin", "backend"),
            }
        )
    return records


def _binary_targets(targets: np.ndarray | list[float], threshold: float = 0.5) -> np.ndarray:
    values = np.asarray(targets, dtype=float)
    return (values >= threshold).astype(int)


def _split_train_validation_holdout(
    features_x: np.ndarray,
    targets_y: np.ndarray,
    random_state: int,
    holdout_fraction: float = 0.3,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    binary_targets = _binary_targets(targets_y)
    if len(features_x) < 8:
        return features_x, features_x, features_x, binary_targets, binary_targets, binary_targets

    stratify = binary_targets if len(np.unique(binary_targets)) > 1 and int(np.bincount(binary_targets, minlength=2).min()) >= 2 else None
    holdout_fraction = float(np.clip(holdout_fraction, 0.2, 0.4))
    x_train, x_holdout, y_train, y_holdout = train_test_split(
        features_x,
        binary_targets,
        test_size=min(holdout_fraction, 0.5),
        random_state=random_state,
        stratify=stratify,
    )
    holdout_stratify = y_holdout if len(np.unique(y_holdout)) > 1 and int(np.bincount(y_holdout, minlength=2).min()) >= 2 else None
    if len(x_holdout) < 4:
        return x_train, x_holdout, x_holdout, y_train, y_holdout, y_holdout
    x_val, x_test, y_val, y_test = train_test_split(
        x_holdout,
        y_holdout,
        test_size=0.5,
        random_state=random_state + 1,
        stratify=holdout_stratify,
    )
    return x_train, x_val, x_test, y_train, y_val, y_test


def _balanced_resample_training_data(
    features_x: np.ndarray,
    targets_y: np.ndarray,
    random_state: int,
) -> tuple[np.ndarray, np.ndarray]:
    labels = np.asarray(targets_y, dtype=int)
    if labels.size == 0:
        return features_x, labels

    unique_labels, counts = np.unique(labels, return_counts=True)
    if len(unique_labels) < 2:
        return features_x, labels

    target_count = int(np.max(counts))
    sampled_features: list[np.ndarray] = []
    sampled_labels: list[np.ndarray] = []
    for label in unique_labels:
        label_mask = labels == label
        label_features = features_x[label_mask]
        label_targets = labels[label_mask]
        if len(label_features) == 0:
            continue
        if len(label_features) < target_count:
            label_features, label_targets = resample(
                label_features,
                label_targets,
                replace=True,
                n_samples=target_count,
                random_state=random_state + int(label),
            )
        sampled_features.append(np.asarray(label_features, dtype=float))
        sampled_labels.append(np.asarray(label_targets, dtype=int))

    if not sampled_features:
        return features_x, labels

    balanced_x = np.vstack(sampled_features)
    balanced_y = np.concatenate(sampled_labels)
    rng = np.random.default_rng(random_state)
    order = rng.permutation(len(balanced_x))
    return balanced_x[order], balanced_y[order]


def _binary_metric_score(metrics: dict[str, float]) -> float:
    return (
        0.55 * float(metrics.get("f1", 0.0))
        + 0.25 * float(metrics.get("precision", 0.0))
        + 0.15 * float(metrics.get("accuracy", 0.0))
        + 0.05 * float(metrics.get("recall", 0.0))
    )


def _evaluate_binary_predictions(y_true: np.ndarray, probabilities: np.ndarray, threshold: float = 0.5) -> dict[str, float]:
    predicted_labels = (np.asarray(probabilities, dtype=float) >= float(threshold)).astype(int)
    return {
        "accuracy": float(accuracy_score(y_true, predicted_labels)),
        "precision": float(precision_score(y_true, predicted_labels, zero_division=0)),
        "recall": float(recall_score(y_true, predicted_labels, zero_division=0)),
        "f1": float(f1_score(y_true, predicted_labels, zero_division=0)),
        "mse": float(mean_squared_error(y_true, probabilities)),
        "r2": float(r2_score(y_true, probabilities)),
    }


def _tune_binary_threshold(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    beta: float = 1.0,
    center: float = THRESHOLD_CENTER,
    center_penalty: float = THRESHOLD_CENTER_PENALTY,
    min_precision: float | None = None,
) -> tuple[float, dict[str, float]]:
    targets = np.asarray(y_true, dtype=int)
    scores = np.asarray(probabilities, dtype=float)
    if targets.size == 0 or len(np.unique(targets)) < 2:
        threshold = 0.5
        metrics = _evaluate_binary_predictions(targets, scores, threshold=threshold)
        metrics["threshold"] = threshold
        return threshold, metrics

    precision, recall, threshold_values = precision_recall_curve(targets, scores)
    if len(threshold_values) == 0:
        threshold = 0.5
        metrics = _evaluate_binary_predictions(targets, scores, threshold=threshold)
        metrics["threshold"] = threshold
        return threshold, metrics

    precision = precision[:-1]
    recall = recall[:-1]
    beta_sq = float(beta) ** 2
    numerator = (1.0 + beta_sq) * precision * recall
    denominator = (beta_sq * precision) + recall
    fbeta = np.divide(
        numerator,
        denominator,
        out=np.zeros_like(numerator, dtype=float),
        where=denominator > 1e-9,
    )
    if min_precision is not None:
        feasible = np.where(precision >= float(min_precision))[0]
        if len(feasible) > 0:
            best_index = int(feasible[np.argmax(fbeta[feasible])])
        else:
            best_index = int(np.argmax(precision))
    else:
        best_index = int(np.argmax(fbeta))
    threshold = float(threshold_values[min(best_index, len(threshold_values) - 1)])
    metrics = _evaluate_binary_predictions(targets, scores, threshold=threshold)
    metrics["threshold"] = threshold
    metrics["best_fbeta"] = float(fbeta[best_index]) if len(fbeta) else 0.0
    return metrics["threshold"], metrics


def _evaluate_multilabel_predictions(
    labels_y: np.ndarray,
    probabilities_y: np.ndarray,
    thresholds: dict[str, float] | None = None,
) -> tuple[dict[str, float], np.ndarray]:
    thresholds = thresholds or {domain: 0.5 for domain in PREDICTION_DOMAINS}
    predicted_labels = np.asarray(
        [
            [
                int(probabilities_y[row_index, domain_index] >= float(thresholds.get(PREDICTION_DOMAINS[domain_index], 0.5)))
                for domain_index in range(len(PREDICTION_DOMAINS))
            ]
            for row_index in range(len(probabilities_y))
        ],
        dtype=int,
    )
    metrics = {
        "exact_match": float(np.mean(np.all(predicted_labels == labels_y, axis=1))) if len(labels_y) else 0.0,
        "macro_f1": float(np.mean([
            f1_score(labels_y[:, index], predicted_labels[:, index], zero_division=0)
            for index in range(labels_y.shape[1])
        ])) if labels_y.size else 0.0,
        "label_accuracy": float(np.mean([
            accuracy_score(labels_y[:, index], predicted_labels[:, index])
            for index in range(labels_y.shape[1])
        ])) if labels_y.size else 0.0,
    }
    return metrics, predicted_labels


def _fit_mlp_binary_candidate(
    x_train: np.ndarray,
    y_train: np.ndarray,
    random_state: int,
) -> Pipeline | DummyClassifier:
    class_counts = np.bincount(y_train, minlength=2)
    if int(class_counts.min()) < 2:
        model: Pipeline | DummyClassifier = DummyClassifier(strategy="prior")
        model.fit(x_train, y_train)
        return model

    balanced_x, balanced_y = _balanced_resample_training_data(x_train, y_train, random_state=random_state)
    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "mlp",
                MLPClassifier(
                    hidden_layer_sizes=(48, 24),
                    activation="relu",
                    solver="adam",
                    alpha=3e-4,
                    batch_size="auto",
                    learning_rate="adaptive",
                    learning_rate_init=3e-4,
                    max_iter=220,
                    early_stopping=True,
                    validation_fraction=0.2,
                    n_iter_no_change=15,
                    random_state=random_state,
                ),
            ),
        ]
    )
    model.fit(balanced_x, balanced_y)
    return model


def _fit_deep_binary_candidate(
    x_train: np.ndarray,
    y_train: np.ndarray,
    random_state: int,
) -> Pipeline | DummyClassifier:
    class_counts = np.bincount(y_train, minlength=2)
    if int(class_counts.min()) < 2:
        model: Pipeline | DummyClassifier = DummyClassifier(strategy="prior")
        model.fit(x_train, y_train)
        return model

    balanced_x, balanced_y = _balanced_resample_training_data(x_train, y_train, random_state=random_state)
    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "mlp",
                MLPClassifier(
                    hidden_layer_sizes=(128, 64, 32),
                    activation="relu",
                    solver="adam",
                    alpha=1e-3,
                    batch_size="auto",
                    learning_rate="adaptive",
                    learning_rate_init=2e-4,
                    max_iter=260,
                    early_stopping=True,
                    validation_fraction=0.2,
                    n_iter_no_change=18,
                    random_state=random_state,
                ),
            ),
        ]
    )
    model.fit(balanced_x, balanced_y)
    return model


def _fit_logistic_binary_candidate(
    x_train: np.ndarray,
    y_train: np.ndarray,
    random_state: int,
) -> Pipeline | DummyClassifier:
    class_counts = np.bincount(y_train, minlength=2)
    if int(class_counts.min()) < 2:
        model: Pipeline | DummyClassifier = DummyClassifier(strategy="prior")
        model.fit(x_train, y_train)
        return model

    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "logistic",
                LogisticRegression(
                    max_iter=4000,
                    class_weight="balanced",
                    solver="liblinear",
                    C=0.7,
                    random_state=random_state,
                ),
            ),
        ]
    )
    model.fit(x_train, y_train)
    return model


def _fit_rf_binary_candidate(
    x_train: np.ndarray,
    y_train: np.ndarray,
    random_state: int,
) -> RandomForestClassifier | DummyClassifier:
    class_counts = np.bincount(y_train, minlength=2)
    if int(class_counts.min()) < 2:
        model: RandomForestClassifier | DummyClassifier = DummyClassifier(strategy="prior")
        model.fit(x_train, y_train)
        return model

    model = RandomForestClassifier(
        n_estimators=500,
        random_state=random_state,
        class_weight="balanced_subsample",
        min_samples_leaf=2,
        min_samples_split=4,
        max_depth=12,
        max_features="sqrt",
        n_jobs=-1,
    )
    model.fit(x_train, y_train)
    return model


def _fit_extra_trees_binary_candidate(
    x_train: np.ndarray,
    y_train: np.ndarray,
    random_state: int,
) -> ExtraTreesClassifier | DummyClassifier:
    class_counts = np.bincount(y_train, minlength=2)
    if int(class_counts.min()) < 2:
        model: ExtraTreesClassifier | DummyClassifier = DummyClassifier(strategy="prior")
        model.fit(x_train, y_train)
        return model

    model = ExtraTreesClassifier(
        n_estimators=600,
        random_state=random_state,
        class_weight="balanced",
        min_samples_leaf=2,
        min_samples_split=4,
        max_depth=14,
        max_features="sqrt",
        bootstrap=False,
        n_jobs=-1,
    )
    model.fit(x_train, y_train)
    return model


def _fit_gradient_boosting_binary_candidate(
    x_train: np.ndarray,
    y_train: np.ndarray,
    random_state: int,
) -> GradientBoostingClassifier | DummyClassifier:
    class_counts = np.bincount(y_train, minlength=2)
    if int(class_counts.min()) < 2:
        model: GradientBoostingClassifier | DummyClassifier = DummyClassifier(strategy="prior")
        model.fit(x_train, y_train)
        return model

    balanced_x, balanced_y = _balanced_resample_training_data(x_train, y_train, random_state=random_state)
    model = GradientBoostingClassifier(
        n_estimators=240,
        learning_rate=0.05,
        max_depth=2,
        subsample=0.85,
        min_samples_leaf=6,
        min_samples_split=10,
        random_state=random_state,
    )
    model.fit(balanced_x, balanced_y)
    return model


def _fit_selected_binary_model(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_test: np.ndarray,
    y_test: np.ndarray,
    random_state: int,
    allow_deep_candidate: bool = True,
    threshold_beta: float = 1.0,
    min_precision: float | None = None,
) -> tuple[RandomForestClassifier | DummyClassifier | Pipeline, dict, str, dict, np.ndarray, float]:
    candidates: list[tuple[str, object]] = [
        ("logistic", _fit_logistic_binary_candidate(x_train, y_train, random_state=random_state)),
        ("random_forest", _fit_rf_binary_candidate(x_train, y_train, random_state=random_state)),
        ("extra_trees", _fit_extra_trees_binary_candidate(x_train, y_train, random_state=random_state)),
        ("gradient_boosting", _fit_gradient_boosting_binary_candidate(x_train, y_train, random_state=random_state)),
    ]
    if allow_deep_candidate:
        candidates.append(("mlp", _fit_mlp_binary_candidate(x_train, y_train, random_state=random_state)))
        candidates.append(("deep_mlp", _fit_deep_binary_candidate(x_train, y_train, random_state=random_state)))

    evaluated: list[tuple[str, object, dict, np.ndarray, float]] = []
    for name, model in candidates:
        probabilities, prediction_std = _forest_prediction_stats(model, x_test)
        threshold, tuned_metrics = _tune_binary_threshold(
            y_test,
            probabilities,
            beta=threshold_beta,
            min_precision=min_precision,
        )
        metrics = dict(tuned_metrics)
        metrics["threshold"] = threshold
        evaluated.append((name, model, metrics, prediction_std, threshold))

    best_name, best_model, best_metrics, best_prediction_std, best_threshold = max(
        evaluated,
        key=lambda item: (_binary_metric_score(item[2]), item[2].get("f1", 0.0), item[2].get("precision", 0.0), item[2].get("accuracy", 0.0)),
    )
    candidate_metrics = {
        name: dict(metrics)
        for name, _, metrics, _, _ in evaluated
    }
    return best_model, dict(best_metrics), best_name, candidate_metrics, best_prediction_std, float(best_threshold)


def _fit_selected_chain_binary_model(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_eval: np.ndarray,
    y_eval: np.ndarray,
    random_state: int,
) -> tuple[object, dict, str, dict]:
    class_counts = np.bincount(y_train, minlength=2)
    candidates: list[tuple[str, object]] = []
    if int(class_counts.min()) >= 2:
        candidates.append(("logistic", _fit_logistic_binary_candidate(x_train, y_train, random_state=random_state)))
        candidates.append(("extra_trees", _fit_extra_trees_binary_candidate(x_train, y_train, random_state=random_state)))
        candidates.append(("mlp", _fit_mlp_binary_candidate(x_train, y_train, random_state=random_state)))
    else:
        fallback = DummyClassifier(strategy="prior")
        fallback.fit(x_train, y_train)
        candidates.append(("dummy", fallback))

    evaluated: list[tuple[str, object, dict]] = []
    for name, model in candidates:
        probabilities, _ = _forest_prediction_stats(model, x_eval)
        threshold, metrics = _tune_binary_threshold(y_eval, probabilities, beta=1.0)
        metrics["threshold"] = threshold
        evaluated.append((name, model, metrics))

    best_name, best_model, best_metrics = max(
        evaluated,
        key=lambda item: (_binary_metric_score(item[2]), item[2].get("f1", 0.0), item[2].get("precision", 0.0), item[2].get("accuracy", 0.0)),
    )
    candidate_metrics = {name: metrics for name, _, metrics in evaluated}
    return best_model, best_metrics, best_name, candidate_metrics


def _fit_comorbidity_chain_binary_model(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_eval: np.ndarray,
    y_eval: np.ndarray,
    random_state: int,
) -> tuple[object, dict, str, dict]:
    class_counts = np.bincount(y_train, minlength=2)
    if int(class_counts.min()) < 2:
        fallback = DummyClassifier(strategy="prior")
        fallback.fit(x_train, y_train)
        probabilities = (
            np.asarray(fallback.predict_proba(x_eval), dtype=float)[:, -1]
            if hasattr(fallback, "predict_proba")
            else np.asarray(fallback.predict(x_eval), dtype=float)
        )
        metrics = _evaluate_binary_predictions(np.asarray(y_eval, dtype=int), probabilities, threshold=0.5)
        metrics["threshold"] = 0.5
        return fallback, metrics, "dummy", {"dummy": metrics}

    balanced_x, balanced_y = _balanced_resample_training_data(x_train, y_train, random_state=random_state)
    candidates: list[tuple[str, object]] = [
        ("logistic", _fit_logistic_binary_candidate(balanced_x, balanced_y, random_state=random_state)),
        (
            "extra_trees",
            ExtraTreesClassifier(
                n_estimators=140,
                random_state=random_state,
                class_weight="balanced",
                min_samples_leaf=2,
                min_samples_split=4,
                max_depth=8,
                max_features="sqrt",
                bootstrap=False,
                n_jobs=-1,
            ),
        ),
    ]
    candidates[1][1].fit(balanced_x, balanced_y)

    evaluated: list[tuple[str, object, dict]] = []
    for name, model in candidates:
        probabilities, _ = _forest_prediction_stats(model, x_eval)
        threshold, metrics = _tune_binary_threshold(y_eval, probabilities, beta=1.0)
        metrics["threshold"] = threshold
        evaluated.append((name, model, metrics))

    best_name, best_model, best_metrics = max(
        evaluated,
        key=lambda item: (_binary_metric_score(item[2]), item[2].get("f1", 0.0), item[2].get("precision", 0.0), item[2].get("accuracy", 0.0)),
    )
    candidate_metrics = {name: metrics for name, _, metrics in evaluated}
    return best_model, best_metrics, best_name, candidate_metrics


class _TextRecordDataset(Dataset):
    def __init__(self, texts: list[str], labels: np.ndarray):
        self.texts = texts
        self.labels = np.asarray(labels, dtype=float)

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, index: int) -> tuple[str, np.ndarray]:
        return self.texts[index], self.labels[index]


class _TextTransformerClassifier(nn.Module):
    def __init__(self, encoder, num_labels: int, dropout: float = 0.2):
        super().__init__()
        self.encoder = encoder
        hidden_size = int(getattr(encoder.config, "hidden_size", 768))
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(hidden_size, num_labels)

    def forward(self, input_ids, attention_mask):
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        hidden_state = outputs.last_hidden_state[:, 0, :]
        logits = self.classifier(self.dropout(hidden_state))
        return logits


_TextTransformerClassifier.__module__ = "mental_health_screening.training"


def _select_text_transformer_rows(
    texts: list[str],
    labels: np.ndarray,
    max_rows: int,
    random_state: int,
) -> tuple[list[str], np.ndarray, list[int]]:
    if len(texts) <= max_rows:
        return texts, labels, list(range(len(texts)))

    labels = np.asarray(labels, dtype=int)
    positive_mask = labels.sum(axis=1) > 0
    positive_indices = np.where(positive_mask)[0]
    negative_indices = np.where(~positive_mask)[0]
    rng = np.random.default_rng(random_state)

    selected_indices: list[int] = []
    if len(positive_indices):
        selected_indices.extend(positive_indices.tolist())
    remaining = max_rows - len(selected_indices)
    if remaining > 0 and len(negative_indices):
        replace = len(negative_indices) < remaining
        sampled_negatives = rng.choice(negative_indices, size=remaining, replace=replace)
        selected_indices.extend(np.asarray(sampled_negatives, dtype=int).tolist())

    if len(selected_indices) < max_rows:
        missing = max_rows - len(selected_indices)
        pool = np.arange(len(texts))
        sampled = rng.choice(pool, size=missing, replace=False if len(pool) >= missing else True)
        selected_indices.extend(np.asarray(sampled, dtype=int).tolist())

    selected_indices = list(dict.fromkeys(selected_indices))
    if len(selected_indices) > max_rows:
        selected_indices = rng.choice(selected_indices, size=max_rows, replace=False).tolist()

    selected_texts = [texts[index] for index in selected_indices]
    selected_labels = labels[selected_indices]
    return selected_texts, selected_labels, selected_indices


def _partition_text_transformer_rows(
    source_splits: list[str],
    random_state: int,
) -> tuple[list[int], list[int], list[int]]:
    train_indices = [index for index, split in enumerate(source_splits) if split in {"train", "full"}]
    eval_indices = [index for index, split in enumerate(source_splits) if split == "dev"]
    test_indices = [index for index, split in enumerate(source_splits) if split == "test"]

    if not train_indices and not eval_indices and not test_indices:
        return [], [], []

    if not train_indices:
        pool = np.arange(len(source_splits))
        rng = np.random.default_rng(random_state)
        indices = rng.permutation(pool)
        split_index = max(1, int(len(indices) * 0.8))
        train_indices = indices[:split_index].tolist()
        eval_indices = indices[split_index:].tolist()
        test_indices = eval_indices[:]
        return train_indices, eval_indices, test_indices

    if not eval_indices and test_indices:
        eval_indices = test_indices[:]
    if not test_indices and eval_indices:
        test_indices = eval_indices[:]
    if not eval_indices:
        pool = np.asarray(train_indices, dtype=int)
        rng = np.random.default_rng(random_state)
        indices = rng.permutation(pool)
        split_index = max(1, int(len(indices) * 0.8))
        train_indices = indices[:split_index].tolist()
        eval_indices = indices[split_index:].tolist()
        test_indices = eval_indices[:]
        return train_indices, eval_indices, test_indices
    if not test_indices:
        test_indices = eval_indices[:]

    return train_indices, eval_indices, test_indices


def _train_text_transformer_classifier(
    texts: list[str],
    labels: np.ndarray,
    source_splits: list[str] | None,
    random_state: int,
    max_rows: int = 8000,
    batch_size: int = 8,
    epochs: int = 2,
    learning_rate: float = 2e-5,
) -> dict:
    from .feature_extract import _load_transformer_encoder

    np.random.seed(random_state)
    torch.manual_seed(random_state)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(random_state)

    selected_texts, selected_labels, selected_indices = _select_text_transformer_rows(
        texts=texts,
        labels=labels,
        max_rows=max_rows,
        random_state=random_state,
    )
    selected_source_splits = [
        str(source_splits[index]).strip().lower() if source_splits and index < len(source_splits) else ""
        for index in selected_indices
    ]
    if len(selected_texts) < 32:
        raise ValueError("Not enough usable text rows to train a transformer classifier.")

    encoder_bundle = _load_transformer_encoder("english")
    if encoder_bundle is None:
        raise ValueError("No local transformer encoder was available for text training.")

    tokenizer = encoder_bundle["tokenizer"]
    encoder = encoder_bundle["model"]
    encoder.train()
    for parameter in encoder.parameters():
        parameter.requires_grad = False
    if hasattr(encoder, "transformer") and hasattr(encoder.transformer, "layer"):
        for layer in encoder.transformer.layer[-2:]:
            for parameter in layer.parameters():
                parameter.requires_grad = True
    for parameter in getattr(encoder, "embeddings", []).parameters() if hasattr(encoder, "embeddings") else []:
        parameter.requires_grad = False

    train_indices, eval_indices, test_indices = _partition_text_transformer_rows(
        source_splits=selected_source_splits,
        random_state=random_state,
    )
    if not train_indices or not eval_indices:
        rng = np.random.default_rng(random_state)
        indices = rng.permutation(len(selected_texts))
        split_index = max(1, int(len(indices) * 0.8))
        train_indices = indices[:split_index].tolist()
        eval_indices = indices[split_index:].tolist() if split_index < len(indices) else indices[: max(1, len(indices) // 5)].tolist()
        test_indices = eval_indices[:]

    train_texts = [selected_texts[index] for index in train_indices]
    train_labels = np.asarray(selected_labels[train_indices], dtype=float)
    eval_texts = [selected_texts[index] for index in eval_indices]
    eval_labels = np.asarray(selected_labels[eval_indices], dtype=float)
    final_texts = [selected_texts[index] for index in test_indices] if test_indices else list(eval_texts)
    final_labels = np.asarray(selected_labels[test_indices], dtype=float) if test_indices else np.asarray(eval_labels, dtype=float)

    def collate_fn(batch: list[tuple[str, np.ndarray]]) -> tuple[dict[str, torch.Tensor], torch.Tensor]:
        batch_texts = [item[0] for item in batch]
        batch_labels = torch.tensor(np.asarray([item[1] for item in batch], dtype=float), dtype=torch.float32)
        encoded = tokenizer(
            batch_texts,
            truncation=True,
            padding=True,
            max_length=128,
            return_tensors="pt",
        )
        return encoded, batch_labels

    train_loader = DataLoader(
        _TextRecordDataset(train_texts, train_labels),
        batch_size=batch_size,
        shuffle=True,
        collate_fn=collate_fn,
    )
    eval_loader = DataLoader(
        _TextRecordDataset(eval_texts, eval_labels),
        batch_size=batch_size,
        shuffle=False,
        collate_fn=collate_fn,
    )

    model = _TextTransformerClassifier(encoder=encoder, num_labels=len(PREDICTION_DOMAINS))
    model = model.to("cpu")
    optimizer = torch.optim.AdamW(
        (parameter for parameter in model.parameters() if parameter.requires_grad),
        lr=learning_rate,
        weight_decay=0.01,
    )

    positive_counts = np.clip(train_labels.sum(axis=0), 1.0, None)
    negative_counts = np.clip(len(train_labels) - positive_counts, 1.0, None)
    pos_weight = torch.tensor(negative_counts / positive_counts, dtype=torch.float32)
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

    best_state = None
    best_score = -1.0
    best_eval_probabilities = None
    best_eval_labels = None
    patience = 2
    epochs_without_improvement = 0

    for _ in range(epochs):
        model.train()
        for encoded, batch_labels in train_loader:
            optimizer.zero_grad(set_to_none=True)
            logits = model(encoded["input_ids"], encoded["attention_mask"])
            loss = loss_fn(logits, batch_labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

        model.eval()
        eval_probabilities: list[np.ndarray] = []
        eval_true: list[np.ndarray] = []
        with torch.no_grad():
            for encoded, batch_labels in eval_loader:
                logits = model(encoded["input_ids"], encoded["attention_mask"])
                probabilities = torch.sigmoid(logits).cpu().numpy()
                eval_probabilities.append(probabilities)
                eval_true.append(batch_labels.cpu().numpy())
        if not eval_probabilities:
            continue
        probabilities_y = np.vstack(eval_probabilities)
        labels_y = np.vstack(eval_true)
        thresholds, _ = _tune_comorbidity_thresholds(labels_y, probabilities_y)
        metrics, _ = _evaluate_multilabel_predictions(labels_y, probabilities_y, thresholds=thresholds)
        score = _binary_metric_score(
            {
                "f1": metrics["macro_f1"],
                "precision": metrics["label_accuracy"],
                "accuracy": metrics["exact_match"],
                "recall": metrics["macro_f1"],
            }
        )
        if score > best_score:
            best_score = score
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
            best_eval_probabilities = probabilities_y
            best_eval_labels = labels_y
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= patience:
                break

    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()

    if best_eval_probabilities is None or best_eval_labels is None:
        raise ValueError("Transformer training did not produce validation predictions.")

    model.eval()
    calibration_thresholds, threshold_tuning = _tune_comorbidity_thresholds(
        best_eval_labels,
        best_eval_probabilities,
        beta=0.5,
        min_precision=0.6,
    )

    test_probabilities: list[np.ndarray] = []
    test_true: list[np.ndarray] = []
    test_loader = DataLoader(
        _TextRecordDataset(final_texts, final_labels),
        batch_size=batch_size,
        shuffle=False,
        collate_fn=collate_fn,
    )
    with torch.no_grad():
        for encoded, batch_labels in test_loader:
            logits = model(encoded["input_ids"], encoded["attention_mask"])
            probabilities = torch.sigmoid(logits).cpu().numpy()
            test_probabilities.append(probabilities)
            test_true.append(batch_labels.cpu().numpy())
    if test_probabilities:
        test_probabilities_y = np.vstack(test_probabilities)
        test_labels_y = np.vstack(test_true)
    else:
        test_probabilities_y = best_eval_probabilities
        test_labels_y = best_eval_labels

    metrics, predicted_labels = _evaluate_multilabel_predictions(test_labels_y, test_probabilities_y, thresholds=calibration_thresholds)

    bundle = {
        "model_type": "text_transformer_multilabel",
        "modality": "text_transformer",
        "domains": list(PREDICTION_DOMAINS),
        "feature_names": [],
        "model": model.cpu(),
        "tokenizer": tokenizer,
        "transformer": {
            "model_name": encoder_bundle["model_name"],
            "model_family": encoder_bundle["model_family"],
            "language": encoder_bundle["language"],
            "preferred_family": encoder_bundle.get("preferred_family"),
            "max_rows": int(max_rows),
            "batch_size": int(batch_size),
            "epochs": int(epochs),
            "learning_rate": float(learning_rate),
        },
        "label_thresholds": calibration_thresholds,
        "metrics": {
            **metrics,
            "sample_count": int(len(selected_texts)),
        },
        "sample_count": int(len(selected_texts)),
        "sample_counts": {domain: int(np.sum(selected_labels[:, index])) for index, domain in enumerate(PREDICTION_DOMAINS)},
        "train_counts": {},
        "test_counts": {},
        "manifest_path": None,
        "dataset_root": None,
        "source_datasets": [],
        "label_sources": [],
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "skipped_domains": {},
        "training_strategy": "transformer_finetune",
        "joint_prediction": {
            "model_type": "text_transformer_multilabel",
            "label_thresholds": calibration_thresholds,
            "threshold_tuning": threshold_tuning,
        },
    }
    save_model_bundle("text_transformer", bundle)
    return bundle


class _AudioSequenceDataset(Dataset):
    def __init__(self, sequences: list[np.ndarray], labels: np.ndarray):
        self.sequences = sequences
        self.labels = np.asarray(labels, dtype=float)

    def __len__(self) -> int:
        return len(self.sequences)

    def __getitem__(self, index: int) -> tuple[np.ndarray, np.ndarray]:
        return self.sequences[index], self.labels[index]


class _AudioSequenceBiLSTM(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, num_layers: int, num_labels: int, dropout: float = 0.25):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0.0,
            bidirectional=True,
            batch_first=True,
        )
        self.dropout = nn.Dropout(dropout)
        self.projection = nn.Sequential(
            nn.Linear(hidden_size * 6, hidden_size * 2),
            nn.ReLU(),
            nn.Dropout(dropout),
        )
        self.classifier = nn.Linear(hidden_size * 2, num_labels)

    def forward(self, padded_sequences: torch.Tensor, lengths: torch.Tensor) -> torch.Tensor:
        packed = torch.nn.utils.rnn.pack_padded_sequence(
            padded_sequences,
            lengths.cpu(),
            batch_first=True,
            enforce_sorted=False,
        )
        packed_output, (hidden_state, _) = self.lstm(packed)
        forward_hidden = hidden_state[-2]
        backward_hidden = hidden_state[-1]
        padded_output, _ = torch.nn.utils.rnn.pad_packed_sequence(packed_output, batch_first=True)
        max_length = int(padded_output.shape[1])
        time_index = torch.arange(max_length, device=padded_output.device).unsqueeze(0)
        mask = time_index < lengths.unsqueeze(1)
        mask_3d = mask.unsqueeze(-1)
        masked_output = padded_output * mask_3d
        pooled_mean = masked_output.sum(dim=1) / lengths.clamp(min=1).unsqueeze(1).to(padded_output.dtype)
        pooled_max = padded_output.masked_fill(~mask_3d, float("-inf")).max(dim=1).values
        pooled_max = torch.where(torch.isfinite(pooled_max), pooled_max, torch.zeros_like(pooled_max))
        features = torch.cat([forward_hidden, backward_hidden, pooled_mean, pooled_max], dim=-1)
        return self.classifier(self.projection(self.dropout(features)))


_AudioSequenceBiLSTM.__module__ = "mental_health_screening.training"


def _normalize_sequence_collection(sequences: list[np.ndarray]) -> tuple[list[np.ndarray], dict[str, list[float]]]:
    stacked = np.vstack(sequences).astype(np.float32)
    mean = stacked.mean(axis=0)
    std = stacked.std(axis=0)
    std = np.where(std < 1e-6, 1.0, std)
    normalized = [((sequence - mean) / std).astype(np.float32) for sequence in sequences]
    return normalized, {
        "mean": mean.astype(np.float32).tolist(),
        "std": std.astype(np.float32).tolist(),
    }


def _augment_audio_sequence(sequence: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    augmented = np.asarray(sequence, dtype=np.float32).copy()
    if augmented.size == 0:
        return augmented

    # Keep the perturbations small so emotion structure survives while the model
    # sees more varied acoustic contours.
    feature_scale = rng.normal(1.0, 0.03, size=(1, augmented.shape[1])).astype(np.float32)
    augmented = augmented * feature_scale
    augmented += rng.normal(0.0, 0.015, size=augmented.shape).astype(np.float32)

    if augmented.shape[0] > 8:
        shift = int(rng.integers(-4, 5))
        augmented = np.roll(augmented, shift=shift, axis=0)

        if rng.random() < 0.35:
            mask_width = int(rng.integers(2, max(3, augmented.shape[0] // 10)))
            mask_start = int(rng.integers(0, max(1, augmented.shape[0] - mask_width)))
            augmented[mask_start : mask_start + mask_width] *= 0.92

    return augmented.astype(np.float32)


def _build_sequence_sampler_weights(labels: np.ndarray) -> list[float]:
    labels = np.asarray(labels, dtype=int)
    if labels.size == 0:
        return []

    prevalence = np.clip(labels.mean(axis=0), 1e-3, 1.0)
    inverse_prevalence = 1.0 / prevalence
    weights: list[float] = []
    for row in labels:
        positive_domains = np.where(row > 0)[0]
        if len(positive_domains):
            weight = 1.0 + float(np.sum(inverse_prevalence[positive_domains])) / float(len(positive_domains))
        else:
            weight = 1.0
        weights.append(float(np.clip(weight, 0.5, 8.0)))
    return weights


def _train_audio_sequence_model(
    manifest_path: str | Path,
    dataset_root: str | Path | None = None,
    random_state: int = 42,
    max_rows: int = 1920,
    batch_size: int = 16,
    epochs: int = 10,
    learning_rate: float = 8e-4,
    max_frames: int = 192,
) -> dict:
    manifest_path = Path(manifest_path)
    base_dir = Path(dataset_root) if dataset_root else manifest_path.parent
    np.random.seed(random_state)
    torch.manual_seed(random_state)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(random_state)
    df = _load_manifest(manifest_path)
    records = [
        record
        for record in df.to_dict(orient="records")
        if _resolve_path(base_dir, record.get("audio_path")) and _comorbidity_targets(record) is not None
    ]
    print(f"[audio_sequence] loaded {len(df)} manifest rows", flush=True)
    print(f"[audio_sequence] usable audio rows {len(records)}", flush=True)
    if max_rows > 0 and len(records) > max_rows:
        rng = np.random.default_rng(random_state)
        selected_indices = np.sort(rng.choice(len(records), size=max_rows, replace=False))
        records = [records[index] for index in selected_indices]
    print(f"[audio_sequence] sampling {len(records)} rows", flush=True)

    sequences: list[np.ndarray] = []
    labels: list[list[int]] = []
    source_datasets = sorted({str(value).strip() for value in df.get("source_dataset", pd.Series(dtype=str)).dropna().tolist() if str(value).strip()})
    label_sources = sorted({str(value).strip() for value in df.get("label_source", pd.Series(dtype=str)).dropna().tolist() if str(value).strip()})

    for record in records:
        audio_path = _resolve_path(base_dir, record.get("audio_path"))
        if not audio_path:
            continue
        targets = _comorbidity_targets(record)
        if targets is None:
            continue
        if len(sequences) and len(sequences) % 10 == 0:
            print(f"[audio_sequence] extracted {len(sequences)} sequences", flush=True)
        extracted = extract_audio_sequence_features(audio_path, max_frames=max_frames, include_mfcc=False)
        if not extracted.get("available"):
            continue
        sequences.append(np.asarray(extracted["sequence_features"], dtype=np.float32))
        labels.append(targets)
    print(f"[audio_sequence] usable sequences {len(sequences)}", flush=True)

    if len(sequences) < 32:
        raise ValueError("At least 32 usable audio rows are required to train the sequence model.")

    labels_array = np.asarray(labels, dtype=int)
    rng = np.random.default_rng(random_state)
    indices = rng.permutation(len(sequences))
    split_index = max(1, int(len(indices) * 0.8))
    train_indices = indices[:split_index]
    eval_indices = indices[split_index:] if split_index < len(indices) else indices[: max(1, len(indices) // 5)]

    train_sequences = [sequences[index] for index in train_indices]
    train_labels = labels_array[train_indices]
    eval_sequences = [sequences[index] for index in eval_indices]
    eval_labels = labels_array[eval_indices]

    augmentation_rng = np.random.default_rng(random_state + 101)
    augmented_train_sequences: list[np.ndarray] = []
    augmented_train_labels: list[np.ndarray] = []
    for sequence, label in zip(train_sequences, train_labels, strict=False):
        augmented_train_sequences.append(np.asarray(sequence, dtype=np.float32))
        augmented_train_labels.append(np.asarray(label, dtype=int))
        augmented_train_sequences.append(_augment_audio_sequence(sequence, augmentation_rng))
        augmented_train_labels.append(np.asarray(label, dtype=int))
    train_sequences = augmented_train_sequences
    train_labels = np.asarray(augmented_train_labels, dtype=int)

    def collate_fn(batch: list[tuple[np.ndarray, np.ndarray]]) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        seq_tensors = [torch.tensor(item[0], dtype=torch.float32) for item in batch]
        lengths = torch.tensor([tensor.shape[0] for tensor in seq_tensors], dtype=torch.long)
        padded = torch.nn.utils.rnn.pad_sequence(seq_tensors, batch_first=True)
        label_tensor = torch.tensor(np.asarray([item[1] for item in batch], dtype=float), dtype=torch.float32)
        return padded, lengths, label_tensor

    sampler_weights = _build_sequence_sampler_weights(train_labels)
    train_sampler = WeightedRandomSampler(
        weights=torch.tensor(sampler_weights, dtype=torch.double),
        num_samples=max(len(sampler_weights), 1),
        replacement=True,
    )

    train_sequences, normalization = _normalize_sequence_collection(train_sequences)
    eval_sequences = [((sequence - np.asarray(normalization["mean"], dtype=np.float32)) / np.asarray(normalization["std"], dtype=np.float32)).astype(np.float32) for sequence in eval_sequences]

    train_loader = DataLoader(
        _AudioSequenceDataset(train_sequences, train_labels),
        batch_size=batch_size,
        sampler=train_sampler,
        collate_fn=collate_fn,
    )
    eval_loader = DataLoader(
        _AudioSequenceDataset(eval_sequences, eval_labels),
        batch_size=batch_size,
        shuffle=False,
        collate_fn=collate_fn,
    )

    model = _AudioSequenceBiLSTM(
        input_size=int(train_sequences[0].shape[1]),
        hidden_size=128,
        num_layers=2,
        num_labels=len(PREDICTION_DOMAINS),
        dropout=0.35,
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4)
    positive_counts = np.clip(train_labels.sum(axis=0), 1.0, None)
    negative_counts = np.clip(len(train_labels) - positive_counts, 1.0, None)
    pos_weight = torch.tensor(negative_counts / positive_counts, dtype=torch.float32)

    best_state = None
    best_score = -1.0
    best_eval_probs = None
    best_eval_labels = None
    patience = 3
    epochs_without_improvement = 0

    for epoch_index in range(epochs):
        model.train()
        for padded, lengths, batch_labels in train_loader:
            optimizer.zero_grad(set_to_none=True)
            logits = model(padded, lengths)
            bce_loss = nn.functional.binary_cross_entropy_with_logits(logits, batch_labels, reduction="none", pos_weight=pos_weight)
            probabilities = torch.sigmoid(logits)
            pt = probabilities * batch_labels + (1.0 - probabilities) * (1.0 - batch_labels)
            focal_weight = torch.pow(1.0 - pt, 1.5)
            loss = (bce_loss * focal_weight).mean()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

        model.eval()
        eval_probs: list[np.ndarray] = []
        eval_true: list[np.ndarray] = []
        with torch.no_grad():
            for padded, lengths, batch_labels in eval_loader:
                logits = model(padded, lengths)
                probs = torch.sigmoid(logits).cpu().numpy()
                eval_probs.append(probs)
                eval_true.append(batch_labels.cpu().numpy())
        if not eval_probs:
            continue
        probabilities_y = np.vstack(eval_probs)
        labels_y = np.vstack(eval_true)
        epoch_thresholds, _ = _tune_comorbidity_thresholds(labels_y, probabilities_y)
        metrics, _ = _evaluate_multilabel_predictions(labels_y, probabilities_y, thresholds=epoch_thresholds)
        print(f"[audio_sequence] epoch {epoch_index + 1}/{epochs} metrics {metrics}", flush=True)
        score = metrics["macro_f1"] + 0.25 * metrics["label_accuracy"] + 0.1 * metrics["exact_match"]
        if score > best_score:
            best_score = score
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
            best_eval_probs = probabilities_y
            best_eval_labels = labels_y
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= patience:
                break

    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()

    if best_eval_probs is None or best_eval_labels is None:
        raise ValueError("Audio sequence training did not produce validation predictions.")

    thresholds, threshold_tuning = _tune_comorbidity_thresholds(best_eval_labels, best_eval_probs)
    metrics, _ = _evaluate_multilabel_predictions(best_eval_labels, best_eval_probs, thresholds=thresholds)

    bundle = {
        "model_type": "audio_bilstm_multilabel",
        "modality": "audio_sequence",
        "domains": list(PREDICTION_DOMAINS),
        "feature_names": [
            "chunk_mean",
            "chunk_std",
            "chunk_max",
            "chunk_min",
            "chunk_energy",
            "chunk_rms",
            "chunk_zero_crossing",
            "chunk_abs_mean",
            "chunk_spectral_centroid",
            "chunk_spectral_bandwidth",
            "chunk_spectral_flatness",
        ],
        "model": model.cpu(),
        "sequence_config": {
            "input_size": int(train_sequences[0].shape[1]),
            "hidden_size": 128,
            "num_layers": 2,
            "batch_size": int(batch_size),
            "epochs": int(epochs),
            "learning_rate": float(learning_rate),
            "max_rows": int(max_rows),
            "max_frames": int(max_frames),
            "feature_mode": "fast",
        },
        "sequence_normalization": normalization,
        "label_thresholds": thresholds,
        "metrics": {
            **metrics,
            "sample_count": int(len(sequences)),
        },
        "sample_count": int(len(sequences)),
        "sample_counts": {domain: int(np.sum(labels_array[:, index])) for index, domain in enumerate(PREDICTION_DOMAINS)},
        "train_counts": {},
        "test_counts": {},
        "manifest_path": None,
        "dataset_root": None,
        "source_datasets": source_datasets,
        "label_sources": label_sources,
        "source_splits": sorted({str(value).strip().lower() for value in df.get("source_split", pd.Series(dtype=str)).dropna().tolist() if str(value).strip()}),
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "skipped_domains": {},
        "training_strategy": "audio_bilstm",
        "joint_prediction": {
            "model_type": "audio_bilstm_multilabel",
            "label_thresholds": thresholds,
            "threshold_tuning": threshold_tuning,
        },
    }
    save_model_bundle("audio_sequence", bundle)
    return bundle


class _AudioSpectrogramDataset(Dataset):
    def __init__(self, spectrograms: list[np.ndarray], labels: np.ndarray):
        self.spectrograms = spectrograms
        self.labels = np.asarray(labels, dtype=float)

    def __len__(self) -> int:
        return len(self.spectrograms)

    def __getitem__(self, index: int) -> tuple[np.ndarray, np.ndarray]:
        return self.spectrograms[index], self.labels[index]


_AudioSpectrogramDataset.__module__ = "mental_health_screening.training"


class _AudioSpectrogramCNN(nn.Module):
    def __init__(self, num_labels: int, dropout: float = 0.25):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((4, 4)),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 4 * 4, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, num_labels),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(x))


_AudioSpectrogramCNN.__module__ = "mental_health_screening.training"


def _augment_audio_spectrogram(spectrogram: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    augmented = np.asarray(spectrogram, dtype=np.float32).copy()
    if augmented.size == 0:
        return augmented
    augmented += rng.normal(0.0, 0.02, size=augmented.shape).astype(np.float32)
    if augmented.shape[1] > 8 and rng.random() < 0.4:
        shift = int(rng.integers(-6, 7))
        augmented = np.roll(augmented, shift=shift, axis=1)
    if augmented.shape[0] > 8 and rng.random() < 0.3:
        mask_height = int(rng.integers(4, max(5, augmented.shape[0] // 8)))
        mask_start = int(rng.integers(0, max(1, augmented.shape[0] - mask_height)))
        augmented[mask_start : mask_start + mask_height, :] *= 0.92
    if augmented.shape[1] > 12 and rng.random() < 0.3:
        mask_width = int(rng.integers(4, max(5, augmented.shape[1] // 8)))
        mask_start = int(rng.integers(0, max(1, augmented.shape[1] - mask_width)))
        augmented[:, mask_start : mask_start + mask_width] *= 0.92
    return augmented.astype(np.float32)


def _train_audio_spectrogram_model(
    manifest_path: str | Path,
    dataset_root: str | Path | None = None,
    random_state: int = 42,
    max_rows: int = 1440,
    batch_size: int = 16,
    epochs: int = 8,
    learning_rate: float = 8e-4,
) -> dict:
    manifest_path = Path(manifest_path)
    base_dir = Path(dataset_root) if dataset_root else manifest_path.parent
    np.random.seed(random_state)
    torch.manual_seed(random_state)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(random_state)
    df = _load_manifest(manifest_path)
    records = [
        record
        for record in df.to_dict(orient="records")
        if _resolve_path(base_dir, record.get("audio_path")) and _comorbidity_targets(record) is not None
    ]
    print(f"[audio_spectrogram] loaded {len(df)} manifest rows", flush=True)
    print(f"[audio_spectrogram] usable audio rows {len(records)}", flush=True)
    if max_rows > 0 and len(records) > max_rows:
        rng = np.random.default_rng(random_state)
        selected_indices = np.sort(rng.choice(len(records), size=max_rows, replace=False))
        records = [records[index] for index in selected_indices]
    print(f"[audio_spectrogram] sampling {len(records)} rows", flush=True)

    spectrograms: list[np.ndarray] = []
    labels: list[list[int]] = []
    source_datasets = sorted({str(value).strip() for value in df.get("source_dataset", pd.Series(dtype=str)).dropna().tolist() if str(value).strip()})
    label_sources = sorted({str(value).strip() for value in df.get("label_source", pd.Series(dtype=str)).dropna().tolist() if str(value).strip()})

    for record in records:
        audio_path = _resolve_path(base_dir, record.get("audio_path"))
        if not audio_path:
            continue
        targets = _comorbidity_targets(record)
        if targets is None:
            continue
        extracted = extract_audio_spectrogram_features(audio_path, max_frames=128)
        if not extracted.get("available"):
            continue
        spectrograms.append(np.asarray(extracted["spectrogram"], dtype=np.float32))
        labels.append(targets)
    print(f"[audio_spectrogram] usable spectrograms {len(spectrograms)}", flush=True)

    if len(spectrograms) < 32:
        raise ValueError("At least 32 usable audio rows are required to train the spectrogram model.")

    labels_array = np.asarray(labels, dtype=int)
    rng = np.random.default_rng(random_state)
    indices = rng.permutation(len(spectrograms))
    split_index = max(1, int(len(indices) * 0.8))
    train_indices = indices[:split_index]
    eval_indices = indices[split_index:] if split_index < len(indices) else indices[: max(1, len(indices) // 5)]

    train_spectrograms = [spectrograms[index] for index in train_indices]
    train_labels = labels_array[train_indices]
    eval_spectrograms = [spectrograms[index] for index in eval_indices]
    eval_labels = labels_array[eval_indices]

    augmentation_rng = np.random.default_rng(random_state + 202)
    augmented_train_spectrograms: list[np.ndarray] = []
    augmented_train_labels: list[np.ndarray] = []
    for spectrogram, label in zip(train_spectrograms, train_labels, strict=False):
        augmented_train_spectrograms.append(np.asarray(spectrogram, dtype=np.float32))
        augmented_train_labels.append(np.asarray(label, dtype=int))
        augmented_train_spectrograms.append(_augment_audio_spectrogram(spectrogram, augmentation_rng))
        augmented_train_labels.append(np.asarray(label, dtype=int))
    train_spectrograms = augmented_train_spectrograms
    train_labels = np.asarray(augmented_train_labels, dtype=int)

    def collate_fn(batch: list[tuple[np.ndarray, np.ndarray]]) -> tuple[torch.Tensor, torch.Tensor]:
        spectrogram_tensors = [torch.tensor(item[0], dtype=torch.float32).unsqueeze(0) for item in batch]
        label_tensor = torch.tensor(np.asarray([item[1] for item in batch], dtype=float), dtype=torch.float32)
        return torch.stack(spectrogram_tensors, dim=0), label_tensor

    train_loader = DataLoader(
        _AudioSpectrogramDataset(train_spectrograms, train_labels),
        batch_size=batch_size,
        shuffle=True,
        collate_fn=collate_fn,
    )
    eval_loader = DataLoader(
        _AudioSpectrogramDataset(eval_spectrograms, eval_labels),
        batch_size=batch_size,
        shuffle=False,
        collate_fn=collate_fn,
    )

    model = _AudioSpectrogramCNN(
        num_labels=len(PREDICTION_DOMAINS),
        dropout=0.30,
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4)
    positive_counts = np.clip(train_labels.sum(axis=0), 1.0, None)
    negative_counts = np.clip(len(train_labels) - positive_counts, 1.0, None)
    pos_weight = torch.tensor(negative_counts / positive_counts, dtype=torch.float32)

    best_state = None
    best_score = -1.0
    best_eval_probs = None
    best_eval_labels = None
    patience = 3
    epochs_without_improvement = 0

    for epoch_index in range(epochs):
        model.train()
        for spectrogram_batch, batch_labels in train_loader:
            optimizer.zero_grad(set_to_none=True)
            logits = model(spectrogram_batch)
            bce_loss = nn.functional.binary_cross_entropy_with_logits(logits, batch_labels, reduction="none", pos_weight=pos_weight)
            probabilities = torch.sigmoid(logits)
            pt = probabilities * batch_labels + (1.0 - probabilities) * (1.0 - batch_labels)
            focal_weight = torch.pow(1.0 - pt, 1.5)
            loss = (bce_loss * focal_weight).mean()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

        model.eval()
        eval_probs: list[np.ndarray] = []
        eval_true: list[np.ndarray] = []
        with torch.no_grad():
            for spectrogram_batch, batch_labels in eval_loader:
                logits = model(spectrogram_batch)
                probs = torch.sigmoid(logits).cpu().numpy()
                eval_probs.append(probs)
                eval_true.append(batch_labels.cpu().numpy())
        if not eval_probs:
            continue
        probabilities_y = np.vstack(eval_probs)
        labels_y = np.vstack(eval_true)
        epoch_thresholds, _ = _tune_comorbidity_thresholds(labels_y, probabilities_y)
        metrics, _ = _evaluate_multilabel_predictions(labels_y, probabilities_y, thresholds=epoch_thresholds)
        print(f"[audio_spectrogram] epoch {epoch_index + 1}/{epochs} metrics {metrics}", flush=True)
        score = metrics["macro_f1"] + 0.25 * metrics["label_accuracy"] + 0.1 * metrics["exact_match"]
        if score > best_score:
            best_score = score
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
            best_eval_probs = probabilities_y
            best_eval_labels = labels_y
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= patience:
                break

    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()

    if best_eval_probs is None or best_eval_labels is None:
        raise ValueError("Audio spectrogram training did not produce validation predictions.")

    thresholds, threshold_tuning = _tune_comorbidity_thresholds(best_eval_labels, best_eval_probs)
    metrics, _ = _evaluate_multilabel_predictions(best_eval_labels, best_eval_probs, thresholds=thresholds)

    bundle = {
        "model_type": "audio_spectrogram_cnn_multilabel",
        "modality": "audio_spectrogram",
        "domains": list(PREDICTION_DOMAINS),
        "feature_names": [f"mel_{index + 1}" for index in range(int(train_spectrograms[0].shape[0]))],
        "model": model.cpu(),
        "spectrogram_config": {
            "n_mels": int(train_spectrograms[0].shape[0]),
            "max_frames": int(train_spectrograms[0].shape[1]),
            "batch_size": int(batch_size),
            "epochs": int(epochs),
            "learning_rate": float(learning_rate),
            "max_rows": int(max_rows),
        },
        "label_thresholds": thresholds,
        "metrics": {
            **metrics,
            "sample_count": int(len(spectrograms)),
        },
        "sample_count": int(len(spectrograms)),
        "sample_counts": {domain: int(np.sum(labels_array[:, index])) for index, domain in enumerate(PREDICTION_DOMAINS)},
        "train_counts": {},
        "test_counts": {},
        "manifest_path": str(manifest_path.resolve()),
        "dataset_root": str(base_dir.resolve()),
        "source_datasets": source_datasets,
        "label_sources": label_sources,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "skipped_domains": {},
        "training_strategy": "audio_spectrogram_cnn",
        "joint_prediction": {
            "model_type": "audio_spectrogram_cnn_multilabel",
            "label_thresholds": thresholds,
            "threshold_tuning": threshold_tuning,
        },
    }
    save_model_bundle("audio_spectrogram", bundle)
    return bundle


class _ImageTensorDataset(Dataset):
    def __init__(self, images: list[np.ndarray], labels: np.ndarray):
        self.images = images
        self.labels = np.asarray(labels, dtype=float)

    def __len__(self) -> int:
        return len(self.images)

    def __getitem__(self, index: int) -> tuple[np.ndarray, np.ndarray]:
        return self.images[index], self.labels[index]


_ImageTensorDataset.__module__ = "mental_health_screening.training"


class _ImageCNN(nn.Module):
    def __init__(self, num_labels: int, dropout: float = 0.30):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((4, 4)),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256 * 4 * 4, 256),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(256, num_labels),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(x))


_ImageCNN.__module__ = "mental_health_screening.training"


def _load_image_tensor(image_path: str, image_size: int = 128) -> np.ndarray | None:
    if cv2 is None or not image_path or not os.path.exists(image_path):
        return None
    image = cv2.imread(image_path)
    if image is None:
        return None
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (image_size, image_size), interpolation=cv2.INTER_AREA)
    return (image.astype(np.float32) / 255.0).transpose(2, 0, 1)


def _augment_image_tensor(image: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    augmented = np.asarray(image, dtype=np.float32).copy()
    if augmented.size == 0:
        return augmented
    channels, height, width = augmented.shape
    if rng.random() < 0.5:
        augmented = np.flip(augmented, axis=2)
    if rng.random() < 0.65:
        angle = float(rng.uniform(-18.0, 18.0))
        matrix = cv2.getRotationMatrix2D((width / 2.0, height / 2.0), angle, float(rng.uniform(0.88, 1.12)))
        augmented = cv2.warpAffine(
            np.transpose(augmented, (1, 2, 0)),
            matrix,
            (width, height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT_101,
        ).transpose(2, 0, 1)
    if rng.random() < 0.45:
        shift_x = int(rng.integers(-10, 11))
        shift_y = int(rng.integers(-10, 11))
        matrix = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
        augmented = cv2.warpAffine(
            np.transpose(augmented, (1, 2, 0)),
            matrix,
            (width, height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT_101,
        ).transpose(2, 0, 1)
    if rng.random() < 0.3 and hasattr(cv2, "getPerspectiveTransform"):
        src = np.float32(
            [
                [0, 0],
                [width - 1, 0],
                [0, height - 1],
                [width - 1, height - 1],
            ]
        )
        jitter = float(min(height, width) * 0.04)
        dst = np.float32(
            [
                [rng.uniform(0, jitter), rng.uniform(0, jitter)],
                [width - 1 - rng.uniform(0, jitter), rng.uniform(0, jitter)],
                [rng.uniform(0, jitter), height - 1 - rng.uniform(0, jitter)],
                [width - 1 - rng.uniform(0, jitter), height - 1 - rng.uniform(0, jitter)],
            ]
        )
        perspective = cv2.getPerspectiveTransform(src, dst)
        augmented = cv2.warpPerspective(
            np.transpose(augmented, (1, 2, 0)),
            perspective,
            (width, height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT_101,
        ).transpose(2, 0, 1)
    brightness = float(rng.uniform(0.76, 1.24))
    contrast = float(rng.uniform(0.78, 1.22))
    saturation = float(rng.uniform(0.82, 1.18))
    gamma = float(rng.uniform(0.88, 1.14))
    augmented = np.clip(((augmented - 0.5) * contrast + 0.5) * brightness, 0.0, 1.0)
    augmented = np.clip(np.power(np.clip(augmented, 1e-6, 1.0), gamma), 0.0, 1.0)
    if channels == 3 and rng.random() < 0.35:
        channel_scale = rng.uniform(0.90, 1.10, size=(3, 1, 1)).astype(np.float32)
        augmented = np.clip(augmented * channel_scale, 0.0, 1.0)
        augmented = np.clip((augmented * saturation) + (augmented.mean(axis=0, keepdims=True) * (1.0 - saturation)), 0.0, 1.0)
    if channels == 3 and rng.random() < 0.18:
        channel_dropout = int(rng.integers(0, 3))
        augmented[channel_dropout, :, :] *= float(rng.uniform(0.85, 0.98))
    if rng.random() < 0.3:
        blur = int(rng.choice([3, 5]))
        blurred = cv2.GaussianBlur(np.transpose(augmented, (1, 2, 0)), (blur, blur), 0)
        augmented = blurred.transpose(2, 0, 1)
    if rng.random() < 0.45:
        cut_h = int(rng.integers(max(8, height // 10), max(12, height // 3)))
        cut_w = int(rng.integers(max(8, width // 10), max(12, width // 3)))
        start_y = int(rng.integers(0, max(1, height - cut_h)))
        start_x = int(rng.integers(0, max(1, width - cut_w)))
        augmented[:, start_y : start_y + cut_h, start_x : start_x + cut_w] = augmented.mean(axis=(1, 2), keepdims=True)
    if rng.random() < 0.3:
        gray = np.mean(augmented, axis=0, keepdims=True)
        augmented = np.repeat(gray, 3, axis=0)
    if rng.random() < 0.35:
        augmented = np.clip(augmented + rng.normal(0.0, 0.03, size=augmented.shape).astype(np.float32), 0.0, 1.0)
    if rng.random() < 0.25:
        augmented = np.clip(augmented * rng.uniform(0.92, 1.08), 0.0, 1.0)
    augmented += rng.normal(0.0, 0.018, size=augmented.shape).astype(np.float32)
    return np.clip(augmented, 0.0, 1.0).astype(np.float32)


def _train_image_cnn_model(
    manifest_path: str | Path,
    dataset_root: str | Path | None = None,
    random_state: int = 42,
    max_rows: int = 1600,
    batch_size: int = 24,
    epochs: int = 8,
    learning_rate: float = 8e-4,
    image_size: int = 128,
) -> dict:
    manifest_path = Path(manifest_path)
    base_dir = Path(dataset_root) if dataset_root else manifest_path.parent
    np.random.seed(random_state)
    torch.manual_seed(random_state)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(random_state)
    if cv2 is None:
        raise ValueError("OpenCV is required for image CNN training but is not installed.")
    df = _load_manifest(manifest_path)
    records = [
        record
        for record in df.to_dict(orient="records")
        if _resolve_path(base_dir, record.get("image_path")) and _comorbidity_targets(record) is not None
    ]
    print(f"[image_dl] loaded {len(df)} manifest rows", flush=True)
    print(f"[image_dl] usable image rows {len(records)}", flush=True)
    if max_rows > 0 and len(records) > max_rows:
        rng = np.random.default_rng(random_state)
        selected_indices = np.sort(rng.choice(len(records), size=max_rows, replace=False))
        records = [records[index] for index in selected_indices]
    print(f"[image_dl] sampling {len(records)} rows", flush=True)

    images: list[np.ndarray] = []
    labels: list[list[int]] = []
    source_datasets = sorted({str(value).strip() for value in df.get("source_dataset", pd.Series(dtype=str)).dropna().tolist() if str(value).strip()})
    label_sources = sorted({str(value).strip() for value in df.get("label_source", pd.Series(dtype=str)).dropna().tolist() if str(value).strip()})

    for record in records:
        image_path = _resolve_path(base_dir, record.get("image_path"))
        if not image_path:
            continue
        targets = _comorbidity_targets(record)
        if targets is None:
            continue
        image_tensor = _load_image_tensor(image_path, image_size=image_size)
        if image_tensor is None:
            continue
        images.append(image_tensor)
        labels.append(targets)
    print(f"[image_dl] usable tensors {len(images)}", flush=True)

    if len(images) < 32:
        raise ValueError("At least 32 usable image rows are required to train the image CNN model.")

    labels_array = np.asarray(labels, dtype=int)
    rng = np.random.default_rng(random_state)
    indices = rng.permutation(len(images))
    split_index = max(1, int(len(indices) * 0.8))
    train_indices = indices[:split_index]
    eval_indices = indices[split_index:] if split_index < len(indices) else indices[: max(1, len(indices) // 5)]

    train_images = [images[index] for index in train_indices]
    train_labels = labels_array[train_indices]
    eval_images = [images[index] for index in eval_indices]
    eval_labels = labels_array[eval_indices]

    augmentation_rng = np.random.default_rng(random_state + 404)
    augmented_train_images: list[np.ndarray] = []
    augmented_train_labels: list[np.ndarray] = []
    for image, label in zip(train_images, train_labels, strict=False):
        augmented_train_images.append(np.asarray(image, dtype=np.float32))
        augmented_train_labels.append(np.asarray(label, dtype=int))
        for _ in range(4):
            augmented_train_images.append(_augment_image_tensor(image, augmentation_rng))
            augmented_train_labels.append(np.asarray(label, dtype=int))
    train_images = augmented_train_images
    train_labels = np.asarray(augmented_train_labels, dtype=int)

    positive_counts = np.clip(train_labels.sum(axis=0), 1.0, None)
    class_prevalence = positive_counts / float(len(train_labels))
    sample_weights = []
    for row in train_labels:
        positive_domains = np.where(row > 0)[0]
        if len(positive_domains):
            weights = [1.0 / float(class_prevalence[index]) for index in positive_domains]
            sample_weights.append(float(np.mean(weights)))
        else:
            sample_weights.append(float(1.0 / max(1e-3, 1.0 - float(class_prevalence.mean()))))
    sampler = WeightedRandomSampler(
        weights=torch.tensor(sample_weights, dtype=torch.double),
        num_samples=len(sample_weights),
        replacement=True,
    )

    def collate_fn(batch: list[tuple[np.ndarray, np.ndarray]]) -> tuple[torch.Tensor, torch.Tensor]:
        image_tensors = [torch.tensor(item[0], dtype=torch.float32) for item in batch]
        label_tensor = torch.tensor(np.asarray([item[1] for item in batch], dtype=float), dtype=torch.float32)
        return torch.stack(image_tensors, dim=0), label_tensor

    train_loader = DataLoader(
        _ImageTensorDataset(train_images, train_labels),
        batch_size=batch_size,
        sampler=sampler,
        collate_fn=collate_fn,
    )
    eval_loader = DataLoader(
        _ImageTensorDataset(eval_images, eval_labels),
        batch_size=batch_size,
        shuffle=False,
        collate_fn=collate_fn,
    )

    model = _ImageCNN(
        num_labels=len(PREDICTION_DOMAINS),
        dropout=0.35,
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate * 0.75, weight_decay=2e-4)
    positive_counts = np.clip(train_labels.sum(axis=0), 1.0, None)
    negative_counts = np.clip(len(train_labels) - positive_counts, 1.0, None)
    pos_weight = torch.tensor(negative_counts / positive_counts, dtype=torch.float32)

    best_state = None
    best_score = -1.0
    best_eval_probs = None
    best_eval_labels = None
    patience = 3
    epochs_without_improvement = 0

    for epoch_index in range(epochs):
        model.train()
        for image_batch, batch_labels in train_loader:
            optimizer.zero_grad(set_to_none=True)
            logits = model(image_batch)
            bce_loss = nn.functional.binary_cross_entropy_with_logits(logits, batch_labels, reduction="none", pos_weight=pos_weight)
            probabilities = torch.sigmoid(logits)
            pt = probabilities * batch_labels + (1.0 - probabilities) * (1.0 - batch_labels)
            focal_weight = torch.pow(1.0 - pt, 1.5)
            loss = (bce_loss * focal_weight).mean()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

        model.eval()
        eval_probs: list[np.ndarray] = []
        eval_true: list[np.ndarray] = []
        with torch.no_grad():
            for image_batch, batch_labels in eval_loader:
                logits = model(image_batch)
                probs = torch.sigmoid(logits).cpu().numpy()
                eval_probs.append(probs)
                eval_true.append(batch_labels.cpu().numpy())
        if not eval_probs:
            continue
        probabilities_y = np.vstack(eval_probs)
        labels_y = np.vstack(eval_true)
        epoch_thresholds, _ = _tune_comorbidity_thresholds(labels_y, probabilities_y)
        metrics, _ = _evaluate_multilabel_predictions(labels_y, probabilities_y, thresholds=epoch_thresholds)
        print(f"[image_dl] epoch {epoch_index + 1}/{epochs} metrics {metrics}", flush=True)
        score = metrics["macro_f1"] + 0.25 * metrics["label_accuracy"] + 0.1 * metrics["exact_match"]
        if score > best_score:
            best_score = score
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
            best_eval_probs = probabilities_y
            best_eval_labels = labels_y
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= patience:
                break

    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()

    if best_eval_probs is None or best_eval_labels is None:
        raise ValueError("Image CNN training did not produce validation predictions.")

    thresholds, threshold_tuning = _tune_comorbidity_thresholds(best_eval_labels, best_eval_probs)
    metrics, _ = _evaluate_multilabel_predictions(best_eval_labels, best_eval_probs, thresholds=thresholds)

    bundle = {
        "model_type": "image_cnn_multilabel",
        "modality": "image_dl",
        "domains": list(PREDICTION_DOMAINS),
        "feature_names": [
            "rgb_image_tensor",
            f"{image_size}x{image_size}",
        ],
        "model": model.cpu(),
        "image_config": {
            "image_size": int(image_size),
            "channels": 3,
            "batch_size": int(batch_size),
            "epochs": int(epochs),
            "learning_rate": float(learning_rate),
            "max_rows": int(max_rows),
        },
        "label_thresholds": thresholds,
        "metrics": {
            **metrics,
            "sample_count": int(len(images)),
        },
        "sample_count": int(len(images)),
        "sample_counts": {domain: int(np.sum(labels_array[:, index])) for index, domain in enumerate(PREDICTION_DOMAINS)},
        "train_counts": {},
        "test_counts": {},
        "manifest_path": str(manifest_path.resolve()),
        "dataset_root": str(base_dir.resolve()),
        "source_datasets": source_datasets,
        "label_sources": label_sources,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "skipped_domains": {},
        "training_strategy": "image_cnn",
        "joint_prediction": {
            "model_type": "image_cnn_multilabel",
            "label_thresholds": thresholds,
            "threshold_tuning": threshold_tuning,
        },
    }
    save_model_bundle("image_dl", bundle)
    return bundle


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
        features = extract_audio_features(audio_path, include_pitch_features=True)
        feature_names, vector = audio_feature_vector(features)
        return features, feature_names, vector

    if modality == "image":
        image_path = _resolve_path(base_dir, record.get("image_path"))
        if not image_path:
            return None
        features = extract_image_features(image_path)
        feature_names, vector = image_feature_vector(features)
        return features, feature_names, vector

    if modality == "passive_biomarkers":
        passive_payload = dict((record.get("multimodal") or {}).get("passive") or {})
        features = dict(passive_payload.get("features") or {})
        if not features:
            return None
        rppg = dict(features.get("rppg") or {})
        typing = dict(features.get("typing") or {})
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
        audio_features = extract_audio_features(audio_path, include_pitch_features=True)
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


def _passive_questionnaire_targets(record: dict, threshold: float = 0.5) -> list[int] | None:
    questionnaire = dict(record.get("questionnaire") or {})
    overall_scores = dict(((record.get("multimodal") or {}).get("overall") or {}).get("scores") or {})
    targets = []
    for domain in PREDICTION_DOMAINS:
        raw_value = _parse_target_value(
            questionnaire.get(f"{domain}_score")
            if questionnaire.get(f"{domain}_score") is not None
            else questionnaire.get(domain)
        )
        if raw_value is None:
            raw_value = _parse_target_value(overall_scores.get(domain))
        if raw_value is None:
            return None
        targets.append(int(float(raw_value) >= threshold))
    return targets


def _passive_training_row(record: dict) -> dict | None:
    passive_payload = dict(((record.get("multimodal") or {}).get("passive") or {}).get("features") or {})
    if not passive_payload:
        return None
    targets = _passive_questionnaire_targets(record)
    if targets is None:
        return None

    questionnaire = dict(record.get("questionnaire") or {})
    overall_scores = dict(((record.get("multimodal") or {}).get("overall") or {}).get("scores") or {})
    rppg = dict(passive_payload.get("rppg") or {})
    typing = dict(passive_payload.get("typing") or {})
    row = {
        "assessment_id": record.get("assessment_id"),
        "created_at": record.get("created_at"),
        "patient_key": record.get("patient_key"),
        "source_dataset": "screening_results",
        "record_origin": record.get("record_origin", "backend"),
        "passive_features": {
            "confidence": float(passive_payload.get("confidence", 0.0) or 0.0),
            "heart_rate_bpm": float(passive_payload.get("heart_rate_bpm", 0.0) or 0.0),
            "heart_rate_score": float(rppg.get("heart_rate_score", passive_payload.get("heart_rate_score", 0.0)) or 0.0),
            "signal_quality": float(rppg.get("signal_quality", passive_payload.get("signal_quality", 0.0)) or 0.0),
            "typing_speed_cpm": float(passive_payload.get("typing_speed_cpm", 0.0) or 0.0),
            "typing_pause_ratio": float(passive_payload.get("typing_pause_ratio", 0.0) or 0.0),
            "typing_backspace_ratio": float(passive_payload.get("typing_backspace_ratio", 0.0) or 0.0),
            "typing_rhythm_score": float(typing.get("rhythm_score", passive_payload.get("typing_rhythm_score", 0.0)) or 0.0),
            "rppg_available": bool(rppg.get("available")),
            "typing_available": bool(typing.get("available")),
        },
        "questionnaire_scores": {
            domain: float(
                _parse_target_value(questionnaire.get(f"{domain}_score"))
                if questionnaire.get(f"{domain}_score") is not None
                else _parse_target_value(questionnaire.get(domain))
                if questionnaire.get(domain) is not None
                else _parse_target_value(overall_scores.get(domain))
                or 0.0
            )
            for domain in PREDICTION_DOMAINS
        },
        "labels": {domain: int(targets[index]) for index, domain in enumerate(PREDICTION_DOMAINS)},
    }
    return row


def collect_passive_training_example(record: dict) -> dict | None:
    row = _passive_training_row(record)
    if row is None:
        return None

    PASSIVE_TRAINING_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    existing_ids = set()
    if PASSIVE_TRAINING_MANIFEST.exists():
        try:
            for line in PASSIVE_TRAINING_MANIFEST.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                payload = json.loads(line)
                assessment_id = str(payload.get("assessment_id", "")).strip().upper()
                if assessment_id:
                    existing_ids.add(assessment_id)
        except Exception:
            existing_ids = set()

    assessment_id = str(row.get("assessment_id", "")).strip().upper()
    if assessment_id and assessment_id in existing_ids:
        return row

    with PASSIVE_TRAINING_MANIFEST.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=True) + "\n")
    return row


def sync_passive_training_manifest(records: list[dict] | None = None) -> int:
    source_records = list(records) if records is not None else _load_saved_assessment_records()
    collected = 0
    for record in source_records:
        if collect_passive_training_example(record) is not None:
            collected += 1
    return collected


def _load_passive_training_rows() -> list[dict]:
    if not PASSIVE_TRAINING_MANIFEST.exists():
        return []
    rows: list[dict] = []
    try:
        for line in PASSIVE_TRAINING_MANIFEST.read_text(encoding="utf-8").splitlines():
            text = line.strip()
            if not text:
                continue
            row = json.loads(text)
            if isinstance(row, dict):
                rows.append(row)
    except Exception:
        return []
    return rows


def train_passive_biomarkers_model(
    random_state: int = 42,
    min_samples: int = 25,
) -> dict:
    passive_rows = _load_passive_training_rows()
    if not passive_rows:
        sync_passive_training_manifest()
        passive_rows = _load_passive_training_rows()

    feature_rows: list[list[float]] = []
    label_rows: list[list[int]] = []
    feature_names: list[str] | None = None

    for row in passive_rows:
        passive_features = dict(row.get("passive_features") or {})
        labels = dict(row.get("labels") or {})
        if not passive_features or len(labels) != len(PREDICTION_DOMAINS):
            continue
        feature_names = feature_names or [
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
        feature_rows.append([
            float(passive_features.get("confidence", 0.0) or 0.0),
            float(passive_features.get("heart_rate_bpm", 0.0) or 0.0),
            float(passive_features.get("heart_rate_score", 0.0) or 0.0),
            float(passive_features.get("signal_quality", 0.0) or 0.0),
            float(passive_features.get("typing_speed_cpm", 0.0) or 0.0),
            float(passive_features.get("typing_pause_ratio", 0.0) or 0.0),
            float(passive_features.get("typing_backspace_ratio", 0.0) or 0.0),
            float(passive_features.get("typing_rhythm_score", 0.0) or 0.0),
            1.0 if passive_features.get("rppg_available") else 0.0,
            1.0 if passive_features.get("typing_available") else 0.0,
        ])
        label_rows.append([int(labels.get(domain, 0)) for domain in PREDICTION_DOMAINS])

    if len(feature_rows) < min_samples:
        raise ValueError(
            f"At least {min_samples} passive-labeled rows are required to train the passive biomarker bundle."
        )

    features_x = np.asarray(feature_rows, dtype=float)
    labels_y = np.asarray(label_rows, dtype=int)

    metrics: dict[str, dict] = {}
    confidence_calibrators: dict[str, dict] = {}
    model_families: dict[str, str] = {}
    model_selection: dict[str, dict] = {}
    label_thresholds: dict[str, float] = {}
    sample_counts: dict[str, int] = {}
    train_counts: dict[str, int] = {}
    test_counts: dict[str, int] = {}
    models: dict[str, RandomForestClassifier | DummyClassifier | Pipeline] = {}
    skipped_domains: dict[str, str] = {}

    for index, domain in enumerate(PREDICTION_DOMAINS):
        try:
            model, domain_metrics, train_count, test_count, calibrator = _fit_domain_model(
                features_x=features_x,
                targets_y=labels_y[:, index].astype(float),
                random_state=random_state,
                test_size=0.3,
                domain=domain,
                modality="passive_biomarkers",
                allow_deep_candidate=False,
            )
        except Exception as error:
            skipped_domains[domain] = str(error)
            continue
        models[domain] = model
        metrics[domain] = domain_metrics
        confidence_calibrators[domain] = calibrator
        model_families[domain] = str(domain_metrics.get("selected_model_family", type(model).__name__)).strip()
        model_selection[domain] = dict(domain_metrics.get("candidate_metrics", {}))
        label_thresholds[domain] = float(domain_metrics.get("decision_threshold", 0.5))
        sample_counts[domain] = int(len(features_x))
        train_counts[domain] = train_count
        test_counts[domain] = test_count

    if not models:
        raise ValueError("No passive biomarker domains were trainable from the available records.")

    trained_domains = list(models.keys())
    macro_accuracy = float(np.mean([metrics[domain]["accuracy"] for domain in trained_domains]))
    macro_precision = float(np.mean([metrics[domain]["precision"] for domain in trained_domains]))
    macro_recall = float(np.mean([metrics[domain]["recall"] for domain in trained_domains]))
    macro_f1 = float(np.mean([metrics[domain]["f1"] for domain in trained_domains]))
    macro_r2 = float(np.mean([metrics[domain]["r2"] for domain in trained_domains]))
    calibration_quality = float(np.mean([confidence_calibrators[domain]["metrics"]["calibrated_accuracy"] for domain in trained_domains]))
    confidence_hint = float(np.clip(0.3 * macro_f1 + 0.2 * macro_precision + 0.5 * calibration_quality, 0.05, 0.99))

    bundle = {
        "modality": "passive_biomarkers",
        "domains": trained_domains,
        "feature_names": feature_names or [],
        "models": models,
        "confidence_calibrators": confidence_calibrators,
        "label_thresholds": label_thresholds,
        "model_families": model_families,
        "model_selection": model_selection,
        "metrics": {
            **metrics,
            "macro_accuracy": macro_accuracy,
            "macro_precision": macro_precision,
            "macro_recall": macro_recall,
            "macro_f1": macro_f1,
            "macro_r2": macro_r2,
            "calibration_quality": calibration_quality,
        },
        "confidence_hint": confidence_hint,
        "sample_count": int(sum(sample_counts.values())),
        "sample_counts": sample_counts,
        "train_counts": train_counts,
        "test_counts": test_counts,
        "manifest_path": None,
        "dataset_root": None,
        "source_datasets": ["screening_results"],
        "label_sources": ["questionnaire"],
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "skipped_domains": skipped_domains,
        "training_strategy": "passive_bootstrap_from_saved_assessments",
    }
    save_model_bundle("passive_biomarkers", bundle)
    return bundle


def maybe_autotrain_passive_biomarkers(
    min_new_rows: int = PASSIVE_AUTOTRAIN_MIN_NEW_ROWS,
    min_total_rows: int = PASSIVE_AUTOTRAIN_MIN_TOTAL_ROWS,
) -> dict | None:
    passive_rows = _load_passive_training_rows()
    if len(passive_rows) < min_total_rows:
        return None

    current_bundle = load_model_bundle("passive_biomarkers") or {}
    current_sample_count = int(current_bundle.get("sample_count", 0) or 0)
    new_rows = len(passive_rows) - current_sample_count
    if new_rows < min_new_rows:
        return None

    return train_passive_biomarkers_model()


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
                    "model_family": "dummy",
                    "train_accuracy": float(model.score(augmented, target)) if len(target) else 0.0,
                    "train_f1": float(f1_score(target, model.predict(augmented), zero_division=0)) if len(target) else 0.0,
                }
            )
            continue

        binary_targets = target
        stratify = binary_targets if len(np.unique(binary_targets)) > 1 and int(np.bincount(binary_targets, minlength=2).min()) >= 2 else None
        if len(augmented) < 6:
            x_train, x_eval, y_train, y_eval = augmented, augmented, binary_targets, binary_targets
        else:
            try:
                x_train, x_eval, y_train, y_eval = train_test_split(
                    augmented,
                    binary_targets,
                    test_size=0.25 if len(augmented) > 8 else 0.5,
                    random_state=random_state + position + domain_index,
                    stratify=stratify,
                )
            except ValueError:
                x_train, x_eval, y_train, y_eval = train_test_split(
                    augmented,
                    binary_targets,
                    test_size=0.25 if len(augmented) > 8 else 0.5,
                    random_state=random_state + position + domain_index,
                    stratify=None,
                )
        model, metrics, model_family, candidate_metrics = _fit_comorbidity_chain_binary_model(
            x_train=x_train,
            y_train=y_train,
            x_eval=x_eval,
            y_eval=y_eval,
            random_state=random_state + position + domain_index,
        )
        final_model = clone(model)
        combined_x = np.concatenate([x_train, x_eval], axis=0)
        combined_y = np.concatenate([y_train, y_eval], axis=0)
        final_model.fit(combined_x, combined_y)
        predictions = (np.asarray(final_model.predict_proba(augmented), dtype=float)[:, -1] >= 0.5).astype(int) if hasattr(final_model, "predict_proba") else final_model.predict(augmented)
        chain_models.append(
            {
                "domain": domain,
                "domain_index": int(domain_index),
                "model": final_model,
                "constant_probability": None,
                "model_family": model_family,
                "candidate_metrics": candidate_metrics,
                "train_accuracy": float(metrics.get("accuracy", accuracy_score(target, predictions))),
                "train_f1": float(metrics.get("f1", f1_score(target, predictions, zero_division=0))),
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


def _tune_comorbidity_thresholds(
    labels_y: np.ndarray,
    probabilities_y: np.ndarray,
    beta: float = COMORBIDITY_THRESHOLD_BETA,
    min_precision: float | None = None,
) -> tuple[dict[str, float], dict[str, dict]]:
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
                "beta": float(beta),
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
            beta_sq = float(beta) ** 2
            numerator = (1.0 + beta_sq) * precision * recall
            denominator = (beta_sq * precision) + recall
            fbeta = np.divide(
                numerator,
                denominator,
                out=np.zeros_like(numerator, dtype=float),
                where=denominator > 1e-9,
            )
            candidate_indices = np.arange(len(fbeta))
            if min_precision is not None:
                precision_floor = float(min_precision)
                eligible = candidate_indices[precision >= precision_floor]
                if len(eligible):
                    candidate_indices = eligible
            candidate_scores = fbeta[candidate_indices]
            if len(candidate_scores) == 0:
                candidate_indices = np.arange(len(fbeta))
                candidate_scores = fbeta
            best_index = int(candidate_indices[int(np.argmax(candidate_scores))])
            tuned_threshold = float(threshold_values[min(best_index, len(threshold_values) - 1)])
            best_fbeta = float(fbeta[best_index]) if len(fbeta) else 0.0

        thresholds[domain] = round(float(np.clip(tuned_threshold, 0.05, 0.95)), 3)
        tuning_meta[domain] = {
            "method": "precision_recall_fbeta",
            "beta": float(beta),
            "min_precision": None if min_precision is None else float(min_precision),
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
    domain: str,
    modality: str,
    allow_deep_candidate: bool = True,
) -> tuple[RandomForestClassifier | DummyClassifier | Pipeline, dict, int, int, dict]:
    tuning = AUDIO_DOMAIN_TUNING.get(str(domain), {}) if modality == "audio" else {}
    threshold_beta = float(tuning.get("beta", AUDIO_THRESHOLD_BETA)) if modality == "audio" else 1.0
    min_precision = tuning.get("min_precision") if modality == "audio" else None
    x_train, x_val, x_test, y_train, y_val, y_test = _split_train_validation_holdout(
        features_x,
        targets_y,
        random_state=random_state,
        holdout_fraction=test_size,
    )

    model, validation_metrics, model_family, candidate_metrics, prediction_std, tuned_threshold = _fit_selected_binary_model(
        x_train=x_train,
        y_train=y_train,
        x_test=x_val,
        y_test=y_val,
        random_state=random_state,
        allow_deep_candidate=allow_deep_candidate,
        threshold_beta=threshold_beta,
        min_precision=min_precision if min_precision is None else float(min_precision),
    )
    combined_x = np.concatenate([x_train, x_val], axis=0)
    combined_y = np.concatenate([y_train, y_val], axis=0)
    final_model = clone(model)
    final_model.fit(combined_x, combined_y)
    probabilities, prediction_std = _forest_prediction_stats(final_model, x_test)
    test_threshold, tuned_test_metrics = _tune_binary_threshold(
        y_test,
        probabilities,
        beta=threshold_beta,
        min_precision=min_precision if min_precision is None else float(min_precision),
    )
    metrics = dict(tuned_test_metrics)
    metrics = dict(metrics)
    calibrator = _fit_confidence_calibrator(
        predictions=np.asarray(probabilities, dtype=float),
        prediction_std=prediction_std,
        targets_y=y_test,
        tolerance=CALIBRATION_TOLERANCE,
        random_state=random_state,
    )
    metrics["confidence_brier"] = float(calibrator["metrics"]["calibrated_brier"])
    metrics["confidence_accuracy"] = float(calibrator["metrics"]["calibrated_accuracy"])
    metrics["selected_model_family"] = model_family
    metrics["decision_threshold"] = float(test_threshold)
    metrics["candidate_metrics"] = candidate_metrics
    metrics["validation_metrics"] = validation_metrics
    metrics["validation_threshold"] = float(tuned_threshold)
    return final_model, metrics, int(len(combined_x)), int(len(x_test)), calibrator


def _forest_prediction_stats(model, features_x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if getattr(model, "predict_proba", None) is not None:
        predicted_probabilities = np.asarray(model.predict_proba(features_x), dtype=float)[:, -1]
        if hasattr(model, "estimators_"):
            estimator_rows = []
            for estimator in np.ravel(model.estimators_):
                if hasattr(estimator, "predict_proba"):
                    estimator_rows.append(np.asarray(estimator.predict_proba(features_x), dtype=float)[:, -1])
                else:
                    estimator_rows.append(np.asarray(estimator.predict(features_x), dtype=float))
            tree_predictions = np.asarray(estimator_rows, dtype=float)
        else:
            approximate_std = np.sqrt(np.clip(predicted_probabilities * (1.0 - predicted_probabilities), 0.0, 0.25))
            return predicted_probabilities, approximate_std
    elif hasattr(model, "estimators_"):
        estimator_rows = []
        for estimator in np.ravel(model.estimators_):
            if hasattr(estimator, "predict_proba"):
                estimator_rows.append(np.asarray(estimator.predict_proba(features_x), dtype=float)[:, -1])
            else:
                estimator_rows.append(np.asarray(estimator.predict(features_x), dtype=float))
        tree_predictions = np.asarray(estimator_rows, dtype=float)
    else:
        tree_predictions = np.asarray([np.asarray(model.predict(features_x), dtype=float)], dtype=float)
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

    models: dict[str, RandomForestClassifier | DummyClassifier | Pipeline] = {}
    metrics: dict[str, dict] = {}
    confidence_calibrators: dict[str, dict] = {}
    model_families: dict[str, str] = {}
    model_selection: dict[str, dict] = {}
    label_thresholds: dict[str, float] = {}
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
            domain=domain,
            modality=modality,
            allow_deep_candidate=(modality == "image"),
        )
        models[domain] = model
        metrics[domain] = domain_metrics
        confidence_calibrators[domain] = calibrator
        model_families[domain] = str(domain_metrics.get("selected_model_family", type(model).__name__)).strip()
        model_selection[domain] = dict(domain_metrics.get("candidate_metrics", {}))
        label_thresholds[domain] = float(domain_metrics.get("decision_threshold", 0.5))
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
    macro_accuracy = float(np.mean([metrics[domain]["accuracy"] for domain in trained_domains]))
    macro_precision = float(np.mean([metrics[domain]["precision"] for domain in trained_domains]))
    macro_recall = float(np.mean([metrics[domain]["recall"] for domain in trained_domains]))
    macro_f1 = float(np.mean([metrics[domain]["f1"] for domain in trained_domains]))
    macro_r2 = float(np.mean([metrics[domain]["r2"] for domain in trained_domains]))
    calibration_quality = float(
        np.mean([
            confidence_calibrators[domain]["metrics"]["calibrated_accuracy"]
            for domain in trained_domains
        ])
    )
    confidence_hint = float(np.clip(0.4 * macro_f1 + 0.2 * macro_precision + 0.4 * calibration_quality, 0.05, 0.99))

    bundle = {
        "modality": modality,
        "domains": trained_domains,
        "feature_names": feature_names,
        "models": models,
        "confidence_calibrators": confidence_calibrators,
        "label_thresholds": label_thresholds,
        "model_families": model_families,
        "model_selection": model_selection,
        "metrics": {
            **metrics,
            "macro_accuracy": macro_accuracy,
            "macro_precision": macro_precision,
            "macro_recall": macro_recall,
            "macro_f1": macro_f1,
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
        results["audio_spectrogram"] = {
            "status": "trained",
            "bundle": _train_audio_spectrogram_model(
                manifest_path=manifest_path,
                dataset_root=dataset_root,
            ),
        }
    except Exception as error:
        results["audio_spectrogram"] = {"status": "skipped", "error": str(error)}
    try:
        results["image_dl"] = {
            "status": "trained",
            "bundle": _train_image_cnn_model(
                manifest_path=manifest_path,
                dataset_root=dataset_root,
            ),
        }
    except Exception as error:
        results["image_dl"] = {"status": "skipped", "error": str(error)}
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
    chain_model_families = {
        f"chain_{index + 1:02d}": [
            model_spec.get("model_family", "unknown")
            for model_spec in chain_spec.get("models", [])
        ]
        for index, chain_spec in enumerate(chain_ensemble)
    }

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
        "chain_model_families": chain_model_families,
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


def train_text_transformer_model(
    manifest_path: str | Path,
    dataset_root: str | Path | None = None,
    random_state: int = 42,
    max_rows: int = 8000,
    batch_size: int = 8,
    epochs: int = 2,
    learning_rate: float = 2e-5,
) -> dict:
    manifest_path = Path(manifest_path)
    base_dir = Path(dataset_root) if dataset_root else manifest_path.parent
    df = _load_manifest(manifest_path)
    records = df.to_dict(orient="records")
    texts: list[str] = []
    labels: list[list[int]] = []
    source_splits: list[str] = []
    source_datasets = sorted({str(value).strip() for value in df.get("source_dataset", pd.Series(dtype=str)).dropna().tolist() if str(value).strip()})
    label_sources = sorted({str(value).strip() for value in df.get("label_source", pd.Series(dtype=str)).dropna().tolist() if str(value).strip()})

    for record in records:
        text = str(record.get("text", "") or "").strip()
        if not text:
            continue
        targets = _comorbidity_targets(record)
        if targets is None:
            continue
        texts.append(text)
        labels.append(targets)
        source_splits.append(str(record.get("source_split", "") or "").strip().lower())

    if len(texts) < 32:
        raise ValueError("At least 32 labeled text rows are required to train the transformer model.")

    bundle = _train_text_transformer_classifier(
        texts=texts,
        labels=np.asarray(labels, dtype=int),
        source_splits=source_splits,
        random_state=random_state,
        max_rows=max_rows,
        batch_size=batch_size,
        epochs=epochs,
        learning_rate=learning_rate,
    )
    bundle["manifest_path"] = str(manifest_path.resolve())
    bundle["dataset_root"] = str(base_dir.resolve())
    bundle["source_datasets"] = source_datasets
    bundle["label_sources"] = label_sources
    save_model_bundle("text_transformer", bundle)
    return bundle


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
        choices=(*SUPPORTED_MODALITIES, "audio-sequence", "audio-spectrogram", "image-dl", "comorbidity", "text-transformer", "passive-biomarkers", "all"),
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
    elif args.modality == "text-transformer":
        result = {
            "text_transformer": {
                "status": "trained",
                "bundle": train_text_transformer_model(
                    manifest_path=args.manifest,
                    dataset_root=args.dataset_root,
                ),
            }
        }
    elif args.modality == "audio-sequence":
        result = {
            "audio_sequence": {
                "status": "trained",
                "bundle": _train_audio_sequence_model(
                    manifest_path=args.manifest,
                    dataset_root=args.dataset_root,
                ),
            }
        }
    elif args.modality == "audio-spectrogram":
        result = {
            "audio_spectrogram": {
                "status": "trained",
                "bundle": _train_audio_spectrogram_model(
                    manifest_path=args.manifest,
                    dataset_root=args.dataset_root,
                ),
            }
        }
    elif args.modality == "image-dl":
        result = {
            "image_dl": {
                "status": "trained",
                "bundle": _train_image_cnn_model(
                    manifest_path=args.manifest,
                    dataset_root=args.dataset_root,
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
    elif args.modality == "passive-biomarkers":
        result = {
            "passive_biomarkers": {
                "status": "trained",
                "bundle": train_passive_biomarkers_model(),
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
