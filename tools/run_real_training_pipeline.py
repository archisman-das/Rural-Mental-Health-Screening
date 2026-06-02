import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST_DIR = REPO_ROOT / "data" / "manifests"
DEFAULT_FRAMES_DIR = REPO_ROOT / "data" / "ravdess_frames"
DEFAULT_SUMMARY_PATH = REPO_ROOT / "models" / "mental_health_screening" / "training_pipeline_summary.json"


@dataclass
class DatasetConfig:
    name: str
    root: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate DAIC-WOZ, MELD, and RAVDESS dataset folders, build manifests, "
            "and run the repo training commands end to end."
        )
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Optional JSON config file with dataset roots. Example: examples/dataset_roots.example.json",
    )
    parser.add_argument("--daic-woz-root", type=Path, help="Path to the DAIC-WOZ dataset root.")
    parser.add_argument("--meld-root", type=Path, help="Path to the MELD dataset root.")
    parser.add_argument("--ravdess-root", type=Path, help="Path to the RAVDESS dataset root.")
    parser.add_argument("--skip-daic-woz", action="store_true", help="Skip DAIC-WOZ manifest generation and training.")
    parser.add_argument("--skip-meld", action="store_true", help="Skip MELD manifest generation and training.")
    parser.add_argument("--skip-ravdess", action="store_true", help="Skip RAVDESS manifest generation and training.")
    parser.add_argument(
        "--manifest-dir",
        type=Path,
        default=DEFAULT_MANIFEST_DIR,
        help="Directory where generated manifests will be written.",
    )
    parser.add_argument(
        "--ravdess-frames-dir",
        type=Path,
        default=DEFAULT_FRAMES_DIR,
        help="Directory where extracted RAVDESS frames will be written for image training.",
    )
    parser.add_argument(
        "--min-samples-per-domain",
        type=int,
        default=5,
        help="Minimum usable labeled rows required before a domain model is trained.",
    )
    parser.add_argument(
        "--dataset-root-mode",
        choices=["dataset", "manifest-parent"],
        default="dataset",
        help=(
            "How to pass --dataset-root to the trainer. "
            "'dataset' uses each dataset folder, 'manifest-parent' uses the manifest directory."
        ),
    )
    parser.add_argument(
        "--skip-manifest-build",
        action="store_true",
        help="Skip dataset_prep and assume manifests already exist in --manifest-dir.",
    )
    parser.add_argument(
        "--skip-training",
        action="store_true",
        help="Build manifests only and skip the training phase.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the commands that would run without executing them.",
    )
    parser.add_argument(
        "--summary-path",
        type=Path,
        default=DEFAULT_SUMMARY_PATH,
        help="Where to save the pipeline summary JSON.",
    )
    return parser.parse_args()


def load_config(path: Path | None) -> dict:
    if not path:
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Config file must contain a JSON object.")
    return data


def resolve_dataset_roots(args: argparse.Namespace) -> dict[str, DatasetConfig]:
    config = load_config(args.config)
    roots = {
        "daic_woz_root": args.daic_woz_root or config.get("daic_woz_root"),
        "meld_root": args.meld_root or config.get("meld_root"),
        "ravdess_root": args.ravdess_root or config.get("ravdess_root"),
    }

    resolved: dict[str, DatasetConfig] = {}
    for key, value in roots.items():
        if not value:
            continue
        path = Path(value).expanduser().resolve()
        name = key.replace("_root", "")
        resolved[key] = DatasetConfig(name=name, root=path)
    return resolved


def validate_dataset_roots(dataset_roots: dict[str, DatasetConfig], required_keys: set[str]) -> None:
    missing_keys = sorted(required_keys - set(dataset_roots))
    if missing_keys:
        missing = ", ".join(missing_keys)
        raise FileNotFoundError(
            f"Missing dataset roots for: {missing}. Provide them with flags or --config."
        )

    missing_paths = [str(item.root) for item in dataset_roots.values() if not item.root.exists()]
    if missing_paths:
        raise FileNotFoundError(
            "The following dataset roots do not exist:\n- " + "\n- ".join(missing_paths)
        )


