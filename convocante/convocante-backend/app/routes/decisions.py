from fastapi import APIRouter, HTTPException, Request, Form, Query
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import httpx, json, base64

from ..config import settings
from ..storage import save_json

router = APIRouter(prefix="/api", tags=["decisions"])

# ---------- Utilidades básicas ----------

class DecisionIn(BaseModel):
    call_id: str
    bidder_identifier: str
    decision: str = Field(..., pattern="^(accepted|rejected)$")
    notes: str | None = None

def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

def _basic_auth_header(username: str, password: str) -> dict:
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}

def _load_credentials() -> dict:
    try:
        return json.loads(settings.LICITANTE_CREDENTIALS_JSON or "{}")
    except Exception:
        return {}

def _pick(d: Dict[str, Any] | None, *keys):
    if not isinstance(d, dict):
        return None
    for k in keys:
        v = d.get(k)
        if v not in (None, ""):
            return v
    return None

# ---------- Notificación unitaria (ya existente) ----------

@router.post("/decisions")
async def set_decision(d: DecisionIn):
    notify_url = f"{settings.LICITANTE_BASE}/{d.bidder_identifier}/api/notifications/selection"
    creds = _load_credentials()
    pwd = creds.get(d.bidder_identifier)
    if not pwd:
        raise HTTPException(status_code=400, detail=f"sin credenciales para {d.bidder_identifier}")
    headers = _basic_auth_header(d.bidder_identifier, pwd)

    payload = {
        "call_id": d.call_id,
        "bidder_identifier": d.bidder_identifier,
        "decision": d.decision,
        "notes": d.notes,
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(notify_url, json=payload, headers=headers)
            if r.status_code >= 400:
                raise HTTPException(status_code=502, detail={"licitante_status": r.status_code, "text": r.text})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"error notificando licitante: {e}")

    record = {
        "call_id": d.call_id,
        "bidder_identifier": d.bidder_identifier,
        "decision": d.decision,
        "notes": d.notes,
        "notified": True,
        "at": _iso(datetime.utcnow()),
        "notify_url": notify_url,
    }
    out_dir = (getattr(settings, "STORAGE_BASE", Path("data")) / "decisions")
    out_dir.mkdir(parents=True, exist_ok=True)
    save_json(out_dir / f"{d.call_id}_decision_{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json", record)

    return {"ok": True, "notified": True, "notify_url": notify_url}

# ---------- Helpers para selección de ganador ----------

def _iter_processed_submissions(call_id: str):
    base = settings.PROCESSED_DIR / call_id
    out = []
    if base.exists():
        for subdir in base.iterdir():
            if not subdir.is_dir():
                continue
            res = subdir / "result.json"
            if res.exists():
                try:
                    data = json.loads(res.read_text(encoding="utf-8"))
                    out.append((subdir.name, data))
                except Exception:
                    continue
    return out

def _targets_from_meta(meta: dict) -> List[dict]:
    """
    Devuelve una lista de destinos de notificación.
    Orden de prioridad:
    1) bidder_identifier o bidder.identifier
    2) callbacks.selection.url (+ auth)
    3) notify_accounts (fan-out)
    4) claves de LICITANTE_CREDENTIALS_JSON (fan-out de desarrollo)
    Cada item: {"url": str, "headers": dict, "kind": "bidder|url", "bidder": optional}
    """
    targets: List[dict] = []
    creds = _load_credentials()

    # 1) bidder directo
    bidder = (
        meta.get("bidder_identifier")
        or (meta.get("bidder") or {}).get("identifier")
    )
    if bidder:
        pwd = creds.get(bidder)
        headers = _basic_auth_header(bidder, pwd) if pwd else {}
        targets.append({
            "url": f"{settings.LICITANTE_BASE}/{bidder}/api/notifications/selection",
            "headers": headers, "kind": "bidder", "bidder": bidder
        })
        return targets

    # 2) callback url explícita en meta
    cb = ((meta or {}).get("callbacks") or {}).get("selection") or {}
    url = cb.get("url")
    if url:
        headers = {}
        auth = cb.get("auth") or {}
        scheme = (auth.get("scheme") or "").lower()
        if scheme == "basic":
            headers = _basic_auth_header(auth.get("username") or "", auth.get("token_or_password") or "")
        elif scheme == "bearer":
            headers = {"Authorization": f"Bearer {auth.get('token_or_password','')}"}
        targets.append({"url": url, "headers": headers, "kind": "url"})
        return targets

    # 3) notify_accounts (fan-out)
    accounts = meta.get("notify_accounts") or []
    for u in accounts:
        pwd = creds.get(u)
        headers = _basic_auth_header(u, pwd) if pwd else {}
        targets.append({
            "url": f"{settings.LICITANTE_BASE}/{u}/api/notifications/selection",
            "headers": headers, "kind": "bidder", "bidder": u
        })
    if targets:
        return targets

    # 4) fan-out a todos los credenciales (fallback de desarrollo)
    for u, pwd in creds.items():
        headers = _basic_auth_header(u, pwd)
        targets.append({
            "url": f"{settings.LICITANTE_BASE}/{u}/api/notifications/selection",
            "headers": headers, "kind": "bidder", "bidder": u
        })
    return targets

