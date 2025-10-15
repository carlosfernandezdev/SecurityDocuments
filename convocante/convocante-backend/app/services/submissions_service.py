from pathlib import Path
from fastapi import HTTPException
from ..config import settings
from ..crypto_utils import sha256_bytes, rsa_decrypt_oaep_sha256, aes_gcm_decrypt, ed25519_verify
from ..storage import save_bytes, save_json, timestamp_slug
import json, zipfile, io

def process_submission(meta_bytes: bytes, payload_bytes: bytes, wrapped_bytes: bytes, nonce_bytes: bytes, tag_bytes: bytes):
    meta = json.loads(meta_bytes)
    call_id = meta["call_id"]; key_id = meta["key_id"]
    bidder_pub_hex = meta["bidder"]["ed25519_pk_hex"]

    # Validate declared payload hash if present
    if "payload_sha256" in meta:
        if sha256_bytes(payload_bytes) != meta["payload_sha256"]:
            raise HTTPException(status_code=400, detail="payload_sha256 mismatch")

    # Paths
    ts = timestamp_slug()
    base_dir = settings.INBOX_DIR / call_id / ts
    save_bytes(base_dir / "meta.json", meta_bytes)
    save_bytes(base_dir / "payload.enc", payload_bytes)
    save_bytes(base_dir / "wrapped_key.bin", wrapped_bytes)
    save_bytes(base_dir / "nonce.bin", nonce_bytes)
    save_bytes(base_dir / "tag.bin", tag_bytes)

    # Load RSA private
    from .calls_service import get_privkey_path
    priv_path = get_privkey_path(key_id)
    if not priv_path.exists():
        raise HTTPException(status_code=400, detail=f"private key for key_id '{key_id}' not found")
    priv_bytes = priv_path.read_bytes()

    # Unwrap K and decrypt sealed_base.zip
    K = rsa_decrypt_oaep_sha256(priv_bytes, wrapped_bytes)
    sealed_base = aes_gcm_decrypt(K, nonce_bytes, tag_bytes, payload_bytes)

    # Save sealed base
    processed_dir = settings.PROCESSED_DIR / call_id / ts
    save_bytes(processed_dir / "sealed_base.zip", sealed_base)

    # Extract and verify signature
    with zipfile.ZipFile(io.BytesIO(sealed_base), "r") as z:
        z.extractall(processed_dir)
    content_zip = (processed_dir / "content.zip").read_bytes()
    signature = (processed_dir / "signature.bin").read_bytes()

    if not ed25519_verify(bidder_pub_hex, content_zip, signature):
        raise HTTPException(status_code=400, detail="Ed25519 signature invalid")

    # Optionally check content_zip_sha256
    cz_hash = sha256_bytes(content_zip)
    result = {
        "status": "ok",
        "call_id": call_id,
        "key_id": key_id,
        "content_zip_sha256": cz_hash
    }
    save_json(processed_dir / "result.json", result)
    return result