def build_commands(
    dataset_roots: dict[str, DatasetConfig],
    manifest_dir: Path,
    ravdess_frames_dir: Path,
    min_samples_per_domain: int,
    dataset_root_mode: str,
    skip_manifest_build: bool,
    skip_training: bool,
    skip_daic_woz: bool,
    skip_meld: bool,
    skip_ravdess: bool,
) -> list[dict]:
    manifest_dir = manifest_dir.resolve()
    ravdess_frames_dir = ravdess_frames_dir.resolve()

    meld_manifest = manifest_dir / "meld_proxy.csv"
    ravdess_manifest = manifest_dir / "ravdess_proxy.csv"
    daic_manifest = manifest_dir / "daic_clinical.csv"

    commands: list[dict] = []

    if not skip_manifest_build:
        if not skip_meld:
            commands.append(
                {
                    "label": "Build MELD manifest",
                    "command": [
                        sys.executable,
                        "-m",
                        "src.mental_health_screening.dataset_prep",
                        "meld",
                        str(dataset_roots["meld_root"].root),
                        str(meld_manifest),
                    ],
                }
            )
        if not skip_ravdess:
            commands.append(
                {
                    "label": "Build RAVDESS manifest",
                    "command": [
                        sys.executable,
                        "-m",
                        "src.mental_health_screening.dataset_prep",
                        "ravdess",
                        str(dataset_roots["ravdess_root"].root),
                        str(ravdess_manifest),
                        "--extract-frames",
                        str(ravdess_frames_dir),
                    ],
                }
            )
        if not skip_daic_woz:
            commands.append(
                {
                    "label": "Build DAIC-WOZ manifest",
                    "command": [
                        sys.executable,
                        "-m",
                        "src.mental_health_screening.dataset_prep",
                        "daic-woz",
                        str(dataset_roots["daic_woz_root"].root),
                        str(daic_manifest),
                    ],
                }
            )

    if not skip_training:
        if not skip_meld:
            commands.append(
                {
                    "label": "Train text models from MELD",
                    "command": training_command(
                        manifest=meld_manifest,
                        modality="text",
                        dataset_root=dataset_root_for_training(
                            dataset_roots["meld_root"].root, manifest_dir, dataset_root_mode
                        ),
                        min_samples_per_domain=min_samples_per_domain,
                    ),
                }
            )
        if not skip_ravdess:
            commands.extend(
                [
                    {
                        "label": "Train audio models from RAVDESS",
                        "command": training_command(
                            manifest=ravdess_manifest,
                            modality="audio",
                            dataset_root=dataset_root_for_training(
                                dataset_roots["ravdess_root"].root, manifest_dir, dataset_root_mode
                            ),
                            min_samples_per_domain=min_samples_per_domain,
                        ),
                    },
                    {
                        "label": "Train image models from RAVDESS",
                        "command": training_command(
                            manifest=ravdess_manifest,
                            modality="image",
                            dataset_root=dataset_root_for_training(
                                dataset_roots["ravdess_root"].root, manifest_dir, dataset_root_mode
                            ),
                            min_samples_per_domain=min_samples_per_domain,
                        ),
                    },
                ]
            )
        if not skip_daic_woz:
            commands.extend(
                [
                    {
                        "label": "Train text models from DAIC-WOZ",
                        "command": training_command(
                            manifest=daic_manifest,
                            modality="text",
                            dataset_root=dataset_root_for_training(
                                dataset_roots["daic_woz_root"].root, manifest_dir, dataset_root_mode
                            ),
                            min_samples_per_domain=min_samples_per_domain,
                        ),
                    },
                    {
                        "label": "Train audio models from DAIC-WOZ",
                        "command": training_command(
                            manifest=daic_manifest,
                            modality="audio",
                            dataset_root=dataset_root_for_training(
                                dataset_roots["daic_woz_root"].root, manifest_dir, dataset_root_mode
                            ),
                            min_samples_per_domain=min_samples_per_domain,
                        ),
                    },
                ]
            )

    return commands


