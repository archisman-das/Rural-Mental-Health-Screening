from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "manifests" / "federated_centres"
SUPPORTED_MODALITIES = ("text", "audio", "image", "all")
DEFAULT_CENTRE_COLUMNS = (
    "health_centre",
    "health_center",
    "centre_id",
    "center_id",
    "site",
    "clinic",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Split a combined manifest into one manifest per health centre and optionally "
            "run federated training across those centre manifests."
        )
    )
    parser.add_argument(
        "manifest",
        type=Path,
        help="Path to a CSV, JSON, or JSONL manifest with rows from multiple health centres.",
    )
    parser.add_argument(
        "--centre-column",
        default=None,
        help=(
            "Column to group by when splitting the manifest. "
            f"If omitted, the script auto-detects one of: {', '.join(DEFAULT_CENTRE_COLUMNS)}."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where the per-centre manifest files will be written.",
    )
    parser.add_argument(
        "--manifest-prefix",
        default=None,
        help="Optional filename prefix for the generated split manifests.",
    )
    parser.add_argument(
        "--modality",
        choices=SUPPORTED_MODALITIES,
        default="all",
        help="Train one modality or all supported modalities after splitting.",
    )
    parser.add_argument(
        "--domains",
        default=None,
        help="Optional comma-separated subset of domains to train, for example: depression,stress",
    )
    parser.add_argument(
        "--min-center-samples",
        dest="min_center_samples",
        type=int,
        default=4,
        help="Minimum usable rows a health centre must contribute for a domain in federated learning.",
    )
    parser.add_argument(
        "--federated-rounds",
        type=int,
        default=6,
        help="Number of federated communication rounds.",
    )
    parser.add_argument(
        "--local-epochs",
        type=int,
        default=2,
        help="Number of local epochs each centre runs per federated round.",
    )
    parser.add_argument(
        "--skip-training",
        action="store_true",
        help="Only split the manifest and stop before training.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the split plan and training command without writing or executing anything.",
    )
    return parser.parse_args()


def _load_manifest(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")
    if path.suffix.lower() == ".jsonl":
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        return pd.DataFrame(rows)
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        return pd.DataFrame(payload)
    return pd.read_csv(path)


def _normalize_value(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return None
    return text


def _sanitize_slug(value: str) -> str:
    slug = []
    for character in value.strip():
        if character.isalnum() or character in {"-", "_"}:
            slug.append(character)
        else:
            slug.append("_")
    cleaned = "".join(slug).strip("_")
    return cleaned or "centre"


def _detect_centre_column(frame: pd.DataFrame, requested: str | None) -> str:
    if requested:
        if requested not in frame.columns:
            raise ValueError(f"Centre column '{requested}' was not found in the manifest.")
        return requested

    for column in DEFAULT_CENTRE_COLUMNS:
        if column in frame.columns:
            return column

    raise ValueError(
        "Could not auto-detect a centre column. "
        f"Add one of {DEFAULT_CENTRE_COLUMNS} or pass --centre-column explicitly."
    )


def split_manifest(
    manifest_path: Path,
    output_dir: Path,
    centre_column: str | None,
    prefix: str | None,
    dry_run: bool,
) -> tuple[list[Path], str]:
    frame = _load_manifest(manifest_path)
    resolved_centre_column = _detect_centre_column(frame, centre_column)

    usable_frame = frame.copy()
    usable_frame[resolved_centre_column] = usable_frame[resolved_centre_column].map(_normalize_value)
    usable_frame = usable_frame[usable_frame[resolved_centre_column].notna()].copy()
    if usable_frame.empty:
        raise ValueError(f"No usable centre values were found in column '{resolved_centre_column}'.")

    generated_paths: list[Path] = []
    base_prefix = prefix or manifest_path.stem

    for centre_value, centre_frame in usable_frame.groupby(resolved_centre_column, dropna=True, sort=True):
        slug = _sanitize_slug(str(centre_value))
        output_path = output_dir / f"{base_prefix}__{slug}.csv"
        output_frame = centre_frame.copy()
        if "centre_id" not in output_frame.columns and "center_id" not in output_frame.columns:
            output_frame.insert(0, "centre_id", str(centre_value))
        if not dry_run:
            output_dir.mkdir(parents=True, exist_ok=True)
            output_frame.to_csv(output_path, index=False)
        generated_paths.append(output_path.resolve())

    return generated_paths, resolved_centre_column


def _parse_domains_argument(raw_value: str | None) -> str | None:
    if raw_value is None:
        return None
    domains = [value.strip() for value in raw_value.split(",") if value.strip()]
    return ",".join(domains) if domains else None


def build_training_command(
    manifest_paths: list[Path],
    modality: str,
    domains: str | None,
    min_center_samples: int,
    federated_rounds: int,
    local_epochs: int,
) -> list[str]:
    command = [
        sys.executable,
        "-m",
        "src.mental_health_screening.training",
        str(manifest_paths[0]),
        "--modality",
        modality,
        "--federated-manifests",
        ",".join(str(path) for path in manifest_paths),
        "--min-center-samples",
        str(min_center_samples),
        "--federated-rounds",
        str(federated_rounds),
        "--local-epochs",
        str(local_epochs),
    ]
    if domains:
        command.extend(["--domains", domains])
    return command


def main() -> int:
    args = parse_args()
    manifest_path = args.manifest.resolve()
    output_dir = args.output_dir.resolve()
    domains = _parse_domains_argument(args.domains)

    split_paths, resolved_centre_column = split_manifest(
        manifest_path=manifest_path,
        output_dir=output_dir,
        centre_column=args.centre_column,
        prefix=args.manifest_prefix,
        dry_run=args.dry_run,
    )

    if not args.skip_training and len(split_paths) < 2:
        raise ValueError(
            "Federated training needs at least two centre manifests. "
            "Use --skip-training if you only want to split the manifest."
        )

    split_summary = {
        "manifest": str(manifest_path),
        "centre_column": resolved_centre_column,
        "output_dir": str(output_dir),
        "split_manifests": [str(path) for path in split_paths],
    }
    print(json.dumps(split_summary, indent=2))

    if args.skip_training:
        return 0

    command = build_training_command(
        manifest_paths=split_paths,
        modality=args.modality,
        domains=domains,
        min_center_samples=args.min_center_samples,
        federated_rounds=args.federated_rounds,
        local_epochs=args.local_epochs,
    )
    printable = subprocess.list2cmdline(command)
    if args.dry_run:
        print(f"[dry-run] {printable}")
        return 0

    completed = subprocess.run(command, cwd=REPO_ROOT, check=False)
    if completed.returncode != 0:
        raise subprocess.CalledProcessError(completed.returncode, command)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
