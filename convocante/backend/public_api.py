from fastapi import APIRouter, HTTPException
from pathlib import Path
from config import CALLS_DIR, APP_PREFIX

router = APIRouter(prefix=f"{APP_PREFIX}/api", tags=["public"])

def _latest_call_dir() -> Path | None:
    if not CALLS_DIR.exists():
        return None
    dirs = [p for p in CALLS_DIR.iterdir() if p.is_dir()]
    if not dirs:
        return None
    dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return dirs[0]

@router.get("/active-call")
def get_active_call():
    d = _latest_call_dir()
    if not d:
        raise HTTPException(404, "no calls")
    pem = d / "rsa_pub.pem"
    if not pem.exists():
        raise HTTPException(500, "missing rsa_pub.pem")
    key_path = d / "key_id.txt"
    key_id = key_path.read_text(encoding="utf-8").strip() if key_path.exists() else "default"
    return {"ok": True, "call_id": d.name, "key_id": key_id, "rsa_pub_pem": pem.read_text(encoding="utf-8")}

@router.get("/call/{call_id}")
def get_call_pub(call_id: str):
    d = CALLS_DIR / call_id
    if not d.exists():
        raise HTTPException(404, "call_id not found")
    pem = d / "rsa_pub.pem"
    if not pem.exists():
        raise HTTPException(500, "missing rsa_pub.pem")
    key_path = d / "key_id.txt"
    key_id = key_path.read_text(encoding="utf-8").strip() if key_path.exists() else "default"
    return {"ok": True, "call_id": call_id, "key_id": key_id, "rsa_pub_pem": pem.read_text(encoding="utf-8")}
