import json
import logging
from typing import Dict, Any
import httpx
from fastapi import APIRouter, HTTPException, Request

from config import APP_PREFIX
from services.store import save_call_files, list_calls, call_dir, now_iso

router = APIRouter(prefix=f"{APP_PREFIX}/api", tags=["calls"])

@router.get("/calls")
def api_list_calls():
    return {"ok": True, "calls": list_calls()}

@router.post("/calls/create")
async def api_create_call(call_id: str, key_id: str = "default", request: Request = None):
    # Crea y persiste claves/archivos
    call = save_call_files(call_id, key_id)

    # Payload con URL ABSOLUTA para el push (el relativo se queda en la respuesta pública)
    base_url = str(request.base_url).rstrip("/") if request else ""
    push_payload = {**call, "rsa_pub_pem_url": f"{base_url}{call['rsa_pub_pem_url']}"}

    # Notifica licitantes (best-effort, no rompe si falla)
    try:
        await _notify_licitantes(request, push_payload)
    except Exception as e:
        logging.warning("notify licitantes failed: %s", e)

    return {"ok": True, "call": call}

@router.get("/calls/{call_id}")
def api_get_call(call_id: str, request: Request = None):
    d = call_dir(call_id)
    if not d.exists():
        raise HTTPException(404, "call_id not found")
    key_id = (d / "key_id.txt").read_text(encoding="utf-8").strip() if (d / "key_id.txt").exists() else "default"
    try:
        created = json.loads((d / "meta.json").read_text(encoding="utf-8")).get("created_at")
    except Exception:
        created = now_iso()
    return {"ok": True, "call": {
        "call_id": call_id,
        "key_id": key_id,
        "rsa_pub_pem_url": f"{APP_PREFIX}/public/keys/{call_id}/rsa_pub.pem",
        "created_at": created,
    }}

@router.post("/calls/rebroadcast")
async def api_rebroadcast(call_id: str, request: Request):
    """Reenvía una convocatoria ya creada a los licitantes configurados."""
    res = api_get_call(call_id, request)
    call = res.get("call", {})
    if not call:
        raise HTTPException(404, "call not found")

    base_url = str(request.base_url).rstrip("/")
    push_payload = {**call, "rsa_pub_pem_url": f"{base_url}{call['rsa_pub_pem_url']}"}
    await _notify_licitantes(request, push_payload)
    return {"ok": True}

async def _notify_licitantes(request: Request, call_payload: Dict[str, Any]):
    """POST {secret, call} a /api/calls/sync de cada licitante."""
    urls = getattr(request.app.state, "licitante_callbacks", []) or []
    secret = getattr(request.app.state, "licitante_secret", "")
    if not urls or not secret:
        return
    data = {"secret": secret, "call": call_payload}
    async with httpx.AsyncClient(timeout=10) as client:
        for base in urls:
            url = f"{base.rstrip('/')}/api/calls/sync"
            try:
                r = await client.post(url, json=data)
                r.raise_for_status()
            except Exception as e:
                logging.warning("Notify %s failed: %s", url, e)
