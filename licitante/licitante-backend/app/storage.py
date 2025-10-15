from pathlib import Path
from .config import settings
import json, time

# === rutas base ===
def _base() -> Path:
    return settings.STORAGE_BASE

def timestamp_slug() -> str:
    return time.strftime("%Y%m%d-%H%M%S")

def ensure_dirs():
    (_base()).mkdir(parents=True, exist_ok=True)
    settings.SUBMISSIONS_DIR.mkdir(parents=True, exist_ok=True)
    settings.NOTIFICATIONS_DIR.mkdir(parents=True, exist_ok=True)
    (settings.NOTIFICATIONS_DIR / "by_user").mkdir(parents=True, exist_ok=True)
    (settings.NOTIFICATIONS_DIR / "by_call").mkdir(parents=True, exist_ok=True)
    if not settings.ACCOUNTS_FILE.exists():
        settings.ACCOUNTS_FILE.write_text("{}", encoding="utf-8")

# === json helpers ===
def save_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

def read_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default

# === accounts ===
def load_accounts() -> dict:
    return read_json(settings.ACCOUNTS_FILE, {})

def save_accounts(acc: dict):
    save_json(settings.ACCOUNTS_FILE, acc)

def resolve_notify_info():
    """
    accounts.json típico:
      {
        "active": "5555",     # opcional
        "5555": "pwd",
        "lola": "pwd2"
      }
    Retorna: (bidder_identifier, notify_group_id, notify_accounts)
    """
    data = load_accounts() or {}
    if not isinstance(data, dict):
        return None, None, []
    all_users = [k for k in data.keys() if k != "active"]
    bidder_identifier = None
    if "active" in data and data["active"] in all_users:
        bidder_identifier = data["active"]
    elif len(all_users) == 1:
        bidder_identifier = all_users[0]
    notify_accounts = all_users
    notify_group_id = None
    return bidder_identifier, notify_group_id, notify_accounts

# === notifications storage ===
def notice_path_user(user: str) -> Path:
    return settings.NOTIFICATIONS_DIR / "by_user" / user

def notice_path_call(call_id: str) -> Path:
    return settings.NOTIFICATIONS_DIR / "by_call" / f"{call_id}.json"

def append_user_notice(user: str, notice: dict):
    box = notice_path_user(user)
    box.mkdir(parents=True, exist_ok=True)
    fname = box / f"{timestamp_slug()}.json"
    save_json(fname, notice)

def upsert_call_summary(call_id: str, summary: dict):
    """
    summary esperado:
      { "call_id": ..., "selected": "...",
        "results": [ { "submission_id": "...", "bidder_identifier": "...", "decision": "..."} ] }
    """
    path = notice_path_call(call_id)
    save_json(path, summary)

def list_user_notices(user: str, call_id: str | None = None):
    box = notice_path_user(user)
    out = []
    if not box.exists():
        return out
    for f in sorted(box.iterdir()):
        if f.suffix.lower() != ".json":
            continue
        try:
            item = read_json(f, None)
            if item is None:
                continue
            if call_id and item.get("call_id") != call_id:
                continue
            out.append(item)
        except Exception:
            continue
    return out

def get_call_summary(call_id: str):
    return read_json(notice_path_call(call_id), {"call_id": call_id, "results": []})
