import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST_DIR = REPO_ROOT / "data" / "manifests"
DEFAULT_FRAMES_DIR = REPO_ROOT / "data" / "ravdess_frames"
DEFAULT_FEDERATED_OUTPUT_DIR = DEFAULT_MANIFEST_DIR / "federated_centres"
DEFAULT_VOICE_OUTPUT_DIR = REPO_ROOT / "models" / "mental_health_screening" / "voice"
DEFAULT_SUMMARY_PATH = REPO_ROOT / "models" / "mental_health_screening" / "training_pipeline_summary.json"
DEFAULT_COMORBIDITY_BALANCED_MANIFEST = REPO_ROOT / "tmp_datasets" / "comorbidity_60k.csv"
DEFAULT_COMORBIDITY_BUCKET_TARGETS = "0:12000,1:12000,2:12000,3:12000,4:12000"
DEFAULT_COMORBIDITY_TARGET_ROWS = 60000


@dataclass
class DatasetConfig:
    name: str
    root: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate DAIC-WOZ, MELD, RAVDESS, and CREMA-D dataset folders, build manifests, "
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
    parser.add_argument("--crema-d-root", type=Path, help="Path to the CREMA-D dataset root.")
    parser.add_argument("--tess-root", type=Path, help="Path to the TESS dataset root.")
    parser.add_argument("--skip-daic-woz", action="store_true", help="Skip DAIC-WOZ manifest generation and training.")
    parser.add_argument("--skip-meld", action="store_true", help="Skip MELD manifest generation and training.")
    parser.add_argument("--skip-ravdess", action="store_true", help="Skip RAVDESS manifest generation and training.")
    parser.add_argument("--skip-crema-d", action="store_true", help="Skip CREMA-D manifest generation and training.")
    parser.add_argument("--skip-tess", action="store_true", help="Skip TESS manifest generation and training.")
    parser.add_argument(
        "--federated-manifest",
        type=Path,
        default=None,
        help=(
            "Optional combined manifest to split by health centre and train with federated averaging "
            "using tools/run_federated_training.py."
        ),
    )
    parser.add_argument(
        "--federated-centre-column",
        default=None,
        help="Optional centre column name to use when splitting --federated-manifest.",
    )
    parser.add_argument(
        "--federated-output-dir",
        type=Path,
        default=DEFAULT_FEDERATED_OUTPUT_DIR,
        help="Directory where split per-centre manifests will be written.",
    )
    parser.add_argument(
        "--federated-manifest-prefix",
        default=None,
        help="Optional filename prefix for split per-centre manifests.",
    )
    parser.add_argument(
        "--federated-modality",
        choices=["text", "audio", "image", "all"],
        default="all",
        help="Which modality to train during the federated run.",
    )
    parser.add_argument(
        "--federated-domains",
        default=None,
        help="Optional comma-separated domain subset for the federated run.",
    )
    parser.add_argument(
        "--federated-min-center-samples",
        type=int,
        default=4,
        help="Minimum usable rows each centre must contribute for federated training.",
    )
    parser.add_argument(
        "--federated-rounds",
        type=int,
        default=6,
        help="Number of federated communication rounds.",
    )
    parser.add_argument(
        "--federated-local-epochs",
        type=int,
        default=2,
        help="Number of local epochs each centre runs per federated round.",
    )
    parser.add_argument(
        "--voice-manifest",
        type=Path,
        default=None,
        help=(
            "Optional voice manifest with audio_path, transcript/text, language, and dialect columns "
            "to fine-tune a rural Bengali/Hindi ASR model."
        ),
    )
    parser.add_argument(
        "--voice-model-family",
        choices=["wav2vec2", "whisper"],
        default="wav2vec2",
        help="Choose which voice backbone to fine-tune.",
    )
    parser.add_argument(
        "--voice-base-model-name",
        default=None,
        help="Optional local Whisper or wav2vec2 checkpoint name/path to fine-tune from.",
    )
    parser.add_argument(
        "--voice-output-dir",
        type=Path,
        default=DEFAULT_VOICE_OUTPUT_DIR,
        help="Directory where per-dialect fine-tuned voice models will be written.",
    )
    parser.add_argument(
        "--voice-min-samples-per-dialect",
        type=int,
        default=8,
        help="Minimum rows required to train a voice dialect slice.",
    )
    parser.add_argument(
        "--voice-per-dialect",
        action="store_true",
        default=True,
        help="Train separate voice models per dialect slice.",
    )
    parser.add_argument(
        "--voice-no-per-dialect",
        action="store_false",
        dest="voice_per_dialect",
        help="Train one shared voice model instead of separate dialect slices.",
    )
    parser.add_argument(
        "--voice-epochs",
        type=int,
        default=3,
        help="Number of fine-tuning epochs for the voice model.",
    )
    parser.add_argument(
        "--voice-batch-size",
        type=int,
        default=4,
        help="Training batch size for the voice model.",
    )
    parser.add_argument(
        "--voice-learning-rate",
        type=float,
        default=3e-5,
        help="Fine-tuning learning rate for the voice model.",
    )
    parser.add_argument(
        "--voice-random-state",
        type=int,
        default=42,
        help="Random seed used for the voice train/eval split.",
    )
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
        "--comorbidity-balanced-manifest",
        type=Path,
        default=DEFAULT_COMORBIDITY_BALANCED_MANIFEST,
        help="Where to write the balanced comorbidity manifest.",
    )
    parser.add_argument(
        "--comorbidity-bucket-targets",
        default=DEFAULT_COMORBIDITY_BUCKET_TARGETS,
        help="Comma-separated bucket targets for comorbidity balancing, for example 0:600,1:600,2:500,3:600,4:1400.",
    )
    parser.add_argument(
        "--comorbidity-target-rows",
        type=int,
        default=DEFAULT_COMORBIDITY_TARGET_ROWS,
        help="Target row count for the bootstrapped comorbidity manifest.",
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


def _resolve_config_value(
    args: argparse.Namespace,
    config: dict,
    name: str,
    default: object | None = None,
) -> object | None:
    current_value = getattr(args, name)
    if current_value != default and current_value is not None:
        return current_value
    if name in config:
        return config[name]
    return current_value if current_value is not None else default


def apply_config_overrides(args: argparse.Namespace, config: dict) -> None:
    for field_name in ("daic_woz_root", "meld_root", "ravdess_root", "crema_d_root", "tess_root"):
        if getattr(args, field_name) is None and config.get(field_name) is not None:
            setattr(args, field_name, config.get(field_name))

    for field_name, default_value in (
        ("manifest_dir", DEFAULT_MANIFEST_DIR),
        ("ravdess_frames_dir", DEFAULT_FRAMES_DIR),
        ("summary_path", DEFAULT_SUMMARY_PATH),
        ("dataset_root_mode", "dataset"),
        ("min_samples_per_domain", 5),
        ("federated_manifest", None),
        ("federated_centre_column", None),
        ("federated_output_dir", DEFAULT_FEDERATED_OUTPUT_DIR),
        ("federated_manifest_prefix", None),
        ("federated_modality", "all"),
        ("federated_domains", None),
        ("federated_min_center_samples", 4),
        ("federated_rounds", 6),
        ("federated_local_epochs", 2),
        ("voice_manifest", None),
        ("voice_model_family", "wav2vec2"),
        ("voice_base_model_name", None),
        ("voice_output_dir", DEFAULT_VOICE_OUTPUT_DIR),
        ("voice_min_samples_per_dialect", 8),
        ("voice_per_dialect", True),
        ("voice_epochs", 3),
        ("voice_batch_size", 4),
        ("voice_learning_rate", 3e-5),
        ("voice_random_state", 42),
        ("comorbidity_balanced_manifest", DEFAULT_COMORBIDITY_BALANCED_MANIFEST),
        ("comorbidity_bucket_targets", DEFAULT_COMORBIDITY_BUCKET_TARGETS),
        ("comorbidity_target_rows", DEFAULT_COMORBIDITY_TARGET_ROWS),
    ):
        value = _resolve_config_value(args, config, field_name, default=default_value)
        if value is not None:
            if field_name in {"manifest_dir", "ravdess_frames_dir", "summary_path", "federated_output_dir", "federated_manifest", "voice_manifest", "voice_output_dir", "comorbidity_balanced_manifest"}:
                setattr(args, field_name, Path(value))
            else:
                setattr(args, field_name, value)

    for field_name in ("skip_daic_woz", "skip_meld", "skip_ravdess", "skip_crema_d", "skip_tess", "skip_manifest_build", "skip_training", "dry_run"):
        if config.get(field_name):
            setattr(args, field_name, True)

    if "voice_per_dialect" in config:
        setattr(args, "voice_per_dialect", bool(config.get("voice_per_dialect")))


def load_config(path: Path | None) -> dict:
    if not path:
        return {}
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("Config file must contain a JSON object.")
    return data


def resolve_dataset_roots(args: argparse.Namespace) -> dict[str, DatasetConfig]:
    config = load_config(args.config)
    roots = {
        "daic_woz_root": args.daic_woz_root or config.get("daic_woz_root"),
        "meld_root": args.meld_root or config.get("meld_root"),
        "ravdess_root": args.ravdess_root or config.get("ravdess_root"),
        "crema_d_root": args.crema_d_root or config.get("crema_d_root"),
        "tess_root": args.tess_root or config.get("tess_root"),
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

    missing_paths = [str(dataset_roots[key].root) for key in sorted(required_keys) if not dataset_roots[key].root.exists()]
    if missing_paths:
        raise FileNotFoundError(
            "The following dataset roots do not exist:\n- " + "\n- ".join(missing_paths)
        )


def build_commands(
    dataset_roots: dict[str, DatasetConfig],
    manifest_dir: Path,
    ravdess_frames_dir: Path,
    federated_manifest: Path | None,
    federated_centre_column: str | None,
    federated_output_dir: Path,
    federated_manifest_prefix: str | None,
    federated_modality: str,
    federated_domains: str | None,
    federated_min_center_samples: int,
    federated_rounds: int,
    federated_local_epochs: int,
    voice_manifest: Path | None,
    voice_model_family: str,
    voice_base_model_name: str | None,
    voice_output_dir: Path,
    voice_min_samples_per_dialect: int,
    voice_per_dialect: bool,
    voice_epochs: int,
    voice_batch_size: int,
    voice_learning_rate: float,
    voice_random_state: int,
    min_samples_per_domain: int,
    comorbidity_balanced_manifest: Path,
    comorbidity_bucket_targets: str,
    comorbidity_target_rows: int,
    dataset_root_mode: str,
    skip_manifest_build: bool,
    skip_training: bool,
    skip_daic_woz: bool,
    skip_meld: bool,
    skip_ravdess: bool,
    skip_crema_d: bool,
    skip_tess: bool,
) -> list[dict]:
    manifest_dir = manifest_dir.resolve()
    ravdess_frames_dir = ravdess_frames_dir.resolve()
    federated_output_dir = federated_output_dir.resolve()
    voice_output_dir = voice_output_dir.resolve()

    meld_manifest = manifest_dir / "meld_proxy.csv"
    ravdess_manifest = manifest_dir / "ravdess_proxy.csv"
    crema_d_manifest = manifest_dir / "crema_d_proxy.csv"
    tess_manifest = manifest_dir / "tess_proxy.csv"
    speech_audio_manifest = manifest_dir / "speech_audio_combined.csv"
    daic_manifest = manifest_dir / "daic_clinical.csv"
    comorbidity_manifest = comorbidity_balanced_manifest.resolve()
    audio_source_manifests: list[Path] = []
    if not skip_ravdess and "ravdess_root" in dataset_roots:
        audio_source_manifests.append(ravdess_manifest)
    if not skip_crema_d and "crema_d_root" in dataset_roots:
        audio_source_manifests.append(crema_d_manifest)
    if not skip_tess and "tess_root" in dataset_roots:
        audio_source_manifests.append(tess_manifest)

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
        if not skip_crema_d and "crema_d_root" in dataset_roots:
            commands.append(
                {
                    "label": "Build CREMA-D manifest",
                    "command": [
                        sys.executable,
                        "-m",
                        "src.mental_health_screening.dataset_prep",
                        "crema-d",
                        str(dataset_roots["crema_d_root"].root),
                        str(crema_d_manifest),
                    ],
                }
            )
        if not skip_tess and "tess_root" in dataset_roots:
            commands.append(
                {
                    "label": "Build TESS manifest",
                    "command": [
                        sys.executable,
                        "-m",
                        "src.mental_health_screening.dataset_prep",
                        "tess",
                        str(dataset_roots["tess_root"].root),
                        str(tess_manifest),
                    ],
                }
            )
        if not skip_meld and not skip_ravdess:
            commands.append(
                {
                    "label": "Build balanced comorbidity manifest",
                    "command": [
                        sys.executable,
                        "-m",
                        "src.mental_health_screening.dataset_prep",
                        "comorbidity-expand",
                        str(meld_manifest),
                        str(ravdess_manifest),
                        "--output-path",
                        str(comorbidity_manifest),
                        "--target-rows",
                        str(comorbidity_target_rows),
                        "--bucket-targets",
                        comorbidity_bucket_targets,
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
        if audio_source_manifests:
            source_weights = []
            if not skip_ravdess and "ravdess_root" in dataset_roots:
                source_weights.append("RAVDESS=1")
            if not skip_crema_d and "crema_d_root" in dataset_roots:
                source_weights.append("CREMA-D=2")
            if not skip_tess and "tess_root" in dataset_roots:
                source_weights.append("TESS=5")
            commands.append(
                {
                    "label": "Build combined speech audio manifest",
                    "command": [
                        sys.executable,
                        "-m",
                        "src.mental_health_screening.dataset_prep",
                        "combine-manifests",
                        *[str(path) for path in audio_source_manifests],
                        "--output-path",
                        str(speech_audio_manifest),
                        *sum([["--source-weight", weight] for weight in source_weights], []),
                    ],
                }
            )

    if federated_manifest is not None:
        commands.append(
            {
                "label": "Split and train federated centres",
                "command": federated_training_command(
                    manifest=federated_manifest.resolve(),
                    output_dir=federated_output_dir,
                    centre_column=federated_centre_column,
                    manifest_prefix=federated_manifest_prefix,
                    modality=federated_modality,
                    domains=federated_domains,
                    min_center_samples=federated_min_center_samples,
                    federated_rounds=federated_rounds,
                    local_epochs=federated_local_epochs,
                    skip_training=skip_training,
                ),
            }
        )
    if voice_manifest is not None and not skip_training:
        commands.append(
            {
                "label": "Fine-tune rural voice model",
                "command": voice_training_command(
                    manifest=voice_manifest.resolve(),
                    model_family=voice_model_family,
                    base_model_name=voice_base_model_name,
                    output_dir=voice_output_dir,
                    min_samples_per_dialect=voice_min_samples_per_dialect,
                    per_dialect=voice_per_dialect,
                    epochs=voice_epochs,
                    batch_size=voice_batch_size,
                    learning_rate=voice_learning_rate,
                    random_state=voice_random_state,
                ),
            }
        )
    if not skip_training:
        if not skip_meld and not skip_ravdess:
            commands.append(
                {
                    "label": "Train comorbidity model from balanced manifest",
                    "command": training_command(
                        manifest=comorbidity_manifest,
                        modality="comorbidity",
                        dataset_root=dataset_root_for_training(
                            manifest_dir, manifest_dir, "manifest-parent"
                        ),
                        min_samples_per_domain=min_samples_per_domain,
                    ),
                }
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
                ]
            )
        if audio_source_manifests:
            commands.append(
                {
                    "label": "Train audio models from combined speech corpora",
                    "command": training_command(
                        manifest=speech_audio_manifest,
                        modality="audio",
                        dataset_root=dataset_root_for_training(manifest_dir, manifest_dir, "manifest-parent"),
                        min_samples_per_domain=min_samples_per_domain,
                    ),
                }
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


def federated_training_command(
    manifest: Path,
    output_dir: Path,
    centre_column: str | None,
    manifest_prefix: str | None,
    modality: str,
    domains: str | None,
    min_center_samples: int,
    federated_rounds: int,
    local_epochs: int,
    skip_training: bool,
) -> list[str]:
    command = [
        sys.executable,
        str(REPO_ROOT / "tools" / "run_federated_training.py"),
        str(manifest),
        "--output-dir",
        str(output_dir),
        "--modality",
        modality,
        "--min-center-samples",
        str(min_center_samples),
        "--federated-rounds",
        str(federated_rounds),
        "--local-epochs",
        str(local_epochs),
    ]
    if centre_column:
        command.extend(["--centre-column", centre_column])
    if manifest_prefix:
        command.extend(["--manifest-prefix", manifest_prefix])
    if domains:
        command.extend(["--domains", domains])
    if skip_training:
        command.append("--skip-training")
    return command


def voice_training_command(
    manifest: Path,
    model_family: str,
    base_model_name: str | None,
    output_dir: Path,
    min_samples_per_dialect: int,
    per_dialect: bool,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    random_state: int,
) -> list[str]:
    command = [
        sys.executable,
        str(REPO_ROOT / "tools" / "run_voice_finetuning.py"),
        str(manifest),
        "--model-family",
        model_family,
        "--output-dir",
        str(output_dir),
        "--min-samples-per-dialect",
        str(min_samples_per_dialect),
        "--epochs",
        str(epochs),
        "--batch-size",
        str(batch_size),
        "--learning-rate",
        str(learning_rate),
        "--random-state",
        str(random_state),
    ]
    if base_model_name:
        command.extend(["--base-model-name", base_model_name])
    if not per_dialect:
        command.append("--no-per-dialect")
    return command


def ensure_directories(args: argparse.Namespace) -> None:
    args.manifest_dir.mkdir(parents=True, exist_ok=True)
    args.ravdess_frames_dir.mkdir(parents=True, exist_ok=True)
    args.comorbidity_balanced_manifest.parent.mkdir(parents=True, exist_ok=True)
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
        "federated_manifest": str(args.federated_manifest.resolve()) if args.federated_manifest else None,
        "federated_centre_column": args.federated_centre_column,
        "federated_output_dir": str(args.federated_output_dir.resolve()),
        "federated_manifest_prefix": args.federated_manifest_prefix,
        "federated_modality": args.federated_modality,
        "federated_domains": args.federated_domains,
        "federated_min_center_samples": args.federated_min_center_samples,
        "federated_rounds": args.federated_rounds,
        "federated_local_epochs": args.federated_local_epochs,
        "voice_manifest": str(args.voice_manifest.resolve()) if args.voice_manifest else None,
        "voice_model_family": args.voice_model_family,
        "voice_base_model_name": args.voice_base_model_name,
        "voice_output_dir": str(args.voice_output_dir.resolve()),
        "voice_min_samples_per_dialect": args.voice_min_samples_per_dialect,
        "voice_per_dialect": args.voice_per_dialect,
        "voice_epochs": args.voice_epochs,
        "voice_batch_size": args.voice_batch_size,
        "voice_learning_rate": args.voice_learning_rate,
        "voice_random_state": args.voice_random_state,
        "min_samples_per_domain": args.min_samples_per_domain,
        "comorbidity_balanced_manifest": str(args.comorbidity_balanced_manifest.resolve()),
        "comorbidity_bucket_targets": args.comorbidity_bucket_targets,
        "comorbidity_target_rows": args.comorbidity_target_rows,
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
    config = load_config(args.config)
    apply_config_overrides(args, config)
    dataset_roots = resolve_dataset_roots(args)
    required_keys = set()
    if not args.skip_daic_woz:
        required_keys.add("daic_woz_root")
    if not args.skip_meld:
        required_keys.add("meld_root")
    if not args.skip_ravdess:
        required_keys.add("ravdess_root")
    if not args.skip_crema_d and (args.crema_d_root is not None or config.get("crema_d_root") is not None):
        required_keys.add("crema_d_root")
    if not args.skip_tess and (args.tess_root is not None or config.get("tess_root") is not None):
        required_keys.add("tess_root")
    validate_dataset_roots(dataset_roots, required_keys)
    ensure_directories(args)
    commands = build_commands(
        dataset_roots=dataset_roots,
        manifest_dir=args.manifest_dir,
        ravdess_frames_dir=args.ravdess_frames_dir,
        federated_manifest=args.federated_manifest,
        federated_centre_column=args.federated_centre_column,
        federated_output_dir=args.federated_output_dir,
        federated_manifest_prefix=args.federated_manifest_prefix,
        federated_modality=args.federated_modality,
        federated_domains=args.federated_domains,
        federated_min_center_samples=args.federated_min_center_samples,
        federated_rounds=args.federated_rounds,
        federated_local_epochs=args.federated_local_epochs,
        voice_manifest=args.voice_manifest,
        voice_model_family=args.voice_model_family,
        voice_base_model_name=args.voice_base_model_name,
        voice_output_dir=args.voice_output_dir,
        voice_min_samples_per_dialect=args.voice_min_samples_per_dialect,
        voice_per_dialect=args.voice_per_dialect,
        voice_epochs=args.voice_epochs,
        voice_batch_size=args.voice_batch_size,
        voice_learning_rate=args.voice_learning_rate,
        voice_random_state=args.voice_random_state,
        min_samples_per_domain=args.min_samples_per_domain,
        comorbidity_balanced_manifest=args.comorbidity_balanced_manifest,
        comorbidity_bucket_targets=args.comorbidity_bucket_targets,
        comorbidity_target_rows=args.comorbidity_target_rows,
        dataset_root_mode=args.dataset_root_mode,
        skip_manifest_build=args.skip_manifest_build,
        skip_training=args.skip_training,
        skip_daic_woz=args.skip_daic_woz,
        skip_meld=args.skip_meld,
        skip_ravdess=args.skip_ravdess,
        skip_crema_d=args.skip_crema_d,
        skip_tess=args.skip_tess,
    )
    results = run_commands(commands, dry_run=args.dry_run)
    write_summary(args.summary_path, args, dataset_roots, results)
    print(f"Pipeline summary written to: {args.summary_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
