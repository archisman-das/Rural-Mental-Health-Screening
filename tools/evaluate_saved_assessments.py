from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from sklearn.metrics import accuracy_score, brier_score_loss, confusion_matrix, precision_recall_fscore_support, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = str(ROOT / "src")
if SRC_PATH not in sys.path:
    sys.path.append(SRC_PATH)

from mental_health_screening.constants import PREDICTION_DOMAINS
from mental_health_screening.utils import risk_level


RISK_LABELS = ("low", "moderate", "high")
HIGH_RISK_THRESHOLD = 0.66
DEFAULT_LABEL_THRESHOLDS = (0.33, 0.66)


@dataclass(frozen=True)
class DomainExample:
    assessment_id: str
    domain: str
    questionnaire_score: float
    questionnaire_label: str
    predicted_score: float
    predicted_label: str
    confidence: float


def _clean_label(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in RISK_LABELS:
        return text
    return None


def _coerce_float(value: object) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _extract_label(raw_label: object, score: float | None) -> str | None:
    label = _clean_label(raw_label)
    if label is not None:
        return label
    if score is None:
        return None
    return risk_level(score)


def _extract_prediction_label(raw_label: object, score: float | None) -> str | None:
    label = _clean_label(raw_label)
    if label is not None:
        return label
    raw_text = str(raw_label or "").strip().lower()
    if raw_text in {"unknown", "unavailable", "n/a", "na", "none"}:
        return None
    if score is None:
        return None
    return risk_level(score)


def _score_to_label(score: float, low_threshold: float, high_threshold: float) -> str:
    if score < low_threshold:
        return "low"
    if score < high_threshold:
        return "moderate"
    return "high"


def _threshold_candidates(scores: Iterable[float]) -> list[float]:
    scores_list = [float(score) for score in scores if score is not None]
    cleaned = sorted({round(score, 3) for score in scores_list if 0.0 < score < 1.0})
    candidates = {round(DEFAULT_LABEL_THRESHOLDS[0], 3), round(DEFAULT_LABEL_THRESHOLDS[1], 3), *cleaned}
    ordered = sorted(candidate for candidate in candidates if 0.0 < candidate < 1.0)
    if len(ordered) > 40:
        quantiles = np.unique(np.quantile(np.asarray(scores_list, dtype=float), np.linspace(0.05, 0.95, 19))).tolist()
        ordered = sorted({round(float(value), 3) for value in quantiles if 0.0 < float(value) < 1.0} | set(ordered[:12]) | {round(DEFAULT_LABEL_THRESHOLDS[0], 3), round(DEFAULT_LABEL_THRESHOLDS[1], 3)})
    return [0.0] + ordered + [1.0]


def _best_label_thresholds(examples: list[DomainExample]) -> tuple[float, float]:
    if not examples:
        return DEFAULT_LABEL_THRESHOLDS

    candidate_scores = _threshold_candidates(item.predicted_score for item in examples)
    truth = [item.questionnaire_label for item in examples]
    best_low, best_high = DEFAULT_LABEL_THRESHOLDS
    best_macro_f1 = -1.0
    best_accuracy = -1.0

    for low_threshold in candidate_scores:
        for high_threshold in candidate_scores:
            if high_threshold <= low_threshold + 0.02:
                continue
            predicted = [_score_to_label(item.predicted_score, low_threshold, high_threshold) for item in examples]
            accuracy = float(accuracy_score(truth, predicted))
            _, _, macro_f1, _ = precision_recall_fscore_support(
                truth,
                predicted,
                labels=list(RISK_LABELS),
                average="macro",
                zero_division=0,
            )
            if macro_f1 > best_macro_f1 or (macro_f1 == best_macro_f1 and accuracy > best_accuracy):
                best_low = float(low_threshold)
                best_high = float(high_threshold)
                best_macro_f1 = float(macro_f1)
                best_accuracy = accuracy

    return best_low, best_high


def _calibrated_predicted_label(example: DomainExample, thresholds_by_domain: dict[str, tuple[float, float]] | None = None) -> str:
    low_threshold, high_threshold = (thresholds_by_domain or {}).get(example.domain, DEFAULT_LABEL_THRESHOLDS)
    return _score_to_label(example.predicted_score, low_threshold, high_threshold)


def _load_records(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [record for record in payload if isinstance(record, dict)]
    if isinstance(payload, dict) and isinstance(payload.get("records"), list):
        return [record for record in payload["records"] if isinstance(record, dict)]
    raise ValueError(f"Unsupported assessment export format in {path}")


def _iter_domain_examples(records: Iterable[dict], domains: Iterable[str]) -> list[DomainExample]:
    examples: list[DomainExample] = []
    for record in records:
        questionnaire = record.get("questionnaire") or {}
        multimodal = record.get("multimodal") or {}
        overall = multimodal.get("overall") or {}
        overall_scores = overall.get("scores") or {}
        assessment_id = str(record.get("assessment_id") or "UNKNOWN")
        confidence = _coerce_float(overall.get("confidence")) or 0.0

        for domain in domains:
            questionnaire_score = _coerce_float(questionnaire.get(f"{domain}_score"))
            predicted_score = _coerce_float(overall_scores.get(domain))
            if questionnaire_score is None or predicted_score is None:
                continue

            questionnaire_label = _extract_label(questionnaire.get(f"{domain}_risk"), questionnaire_score)
            predicted_label = _extract_prediction_label(overall.get(domain), predicted_score)
            if questionnaire_label is None or predicted_label is None:
                continue

            examples.append(
                DomainExample(
                    assessment_id=assessment_id,
                    domain=domain,
                    questionnaire_score=questionnaire_score,
                    questionnaire_label=questionnaire_label,
                    predicted_score=predicted_score,
                    predicted_label=predicted_label,
                    confidence=confidence,
                )
            )
    return examples


def _safe_roc_auc(y_true: list[int], y_prob: list[float]) -> float | None:
    if len(set(y_true)) < 2:
        return None
    try:
        return float(roc_auc_score(y_true, y_prob))
    except ValueError:
        return None


def _summarize_examples(
    examples: list[DomainExample],
    thresholds_by_domain: dict[str, tuple[float, float]] | None = None,
) -> dict:
    if not examples:
        return {
            "count": 0,
            "accuracy": None,
            "macro_precision": None,
            "macro_recall": None,
            "macro_f1": None,
            "weighted_f1": None,
            "brier_score": None,
            "roc_auc": None,
            "score_mae": None,
            "confidence_mean": None,
            "confusion_matrix": [],
            "per_class": {},
        }

    y_true = [item.questionnaire_label for item in examples]
    y_pred = [_calibrated_predicted_label(item, thresholds_by_domain) for item in examples]
    y_true_binary = [1 if item.questionnaire_score >= HIGH_RISK_THRESHOLD else 0 for item in examples]
    y_prob_binary = [item.predicted_score for item in examples]

    precision, recall, f1, support = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=list(RISK_LABELS),
        average=None,
        zero_division=0,
    )
    macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=list(RISK_LABELS),
        average="macro",
        zero_division=0,
    )
    _, _, weighted_f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=list(RISK_LABELS),
        average="weighted",
        zero_division=0,
    )

    cm = confusion_matrix(y_true, y_pred, labels=list(RISK_LABELS))
    brier = brier_score_loss(y_true_binary, y_prob_binary) if len(set(y_true_binary)) > 1 else None
    roc_auc = _safe_roc_auc(y_true_binary, y_prob_binary)
    score_mae = sum(abs(item.questionnaire_score - item.predicted_score) for item in examples) / len(examples)
    confidence_mean = sum(item.confidence for item in examples) / len(examples)

    per_class = {}
    for index, label in enumerate(RISK_LABELS):
        per_class[label] = {
            "precision": float(precision[index]),
            "recall": float(recall[index]),
            "f1": float(f1[index]),
            "support": int(support[index]),
        }

    return {
        "count": len(examples),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_precision": float(macro_precision),
        "macro_recall": float(macro_recall),
        "macro_f1": float(macro_f1),
        "weighted_f1": float(weighted_f1),
        "brier_score": None if brier is None else float(brier),
        "roc_auc": roc_auc,
        "score_mae": float(score_mae),
        "confidence_mean": float(confidence_mean),
        "confusion_matrix": cm.tolist(),
        "per_class": per_class,
    }


