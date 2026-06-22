from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mental_health_screening.model_store import save_model_bundle  # noqa: E402
from mental_health_screening.training import train_text_transformer_model  # noqa: E402


def main() -> None:
    manifest_path = ROOT / "data" / "manifests" / "meld_proxy.csv"
    dataset_root = ROOT / "data" / "manifests"
    best_bundle = None
    best_seed = None
    best_macro_f1 = -1.0
    for seed in (42, 84, 126):
        bundle = train_text_transformer_model(
            manifest_path=manifest_path,
            dataset_root=dataset_root,
            random_state=seed,
            max_rows=8000,
            batch_size=8,
            epochs=2,
            learning_rate=2e-5,
        )
        macro_f1 = float(bundle.get("metrics", {}).get("macro_f1", 0.0) or 0.0)
        print(f"seed {seed} macro_f1 {macro_f1}", flush=True)
        if macro_f1 > best_macro_f1:
            best_macro_f1 = macro_f1
            best_seed = seed
            best_bundle = bundle

    if best_bundle is None:
        raise RuntimeError("No text transformer bundle was produced.")

    save_model_bundle("text_transformer", best_bundle)

    output = {
        "bundle_path": str((ROOT / "tmp_datasets" / "text_transformer_bundle.pkl").resolve()),
        "metrics": best_bundle.get("metrics", {}),
        "sample_count": best_bundle.get("sample_count"),
        "model_type": best_bundle.get("model_type"),
        "best_seed": best_seed,
    }
    (ROOT / "tmp_datasets" / "text_transformer_sweep_result.json").write_text(
        json.dumps(output, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
