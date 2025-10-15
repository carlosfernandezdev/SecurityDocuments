from pathlib import Path
from .config import settings
import json, time

def ensure_dirs():
    # Asegura carpetas base
    for d in [settings.STORAGE_BASE, settings.SUBMISSIONS_DIR, settings.NOTIFICATIONS_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    # Asegura archivo de cuentas
    if not settings.ACCOUNTS_FILE.exists():
        settings.ACCOUNTS_FILE.write_text("{}", encoding="utf-8")

def timestamp_slug() -> str:
    return time.strftime("%Y%m%d-%H%M%S")

def save_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

def read_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default

def load_accounts() -> dict:
    return read_json(settings.ACCOUNTS_FILE, {})

def save_accounts(acc: dict):
    save_json(settings.ACCOUNTS_FILE, acc)