def _top_mismatches(
    examples: list[DomainExample],
    thresholds_by_domain: dict[str, tuple[float, float]] | None = None,
    limit: int = 10,
) -> list[dict]:
    ranked = sorted(
        examples,
        key=lambda item: (
            item.questionnaire_label != _calibrated_predicted_label(item, thresholds_by_domain),
            abs(item.questionnaire_score - item.predicted_score),
        ),
        reverse=True,
    )
    return [
        {
            "assessment_id": item.assessment_id,
            "domain": item.domain,
            "questionnaire_label": item.questionnaire_label,
            "predicted_label": _calibrated_predicted_label(item, thresholds_by_domain),
            "questionnaire_score": round(item.questionnaire_score, 3),
            "predicted_score": round(item.predicted_score, 3),
            "confidence": round(item.confidence, 3),
            "score_gap": round(abs(item.questionnaire_score - item.predicted_score), 3),
        }
        for item in ranked[:limit]
    ]


def _format_metric(value: object) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _print_domain_report(domain: str, summary: dict) -> None:
    print(f"\n[{domain}]")
    print(f"  samples: {summary['count']}")
    print(f"  accuracy: {_format_metric(summary['accuracy'])}")
    print(f"  macro precision: {_format_metric(summary['macro_precision'])}")
    print(f"  macro recall: {_format_metric(summary['macro_recall'])}")
    print(f"  macro F1: {_format_metric(summary['macro_f1'])}")
    print(f"  weighted F1: {_format_metric(summary['weighted_f1'])}")
    print(f"  Brier score: {_format_metric(summary['brier_score'])}")
    print(f"  ROC AUC: {_format_metric(summary['roc_auc'])}")
    print(f"  score MAE: {_format_metric(summary['score_mae'])}")
    print(f"  mean confidence: {_format_metric(summary['confidence_mean'])}")
    print("  confusion matrix [low, moderate, high]:")
    for row in summary["confusion_matrix"]:
        print(f"    {row}")


