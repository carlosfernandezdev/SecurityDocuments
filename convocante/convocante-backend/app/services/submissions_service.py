from pathlib import Path
from fastapi import HTTPException
from ..config import settings
from ..crypto_utils import sha256_bytes, rsa_decrypt_oaep_sha256, aes_gcm_decrypt, ed25519_verify
from ..storage import save_bytes, save_json, timestamp_slug
import json, zipfile, io


def process_submission(meta_bytes: bytes, payload_bytes: bytes, wrapped_bytes: bytes, nonce_bytes: bytes, tag_bytes: bytes):
    # --- 1) Leer meta y campos mínimos ---
    try:
        meta = json.loads(meta_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"meta.json inválido: {e}")

    call_id = meta.get("call_id")
    key_id = meta.get("key_id")
    if not call_id or not key_id:
        raise HTTPException(status_code=400, detail="meta.json debe incluir call_id y key_id")

    bidder_pub_hex = meta.get("bidder", {}).get("ed25519_pk_hex")
    if not bidder_pub_hex:
        raise HTTPException(status_code=400, detail="meta.bidder.ed25519_pk_hex faltante")

    # --- 2) Rutas de almacenamiento ---
    ts = timestamp_slug()
    inbox_dir = settings.INBOX_DIR / call_id / ts
    processed_dir = settings.PROCESSED_DIR / call_id / ts
    inbox_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Guardar entrada tal cual
    save_bytes(inbox_dir / "meta.json", meta_bytes)
    save_bytes(inbox_dir / "payload.enc", payload_bytes)
    save_bytes(inbox_dir / "wrapped_key.bin", wrapped_bytes)
    save_bytes(inbox_dir / "nonce.bin", nonce_bytes)
    save_bytes(inbox_dir / "tag.bin", tag_bytes)

    # --- 3) Descifrar K (RSA-OAEP-SHA256) ---
    # Se espera el RSA *privado* del convocante en keys/<key_id>/rsa_priv.pem
    key_dir = settings.KEYS_DIR / key_id
    priv_pem = key_dir / "rsa_priv.pem"
    if not priv_pem.exists():
        raise HTTPException(status_code=400, detail="RSA privada no encontrada para key_id")

    K = rsa_decrypt_oaep_sha256(priv_pem.read_bytes(), wrapped_bytes)

    # --- 4) Descifrar sealed_base (AES-GCM) ---
    sealed_base = aes_gcm_decrypt(K, nonce_bytes, tag_bytes, payload_bytes)
    save_bytes(processed_dir / "sealed_base.zip", sealed_base)

    # --- 5) Extraer content.zip y signature.bin del sealed_base ---
    try:
        with zipfile.ZipFile(io.BytesIO(sealed_base), "r") as z:
            z.extractall(processed_dir)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"sealed_base.zip corrupto: {e}")

    content_zip_b = (processed_dir / "content.zip").read_bytes()
    signature_b = (processed_dir / "signature.bin").read_bytes()

    # --- 6) Verificar firma Ed25519 de content.zip ---
    if not ed25519_verify(bidder_pub_hex, content_zip_b, signature_b):
        raise HTTPException(status_code=400, detail="Firma Ed25519 inválida para content.zip")

    # (opcional) comparar hash si viene en meta
    cz_hash = sha256_bytes(content_zip_b)
    claimed = meta.get("content_zip_sha256")
    # No forzamos, solo informativo: si quieres forzar, compara y lanza 400 si no coincide.

    # --- 7) EXTRAER contenido final a processed/.../content/ ---
    content_dir = processed_dir / "content"
    content_dir.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(io.BytesIO(content_zip_b), "r") as cz:
            cz.extractall(content_dir)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"content.zip corrupto: {e}")

    # --- 8) Guardar result.json y retornar ---
    result = {
        "status": "ok",
        "call_id": call_id,
        "key_id": key_id,
        "submission_id": ts,
        "content_zip_sha256": cz_hash,
        "files_extracted": True,
    }
    save_json(processed_dir / "result.json", result)
    return result
