from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mental_health_screening.training import _train_audio_sequence_model  # noqa: E402
from mental_health_screening.model_store import save_model_bundle  # noqa: E402


def main() -> None:
    try:
        print("starting_audio_sequence_training", flush=True)
        best_bundle = None
        best_seed = None
        best_macro_f1 = -1.0
        for seed in (42, 84, 126):
            bundle = _train_audio_sequence_model(
                manifest_path=ROOT / "data" / "manifests" / "ravdess_proxy.csv",
                dataset_root=ROOT / "data" / "manifests",
                random_state=seed,
                max_rows=0,
                batch_size=32,
                epochs=8,
                max_frames=24,
            )
            macro_f1 = float(bundle.get("metrics", {}).get("macro_f1", 0.0) or 0.0)
            print(f"seed {seed} macro_f1 {macro_f1}", flush=True)
            if macro_f1 > best_macro_f1:
                best_macro_f1 = macro_f1
                best_seed = seed
                best_bundle = bundle
        if best_bundle is None:
            raise RuntimeError("No audio sequence bundle was produced.")
        bundle = best_bundle
        save_model_bundle("audio_sequence", bundle)
        print(f"finished_audio_sequence_training best_seed={best_seed}", flush=True)
        output = {
            "bundle_path": str((ROOT / "tmp_datasets" / "audio_sequence_bundle.pkl").resolve()),
            "metrics": bundle.get("metrics", {}),
            "sample_count": bundle.get("sample_count"),
            "model_type": bundle.get("model_type"),
            "best_seed": best_seed,
        }
        (ROOT / "tmp_datasets" / "audio_sequence_train_result.json").write_text(
            json.dumps(output, indent=2),
            encoding="utf-8",
        )
        print("wrote_audio_sequence_result", flush=True)
    except Exception as exc:
        error_path = ROOT / "tmp_datasets" / "audio_sequence_train_error.txt"
        error_path.write_text(
            "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
            encoding="utf-8",
        )
        print(f"audio_sequence_training_failed: {exc}", flush=True)
        raise


if __name__ == "__main__":
    main()