def build_report(records: list[dict], domains: list[str]) -> dict:
    examples = _iter_domain_examples(records, domains)
    by_domain: dict[str, list[DomainExample]] = {domain: [] for domain in domains}
    for example in examples:
        by_domain.setdefault(example.domain, []).append(example)

    label_thresholds = {
        domain: _best_label_thresholds(by_domain.get(domain, []))
        for domain in domains
    }
    domain_reports = {
        domain: _summarize_examples(by_domain.get(domain, []), thresholds_by_domain={domain: label_thresholds.get(domain, DEFAULT_LABEL_THRESHOLDS)})
        for domain in domains
    }
    overall_report = _summarize_examples(examples, thresholds_by_domain=label_thresholds)
    mismatch_report = _top_mismatches(examples, thresholds_by_domain=label_thresholds)

    return {
        "record_count": len(records),
        "domain_count": len(domains),
        "example_count": len(examples),
        "domains": domains,
        "label_thresholds": {
            domain: {"low": float(thresholds[0]), "high": float(thresholds[1])}
            for domain, thresholds in label_thresholds.items()
        },
        "overall": overall_report,
        "by_domain": domain_reports,
        "top_mismatches": mismatch_report,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate saved assessments as a proxy benchmark by comparing questionnaire risk labels "
            "against multimodal dashboard predictions."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data") / "screening_results.json",
        help="Path to the saved assessment JSON export.",
    )
    parser.add_argument(
        "--domains",
        nargs="*",
        choices=list(PREDICTION_DOMAINS),
        default=list(PREDICTION_DOMAINS),
        help="Optional subset of domains to evaluate.",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=None,
        help="Optional path to write the evaluation report as JSON.",
    )
    parser.add_argument(
        "--mismatches",
        type=int,
        default=10,
        help="Number of high-gap examples to print and include in the report.",
    )
    args = parser.parse_args()

    records = _load_records(args.input)
    report = build_report(records, list(args.domains))
    report["top_mismatches"] = report["top_mismatches"][: max(0, int(args.mismatches))]

    print(f"Loaded {report['record_count']} saved assessments from {args.input}")
    print(
        "This is a proxy evaluation: questionnaire risk labels are treated as the reference "
        "and multimodal dashboard outputs are treated as predictions."
    )
    print(f"Compared {report['example_count']} domain-level examples across {report['domain_count']} domains.")
    print("\n[Overall]")
    overall = report["overall"]
    print(f"  samples: {overall['count']}")
    print(f"  accuracy: {_format_metric(overall['accuracy'])}")
    print(f"  macro precision: {_format_metric(overall['macro_precision'])}")
    print(f"  macro recall: {_format_metric(overall['macro_recall'])}")
    print(f"  macro F1: {_format_metric(overall['macro_f1'])}")
    print(f"  weighted F1: {_format_metric(overall['weighted_f1'])}")
    print(f"  Brier score: {_format_metric(overall['brier_score'])}")
    print(f"  ROC AUC: {_format_metric(overall['roc_auc'])}")
    print(f"  score MAE: {_format_metric(overall['score_mae'])}")
    print(f"  mean confidence: {_format_metric(overall['confidence_mean'])}")

    for domain in report["domains"]:
        _print_domain_report(domain, report["by_domain"][domain])

    if report["top_mismatches"]:
        print("\n[Top Mismatches]")
        for item in report["top_mismatches"]:
            print(
                f"  {item['assessment_id']} | {item['domain']} | "
                f"q={item['questionnaire_label']} ({item['questionnaire_score']:.3f}) -> "
                f"p={item['predicted_label']} ({item['predicted_score']:.3f}) | "
                f"gap={item['score_gap']:.3f}"
            )

    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nWrote JSON report to {args.json_output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