async def _post_notify(url: str, headers: dict, payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(url, json=payload, headers=headers)
        return {"status_code": r.status_code, "text": r.text, "notify_url": url}

# ---------- Seleccionar ganador (acepta uno y rechaza el resto) ----------

@router.post("/decisions/select")
async def select_winner(
    request: Request,
    # FORM (x-www-form-urlencoded)
    call_id_f: str | None = Form(default=None, alias="call_id"),
    submission_id_f: str | None = Form(default=None, alias="submission_id"),
    notes_f: str | None = Form(default=None, alias="notes"),
    # QUERY (?call_id=&submission_id=)
    call_id_q: str | None = Query(default=None, alias="call_id"),
    submission_id_q: str | None = Query(default=None, alias="submission_id"),
    notes_q: str | None = Query(default=None, alias="notes"),
):
    """
    Acepta call_id y submission_id por: query, form o JSON (también camelCase).
    Envía 'accepted' al ganador y 'rejected' al resto de submissions del mismo call_id.
    """
    call_id = call_id_f or call_id_q
    submission_id = submission_id_f or submission_id_q
    notes = notes_f or notes_q

    # JSON opcional
    if not (call_id and submission_id):
        try:
            body = await request.json()
        except Exception:
            body = None
        if isinstance(body, dict):
            call_id = call_id or body.get("call_id") or body.get("callId")
            submission_id = submission_id or body.get("submission_id") or body.get("submissionId")
            notes = notes or body.get("notes")

    if not (call_id and submission_id):
        raise HTTPException(status_code=422, detail="call_id y submission_id son requeridos")

    # Recorre submissions procesadas del call y notifica
    subs = _iter_processed_submissions(call_id)
    if not subs:
        raise HTTPException(status_code=404, detail="No hay submissions para ese call_id")

    results = []
    for sub_id, data in subs:
        meta = (data.get("meta") or {})

        decision = "accepted" if sub_id == submission_id else "rejected"
        payload = {
            "call_id": call_id,
            "submission_id": sub_id,
            "decision": decision,
            "bidder_identifier": (
                meta.get("bidder_identifier")
                or (meta.get("bidder") or {}).get("identifier")
            ),
            "notify_group_id": meta.get("notify_group_id"),
            "notify_accounts": meta.get("notify_accounts"),
            "notes": notes,
        }

        try:
            targets = _targets_from_meta(meta)
            if not targets:
                r = {"ok": False, "reason": "sin destino de notificación"}
            else:
                r = []
                for t in targets:
                    rr = await _post_notify(t["url"], t["headers"], payload)
                    r.append(rr)
            results.append({"submission_id": sub_id, "decision": decision, "notify_result": r})
        except Exception as e:
            results.append({"submission_id": sub_id, "decision": decision, "error": str(e)})

    # Guardar resumen
    out_dir = (getattr(settings, "STORAGE_BASE", Path("data")) / "decisions")
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "call_id": call_id,
        "selected": submission_id,
        "at": _iso(datetime.utcnow()),
        "count": len(results),
    }
    save_json(out_dir / f"{call_id}_select_{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json", summary)
        # Guardar resumen local
    out_dir = (getattr(settings, "STORAGE_BASE", Path("data")) / "decisions")
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "call_id": call_id,
        "selected": submission_id,
        "at": _iso(datetime.utcnow()),
        "results": [
            {
                "submission_id": it["submission_id"],
                "decision": it["decision"],
                "bidder_identifier": (
                    ( (it.get("notify_result") or [{}])[0].get("bidder") )  # si lo devolviste así
                    if isinstance(it.get("notify_result"), list) else None
                )
            } for it in results
        ],
    }
    save_json(out_dir / f"{call_id}_select_{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json", summary)

    # -------- NUEVO: enviar summary al licitante --------
    try:
        lic_base = settings.LICITANTE_BASE.rstrip("/")
        async with httpx.AsyncClient(timeout=15) as client:
            await client.post(f"{lic_base}/api/notifications/summary", json=summary)
    except Exception:
        # no rompemos el éxito de selección si el summary falla
        pass

    return {"ok": True, "call_id": call_id, "selected": submission_id, "results": results}