def dataset_root_for_training(dataset_root: Path, manifest_dir: Path, mode: str) -> Path:
    if mode == "manifest-parent":
        return manifest_dir.resolve()
    return dataset_root.resolve()


def training_command(
    manifest: Path,
    modality: str,
    dataset_root: Path,
    min_samples_per_domain: int,
) -> list[str]:
    return [
        sys.executable,
        "-m",
        "src.mental_health_screening.training",
        str(manifest),
        "--modality",
        modality,
        "--dataset-root",
        str(dataset_root),
        "--min-samples-per-domain",
        str(min_samples_per_domain),
    ]


def ensure_directories(args: argparse.Namespace) -> None:
    args.manifest_dir.mkdir(parents=True, exist_ok=True)
    args.ravdess_frames_dir.mkdir(parents=True, exist_ok=True)
    args.summary_path.parent.mkdir(parents=True, exist_ok=True)


def run_commands(commands: list[dict], dry_run: bool) -> list[dict]:
    results: list[dict] = []
    for item in commands:
        label = item["label"]
        command = item["command"]
        printable = subprocess.list2cmdline(command)
        if dry_run:
            print(f"[dry-run] {label}: {printable}")
            results.append({"label": label, "command": command, "status": "dry-run"})
            continue

        print(f"[run] {label}")
        completed = subprocess.run(command, cwd=REPO_ROOT, check=False)
        status = "ok" if completed.returncode == 0 else "failed"
        results.append(
            {
                "label": label,
                "command": command,
                "status": status,
                "returncode": completed.returncode,
            }
        )
        if completed.returncode != 0:
            raise subprocess.CalledProcessError(completed.returncode, command)
    return results


def write_summary(
    summary_path: Path,
    args: argparse.Namespace,
    dataset_roots: dict[str, DatasetConfig],
    results: list[dict],
) -> None:
    payload = {
        "manifest_dir": str(args.manifest_dir.resolve()),
        "ravdess_frames_dir": str(args.ravdess_frames_dir.resolve()),
        "min_samples_per_domain": args.min_samples_per_domain,
        "dataset_root_mode": args.dataset_root_mode,
        "skip_manifest_build": args.skip_manifest_build,
        "skip_training": args.skip_training,
        "dry_run": args.dry_run,
        "datasets": {key: str(item.root) for key, item in dataset_roots.items()},
        "results": results,
    }
    summary_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> int:
    args = parse_args()
    dataset_roots = resolve_dataset_roots(args)
    required_keys = set()
    if not args.skip_daic_woz:
        required_keys.add("daic_woz_root")
    if not args.skip_meld:
        required_keys.add("meld_root")
    if not args.skip_ravdess:
        required_keys.add("ravdess_root")
    validate_dataset_roots(dataset_roots, required_keys)
    ensure_directories(args)
    commands = build_commands(
        dataset_roots=dataset_roots,
        manifest_dir=args.manifest_dir,
        ravdess_frames_dir=args.ravdess_frames_dir,
        min_samples_per_domain=args.min_samples_per_domain,
        dataset_root_mode=args.dataset_root_mode,
        skip_manifest_build=args.skip_manifest_build,
        skip_training=args.skip_training,
        skip_daic_woz=args.skip_daic_woz,
        skip_meld=args.skip_meld,
        skip_ravdess=args.skip_ravdess,
    )
    results = run_commands(commands, dry_run=args.dry_run)
    write_summary(args.summary_path, args, dataset_roots, results)
    print(f"Pipeline summary written to: {args.summary_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
