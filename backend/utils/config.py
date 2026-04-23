from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml


CONFIG_PATH = Path(__file__).resolve().parents[2] / "config.yaml"


def load_config() -> Dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)
