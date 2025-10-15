# app/routes/accounts.py
from fastapi import APIRouter, HTTPException, Request
from pathlib import Path
import json
from ..storage import settings, ensure_dirs

router = APIRouter(prefix="/api", tags=["accounts"])

def _acc_file() -> Path:
    ensure_dirs()
    return settings.ACCOUNTS_FILE

def _read_accounts() -> dict:
    p = _acc_file()
    if not p.exists():
        return {"active": None}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"active": None}

def _write_accounts(d: dict):
    p = _acc_file()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

@router.get("/accounts")
async def list_accounts():
    d = _read_accounts()
    users = [k for k in d.keys() if k != "active"]
    return {"active": d.get("active"), "users": users}

@router.post("/accounts")
async def create_account(req: Request):
    try:
        body = await req.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido")

    bidder_id = (body or {}).get("bidder_id")
    password = (body or {}).get("password")
    if not bidder_id or not password:
        raise HTTPException(status_code=422, detail="bidder_id y password son requeridos")

    d = _read_accounts()
    if bidder_id in d:
        raise HTTPException(status_code=409, detail="la cuenta ya existe")
    d[bidder_id] = password
    if not d.get("active"):
        d["active"] = bidder_id
    _write_accounts(d)
    return {"ok": True, "created": bidder_id, "active": d.get("active")}

@router.post("/accounts/active")
async def set_active(req: Request):
    try:
        body = await req.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido")
    user = (body or {}).get("user")
    if not user:
        raise HTTPException(status_code=422, detail="user requerido")
    d = _read_accounts()
    if user not in d:
        raise HTTPException(status_code=404, detail="usuario no existe")
    d["active"] = user
    _write_accounts(d)
    return {"ok": True, "active": user}
