import io, json, zipfile, uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from config import APP_PREFIX, INTERNAL_SECRET
from services.store import call_dir, persist_submission, now_iso
from services.crypto import rsa_oaep_unwrap, aes_gcm_decrypt, ed25519_verify_hex, sha256_bytes

router = APIRouter(prefix=f"{APP_PREFIX}/internal", tags=["internal"])

@router.post("/receive-proposal")
async def receive_proposal(
    secret: str = Query(...),
    meta: UploadFile = File(...),
    payload: UploadFile = File(...),
    wrapped_key: UploadFile = File(...),
    nonce: UploadFile = File(...),
    tag: UploadFile = File(...),
    sealed_base: UploadFile = File(...),
):
    if secret != INTERNAL_SECRET:
        raise HTTPException(403, "forbidden")

    # read pieces
    meta_json = json.loads((await meta.read()).decode("utf-8"))
    payload_bytes = await payload.read()
    wrapped_key_bytes = await wrapped_key.read()
    nonce_bytes = await nonce.read()
    tag_bytes = await tag.read()
    sealed_bytes = await sealed_base.read()

    call_id = meta_json.get("call_id")
    if not call_id:
        raise HTTPException(400, "missing call_id")

    priv_pem = (call_dir(call_id) / "rsa_priv.pem").read_bytes()

    # unwrap
    ok_unwrap = False
    aes_key = b""
    try:
        aes_key = rsa_oaep_unwrap(priv_pem, wrapped_key_bytes)
        ok_unwrap = True
    except Exception as e:
        state = {
            "id": None,
            "call_id": call_id,
            "ok_unwrap": False,
            "ok_decrypt": False,
            "ok_signature": None,
            "payload_sha256_meta": meta_json.get("payload_sha256"),
            "payload_sha256_got": sha256_bytes(payload_bytes),
            "content_files": [],
            "notes": f"unwrap error: {e}",
            "extra": {"meta": meta_json},
        }
        sid = uuid.uuid4().hex[:12]
        persist_submission(call_id, sid, {
            "meta.json": json.dumps(meta_json).encode("utf-8"),
            "payload.enc": payload_bytes,
            "wrapped_key.bin": wrapped_key_bytes,
            "nonce.bin": nonce_bytes,
            "tag.bin": tag_bytes,
            "sealed_base.zip": sealed_bytes,
        }, state)
        raise HTTPException(400, "unwrap failed")

    # decrypt
    ok_decrypt = False
    try:
        _ = aes_gcm_decrypt(aes_key, nonce_bytes, payload_bytes, tag_bytes, aad=None)
        ok_decrypt = True
    except Exception as e:
        state = {
            "id": None,
            "call_id": call_id,
            "ok_unwrap": True,
            "ok_decrypt": False,
            "ok_signature": None,
            "payload_sha256_meta": meta_json.get("payload_sha256"),
            "payload_sha256_got": sha256_bytes(payload_bytes),
            "content_files": [],
            "notes": f"decrypt error: {e}",
            "extra": {"meta": meta_json},
        }
        sid = uuid.uuid4().hex[:12]
        persist_submission(call_id, sid, {
            "meta.json": json.dumps(meta_json).encode("utf-8"),
            "payload.enc": payload_bytes,
            "wrapped_key.bin": wrapped_key_bytes,
            "nonce.bin": nonce_bytes,
            "tag.bin": tag_bytes,
            "sealed_base.zip": sealed_bytes,
        }, state)
        raise HTTPException(400, "decrypt failed")

    # open sealed_base.zip
    content_files = []
    ok_signature = None
    try:
        with zipfile.ZipFile(io.BytesIO(sealed_bytes), "r") as z:
            names = set(z.namelist())
            must = {"content.zip", "manifest.json"}
            if not must.issubset(names):
                raise ValueError(f"sealed_base.zip missing {must - names}")
            manifest = json.loads(z.read("manifest.json").decode("utf-8"))
            content_files.append("manifest.json")

            if "signature.bin" in names:
                signature = z.read("signature.bin")
                content_files.append("signature.bin")
            else:
                signature = None

            content_zip = z.read("content.zip")
            content_files.append("content.zip")

        # verify signature if present
        if signature is not None:
            pub_hex = manifest.get("ed25519_pub_hex")
            message = sha256_bytes(content_zip).encode("utf-8")
            ok_signature = ed25519_verify_hex(pub_hex, message, signature) if pub_hex else None
        else:
            ok_signature = None
    except Exception:
        # treat as decrypt ok but content invalid
        ok_signature = None

    sid = uuid.uuid4().hex[:12]
    state = {
        "id": sid,
        "call_id": call_id,
        "ok_unwrap": ok_unwrap,
        "ok_decrypt": ok_decrypt,
        "ok_signature": ok_signature,
        "payload_sha256_meta": meta_json.get("payload_sha256"),
        "payload_sha256_got": sha256_bytes(payload_bytes),
        "content_files": content_files,
        "notes": None,
        "extra": {"meta": meta_json},
    }
    persist_submission(call_id, sid, {
        "meta.json": json.dumps(meta_json).encode("utf-8"),
        "payload.enc": payload_bytes,
        "wrapped_key.bin": wrapped_key_bytes,
        "nonce.bin": nonce_bytes,
        "tag.bin": tag_bytes,
        "sealed_base.zip": sealed_bytes,
    }, state)

    return {
        "ok": True,
        "submission_id": sid,
        "ok_unwrap": ok_unwrap,
        "ok_decrypt": ok_decrypt,
        "ok_signature": ok_signature,
        "content_files": content_files,
    }
