from __future__ import annotations

import runpy
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    module_path = REPO_ROOT / "src" / "mental_health_screening" / "voice_training.py"
    runpy.run_path(str(module_path), run_name="__main__")
