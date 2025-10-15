from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from ..models import SelectionNotification
from ..config import settings
from ..storage import save_json, timestamp_slug, load_accounts, save_accounts

router = APIRouter(tags=["notifications"])
security = HTTPBasic()


def verify_credentials(bidder_id: str, cred: HTTPBasicCredentials):
    if cred.username != bidder_id:
        raise HTTPException(status_code=401, detail="invalid user")
    acc = load_accounts()
    pwd = acc.get(bidder_id)
    if not pwd or pwd != cred.password:
        raise HTTPException(status_code=401, detail="invalid password")


@router.post("/{bidder_id}/api/notifications/selection")
def selection_notify(
    bidder_id: str,
    n: SelectionNotification,
    cred: HTTPBasicCredentials = Depends(security),
):
    # HTTP Basic: user = bidder_id, pass = contraseña registrada
    verify_credentials(bidder_id, cred)

    ts = timestamp_slug()
    path = settings.NOTIFICATIONS_DIR / bidder_id / f"{n.call_id}_{ts}.json"
    save_json(path, n.dict())
    return {"ok": True, "stored": path.as_posix()}


@router.get("/api/notifications/selection")
def list_selection_notifications(bidder_id: str | None = None):
    """Lista notificaciones (global o filtradas por licitante)."""
    import json
    from pathlib import Path

    base = settings.NOTIFICATIONS_DIR if not bidder_id else (settings.NOTIFICATIONS_DIR / bidder_id)
    items = []
    if base.exists():
        for p in sorted(base.rglob("*.json"), reverse=True):
            try:
                items.append(json.loads(p.read_text(encoding="utf-8")))
            except Exception:
                continue
    return items


# ===== Gestión simple de cuentas (para simular varios licitantes) =====

class AccountIn(BaseModel):
    bidder_id: str
    password: str


@router.post("/api/accounts")
def create_account(payload: AccountIn):
    acc = load_accounts()
    acc[payload.bidder_id] = payload.password
    save_accounts(acc)
    return {"ok": True, "created": payload.bidder_id}


@router.get("/api/accounts")
def list_accounts():
    acc = load_accounts()
    return [{"bidder_id": k} for k in sorted(acc.keys())]
