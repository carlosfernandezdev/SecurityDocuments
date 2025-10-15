from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from ..config import settings
from ..services.submissions_service import process_submission

router = APIRouter(prefix="/internal", tags=["receive"])

def check_secret(secret: str):
    if secret != settings.SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="forbidden")

@router.post("/receive-proposal")
async def receive_proposal(
    secret: str,
    meta: UploadFile = File(...),
    payload: UploadFile = File(...),
    wrapped_key: UploadFile = File(...),
    nonce: UploadFile = File(...),
    tag: UploadFile = File(...),
):
    check_secret(secret)
    meta_b = await meta.read()
    payload_b = await payload.read()
    wrapped_b = await wrapped_key.read()
    nonce_b = await nonce.read()
    tag_b = await tag.read()
    # basic size guard
    if len(payload_b) > settings.MAX_PAYLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail="payload too large")
    result = process_submission(meta_b, payload_b, wrapped_b, nonce_b, tag_b)
    return result
