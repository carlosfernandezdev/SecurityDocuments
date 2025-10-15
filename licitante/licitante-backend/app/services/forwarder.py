from pathlib import Path
import httpx, zipfile, io, json
from fastapi import HTTPException
from ..config import settings
from ..storage import timestamp_slug, save_json

# === Enriquecedor de meta ===
def _enrich_meta_bytes(meta_bytes: bytes) -> bytes:
    from ..storage import resolve_notify_info

    try:
        meta = json.loads(meta_bytes.decode("utf-8"))
    except Exception:
        meta = {"_raw_meta": meta_bytes.decode("utf-8", errors="ignore")}

    bidder_identifier, group_id, notify_accounts = resolve_notify_info()

    # Normaliza identificador principal
    if bidder_identifier and not meta.get("bidder_identifier"):
        meta["bidder_identifier"] = bidder_identifier

    if group_id and not meta.get("notify_group_id"):
        meta["notify_group_id"] = group_id

    if notify_accounts and not meta.get("notify_accounts"):
        meta["notify_accounts"] = notify_accounts

    # Callback selection con bidder en la URL esperada por notifications.py
    # Por ejemplo: http://127.0.0.1:8002/licitante/{bidder_id}/api/notifications/selection
    meta.setdefault("callbacks", {})
    sel = (meta["callbacks"].get("selection") or {})
    meta["callbacks"]["selection"] = sel

    base = getattr(settings, "LICITANTE_BASE", "http://127.0.0.1:8002/licitante").rstrip("/")
    if bidder_identifier:
        sel["url"] = f"{base}/{bidder_identifier}/api/notifications/selection"
    else:
        # Fallback genérico (por si no hay active en accounts.json)
        sel["url"] = getattr(settings, "CALLBACK_SELECTION_URL", f"{base}/unknown/api/notifications/selection")

    sel["auth"] = {
        "scheme": getattr(settings, "CALLBACK_AUTH_SCHEME", "basic"),
        "username": getattr(settings, "CALLBACK_AUTH_USERNAME", bidder_identifier or ""),
        "token_or_password": getattr(settings, "CALLBACK_AUTH_PASSWORD", ""),
    }

    return json.dumps(meta, ensure_ascii=False).encode("utf-8")


async def forward_submission(meta_b: bytes=None, payload_b: bytes=None, wrapped_b: bytes=None, nonce_b: bytes=None, tag_b: bytes=None, sealed_zip_b: bytes=None):
    """
    Acepta:
      - parts sueltas (meta/payload/wrapped_key/nonce/tag)
      - o sealed_zip_b con esos 5 archivos adentro.
    Enriquecerá meta.json, guardará copia local y reenviará al Convocante.
    """
    # 1) Si viene sealed.zip, extraer partes
    if sealed_zip_b and not (meta_b and payload_b and wrapped_b and nonce_b and tag_b):
        try:
            with zipfile.ZipFile(io.BytesIO(sealed_zip_b), "r") as z:
                meta_b = z.read("meta.json")
                payload_b = z.read("payload.enc")
                wrapped_b = z.read("wrapped_key.bin")
                nonce_b = z.read("nonce.bin")
                tag_b = z.read("tag.bin")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"sealed.zip inválido: {e}")

    if not all([meta_b, payload_b, wrapped_b, nonce_b, tag_b]):
        raise HTTPException(status_code=400, detail="Faltan partes: meta/payload/wrapped_key/nonce/tag")

    # 2) Enriquecer meta
    meta_b = _enrich_meta_bytes(meta_b)
    meta = json.loads(meta_b)  # bytes JSON válidos

    call_id = meta.get("call_id", "UNKNOWN")

    # bidder robusto: primero el nuevo campo, luego compat "bidder.identifier"
    bidder_identifier = meta.get("bidder_identifier") or (meta.get("bidder") or {}).get("identifier")

    # 3) Persistencia local de la submission (para auditoría)
    ts = timestamp_slug()
    base = settings.SUBMISSIONS_DIR / call_id / ts
    base.mkdir(parents=True, exist_ok=True)
    (base / "meta.json").write_bytes(meta_b)
    (base / "payload.enc").write_bytes(payload_b)
    (base / "wrapped_key.bin").write_bytes(wrapped_b)
    (base / "nonce.bin").write_bytes(nonce_b)
    (base / "tag.bin").write_bytes(tag_b)

    # 4) Reenvío al Convocante
    url = f"{settings.CONVOCANTE_BASE}/internal/receive-proposal"
    params = {"secret": settings.CONVOCANTE_SHARED_SECRET}
    files = {
        "meta": ("meta.json", meta_b, "application/json"),
        "payload": ("payload.enc", payload_b, "application/octet-stream"),
        "wrapped_key": ("wrapped_key.bin", wrapped_b, "application/octet-stream"),
        "nonce": ("nonce.bin", nonce_b, "application/octet-stream"),
        "tag": ("tag.bin", tag_b, "application/octet-stream"),
    }

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(url, params=params, files=files)
        if r.status_code >= 400:
            try:
                detail = r.json()
            except Exception:
                detail = r.text
            raise HTTPException(status_code=502, detail={"convocante_error": detail})

    resp = r.json()

    # 5) Registro local del resultado
    rec = {
        "id": ts,
        "call_id": call_id,
        "bidder_identifier": bidder_identifier,
        "status": resp.get("status", "ok"),
        "created_at": ts,
        "response": resp
    }
    save_json(base / "record.json", rec)
    return rec
