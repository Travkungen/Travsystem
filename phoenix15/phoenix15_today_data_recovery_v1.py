"""Phoenix 15 today_data recovery utility.

Purpose:
    Persist the exact discovery input used by a live Phoenix 15 run so a
    Colab runtime restart does not destroy the input needed by the pipeline.

Rules:
    - Does not modify SQLite.
    - Does not modify the trained model.
    - Stores/reloads today_data only.
    - Intended to be used immediately after today_data is created.
"""

import json
from pathlib import Path


VERSION = "1.0"


def save_today_data(today_data, path):
    """Save the exact today_data object as UTF-8 JSON."""
    if not isinstance(today_data, dict):
        raise TypeError("today_data måste vara dict")

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(today_data, f, ensure_ascii=False, indent=2, default=str)

    return path


def load_today_data(path):
    """Reload a previously saved today_data object."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"today_data saknas: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise RuntimeError("Sparad today_data måste vara dict")

    return data
