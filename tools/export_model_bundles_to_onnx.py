from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import onnxruntime as ort
from skl2onnx import to_onnx

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.mental_health_screening.model_store import ensure_model_dir, get_model_bundle_path, get_onnx_bundle_dir, get_onnx_manifest_path


SUPPORTED_BUNDLES = ("text", "audio", "image", "comorbidity")


def _load_bundle(modality: str) -> dict:
    bundle_path = get_model_bundle_path(modality)
    if not bundle_path.exists():
        raise FileNotFoundError(f"Missing bundle: {bundle_path}")
    import pickle

    with bundle_path.open("rb") as handle:
        return pickle.load(handle)


def _export_estimator(estimator, feature_count: int, output_path: Path, zipmap: bool = False) -> dict:
    sample = np.zeros((1, max(1, feature_count)), dtype=np.float32)
    options = {id(estimator): {"zipmap": False}} if zipmap else None
    onnx_model = to_onnx(estimator, sample, target_opset=17, options=options)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(onnx_model.SerializeToString())

    session = ort.InferenceSession(str(output_path), providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    session.run(None, {input_name: sample})
    return {
        "path": str(output_path),
        "inputs": feature_count,
        "outputs": [output.name for output in session.get_outputs()],
    }


def export_bundle(modality: str, output_dir: Path | None = None) -> dict:
    bundle = _load_bundle(modality)
    feature_names = list(bundle.get("feature_names", []) or [])
    feature_count = len(feature_names) or 1
    target_dir = (output_dir or get_onnx_bundle_dir()) / modality
    target_dir.mkdir(parents=True, exist_ok=True)

    artifacts: dict[str, dict] = {}

    if modality in {"text", "audio", "image"}:
        models = bundle.get("models", {}) or {}
        for domain, estimator in models.items():
            artifact_name = f"{modality}_{domain}.onnx"
            artifact_path = target_dir / artifact_name
            artifacts[domain] = _export_estimator(estimator, feature_count, artifact_path, zipmap=False)
        return {
            "modality": modality,
            "bundle_path": str(get_model_bundle_path(modality)),
            "feature_count": feature_count,
            "artifacts": artifacts,
        }

    if modality == "comorbidity":
        chains = bundle.get("models", []) or []
        for chain_index, chain in enumerate(chains, start=1):
            chain_order = list(chain.get("chain_order", []))
            chain_dir = target_dir / f"chain_{chain_index:02d}"
            chain_dir.mkdir(parents=True, exist_ok=True)
            chain_artifacts = {}
            for model_entry in chain.get("models", []) or []:
                domain = str(model_entry.get("domain") or f"domain_{model_entry.get('domain_index', 0)}")
                estimator = model_entry.get("model")
                if estimator is None:
                    continue
                artifact_path = chain_dir / f"{domain}.onnx"
                chain_artifacts[domain] = _export_estimator(estimator, feature_count, artifact_path, zipmap=False)
            artifacts[f"chain_{chain_index:02d}"] = {
                "chain_order": chain_order,
                "artifacts": chain_artifacts,
            }
        return {
            "modality": modality,
            "bundle_path": str(get_model_bundle_path(modality)),
            "feature_count": feature_count,
            "artifacts": artifacts,
        }

    raise ValueError(f"Unsupported modality: {modality}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Export trained model bundles to ONNX while keeping pickle bundles intact.")
    parser.add_argument("--modality", action="append", choices=SUPPORTED_BUNDLES, help="Modality to export. Repeatable. Defaults to all.")
    args = parser.parse_args()

    ensure_model_dir()
    get_onnx_bundle_dir()
    modalities = args.modality or list(SUPPORTED_BUNDLES)

    manifest = {}
    for modality in modalities:
        manifest[modality] = export_bundle(modality)

    manifest_path = get_onnx_manifest_path()
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote ONNX manifest to {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
