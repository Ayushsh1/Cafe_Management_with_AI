import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def _ensure_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_json(filename: str, default: Any) -> Any:
    _ensure_dir()
    file_path = DATA_DIR / filename
    if not file_path.exists():
        save_json(filename, default)
        return default
    with file_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)

def save_json(filename: str, payload: Any) -> None:
    _ensure_dir()
    file_path = DATA_DIR / filename
    with file_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
