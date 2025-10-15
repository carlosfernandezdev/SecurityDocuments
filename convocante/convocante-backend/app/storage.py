from pathlib import Path
from .config import settings
import json, time

def ensure_dirs():
    for d in [settings.INBOX_DIR, settings.PROCESSED_DIR, settings.QUARANTINE_DIR, settings.KEYS_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def save_bytes(path: Path, data: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)

def save_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

def timestamp_slug() -> str:
    return time.strftime("%Y%m%d-%H%M%S")
