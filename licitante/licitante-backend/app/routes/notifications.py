from fastapi import APIRouter, Request, HTTPException, Depends, Path, Query
from ..storage import (
    ensure_dirs, append_user_notice, upsert_call_summary,
    list_user_notices, get_call_summary
)
import json, base64

router = APIRouter()

def _basic_ok(request: Request, expected_user: str | None):
    # Basic auth opcional. Si expected_user está definido, valida que coincida.
    h = request.headers.get("authorization") or request.headers.get("Authorization")
    if not h or not h.lower().startswith("basic "):
        return False
    try:
        raw = base64.b64decode(h.split(" ", 1)[1]).decode("utf-8")
        user, _pwd = raw.split(":", 1)
        if expected_user and user != expected_user:
            return False
        return True
    except Exception:
        return False

@router.on_event("startup")
async def _on_start():
    ensure_dirs()

# === Selección (unitaria) ===
@router.post("/{bidder_id}/api/notifications/selection")
async def selection(bidder_id: str = Path(...), request: Request = None):
    """
    Guarda una notificación unitaria en storage/notifications/by_user/<bidder_id>/YYYYMMDD-HHMMSS.json
    payload esperado:
      { "call_id": "...", "submission_id": "...", "decision": "accepted|rejected",
        "bidder_identifier": "...", "notify_accounts": ["u1","u2"]? }
    """
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido")

    # (opcional) valida Basic del propio bidder
    # if not _basic_ok(request, bidder_id): raise HTTPException(status_code=401, detail="auth inválida")

    # 1) guarda para el owner
    append_user_notice(bidder_id, data)

    # 2) si hay lista de cuentas, hace fan-out para que todos vean el estado en su Inbox
    for u in data.get("notify_accounts") or []:
        if u == bidder_id:
            continue
        append_user_notice(u, data)

    return {"ok": True, "delivered": [bidder_id] + [u for u in (data.get("notify_accounts") or []) if u != bidder_id]}

# === Summary por convocatoria (enviado por el Convocante) ===
@router.post("/api/notifications/summary")
async def summary(request: Request):
    """
    Guarda/actualiza un resumen por convocatoria en storage/notifications/by_call/<call_id>.json
    payload esperado:
      { "call_id": "...", "selected": "...",
        "results": [ { "submission_id": "...", "bidder_identifier": "...", "decision": "..."} ] }
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido")

    call_id = payload.get("call_id")
    if not call_id:
        raise HTTPException(status_code=422, detail="call_id requerido")

    upsert_call_summary(call_id, payload)
    return {"ok": True, "stored": True}

# === Lecturas para el frontend ===
@router.get("/{user}/api/notifications")
async def user_notices(user: str, call_id: str | None = Query(default=None)):
    """ Lista de notificaciones del usuario; opcionalmente filtra por call_id """
    return {"user": user, "call_id": call_id, "items": list_user_notices(user, call_id)}

@router.get("/api/notifications/by-call/{call_id}")
async def call_notices(call_id: str):
    """ Resumen por convocatoria """
    return get_call_summary(call_id)
