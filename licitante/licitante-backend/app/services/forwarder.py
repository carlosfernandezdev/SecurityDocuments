from pathlib import Path
import httpx, zipfile, io, json
from fastapi import HTTPException
from ..config import settings
from ..storage import timestamp_slug, save_json

async def forward_submission(meta_b: bytes=None, payload_b: bytes=None, wrapped_b: bytes=None, nonce_b: bytes=None, tag_b: bytes=None, sealed_zip_b: bytes=None):
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

    meta = json.loads(meta_b)
    call_id = meta.get("call_id", "UNKNOWN")
    bidder_identifier = meta.get("bidder", {}).get("identifier")

    ts = timestamp_slug()
    base = settings.SUBMISSIONS_DIR / call_id / ts
    base.mkdir(parents=True, exist_ok=True)
    (base / "meta.json").write_bytes(meta_b)
    (base / "payload.enc").write_bytes(payload_b)
    (base / "wrapped_key.bin").write_bytes(wrapped_b)
    (base / "nonce.bin").write_bytes(nonce_b)
    (base / "tag.bin").write_bytes(tag_b)

    url = f"{settings.CONVOCANTE_BASE}/internal/receive-proposal"
    params = {"secret": settings.CONVOCANTE_SHARED_SECRET}
    files = {
        "meta": ("meta.json", meta_b, "application/json"),
        "payload": ("payload.enc", payload_b, "application/octet-stream"),
        "wrapped_key": ("wrapped_key.bin", wrapped_b, "application/octet-stream"),
        "nonce": ("nonce.bin", nonce_b, "application/octet-stream"),
        "tag": ("tag.bin", tag_b, "application/octet-stream"),
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(url, params=params, files=files, timeout=120)
        if r.status_code >= 400:
            try:
                detail = r.json()
            except Exception:
                detail = r.text
            raise HTTPException(status_code=502, detail={"convocante_error": detail})

    resp = r.json()
    rec = {
        "id": ts,
        "call_id": call_id,
        "bidder_identifier": bidder_identifier,
        "status": resp.get("status", "sent"),
        "created_at": ts,
        "response": resp
    }
    save_json(base / "record.json", rec)
    return rec