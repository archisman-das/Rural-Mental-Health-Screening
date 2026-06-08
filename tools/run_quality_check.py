from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = str(ROOT / "src")
TOOLS_PATH = str(ROOT / "tools")
if SRC_PATH not in sys.path:
    sys.path.append(SRC_PATH)
if TOOLS_PATH not in sys.path:
    sys.path.append(TOOLS_PATH)

from evaluate_saved_assessments import build_report, _print_domain_report, _format_metric, _load_records  # noqa: E402
from mental_health_screening.constants import PREDICTION_DOMAINS  # noqa: E402


def _metric_pass(metric_name: str, value: object, minimum: float | None, maximum: float | None) -> tuple[str, bool]:
    if value is None:
        return f"{metric_name}=n/a", False
    numeric = float(value)
    if minimum is not None and numeric < minimum:
        return f"{metric_name}={numeric:.3f} < {minimum:.3f}", False
    if maximum is not None and numeric > maximum:
        return f"{metric_name}={numeric:.3f} > {maximum:.3f}", False
    return f"{metric_name}={numeric:.3f}", True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a saved-assessment quality check and write a JSON report."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data") / "screening_results.json",
        help="Path to the saved assessment JSON export.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data") / "assessment_quality_report.json",
        help="Path to write the JSON quality report.",
    )
    parser.add_argument(
        "--mismatches",
        type=int,
        default=10,
        help="Number of mismatch examples to keep in the report.",
    )
    parser.add_argument(
        "--domains",
        nargs="*",
        choices=list(PREDICTION_DOMAINS),
        default=list(PREDICTION_DOMAINS),
        help="Optional subset of domains to evaluate.",
    )
    parser.add_argument(
        "--min-accuracy",
        type=float,
        default=0.70,
        help="Minimum overall accuracy required for a PASS.",
    )
    parser.add_argument(
        "--min-macro-f1",
        type=float,
        default=0.70,
        help="Minimum overall macro F1 required for a PASS.",
    )
    parser.add_argument(
        "--max-brier-score",
        type=float,
        default=0.25,
        help="Maximum overall Brier score allowed for a PASS.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return exit code 1 when the quality checks do not meet the configured thresholds.",
    )
    args = parser.parse_args()

    records = _load_records(args.input)
    report = build_report(records, list(args.domains))
    report["top_mismatches"] = report["top_mismatches"][: max(0, int(args.mismatches))]
    report["quality_thresholds"] = {
        "min_accuracy": float(args.min_accuracy),
        "min_macro_f1": float(args.min_macro_f1),
        "max_brier_score": float(args.max_brier_score),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    overall = report["overall"]
    print(f"Quality report written to {args.output}")
    print(f"Records: {report['record_count']} | Examples: {report['example_count']}")
    print(f"Accuracy: {_format_metric(overall['accuracy'])} | Macro F1: {_format_metric(overall['macro_f1'])} | ROC AUC: {_format_metric(overall['roc_auc'])}")
    if report.get("label_thresholds"):
        print("Calibrated label thresholds:")
        for domain, thresholds in report["label_thresholds"].items():
            print(f"  - {domain}: low<{_format_metric(thresholds['low'])}, high≥{_format_metric(thresholds['high'])}")

    checks = [
        _metric_pass("accuracy", overall["accuracy"], args.min_accuracy, None),
        _metric_pass("macro_f1", overall["macro_f1"], args.min_macro_f1, None),
        _metric_pass("brier_score", overall["brier_score"], None, args.max_brier_score),
    ]
    failed_checks = [message for message, passed in checks if not passed]
    if failed_checks:
        print("Quality gate: FAIL")
        for message in failed_checks:
            print(f"  - {message}")
    else:
        print("Quality gate: PASS")

    for domain in report["domains"]:
        _print_domain_report(domain, report["by_domain"][domain])
    if report["top_mismatches"]:
        print("\nTop mismatches:")
        for item in report["top_mismatches"]:
            print(
                f"  {item['assessment_id']} | {item['domain']} | "
                f"{item['questionnaire_label']} -> {item['predicted_label']} "
                f"(gap {item['score_gap']:.3f})"
            )

    if args.strict and failed_checks:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
