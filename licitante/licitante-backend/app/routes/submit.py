from fastapi import APIRouter, UploadFile, File
from ..services.forwarder import forward_submission
router = APIRouter(prefix="/api", tags=["submit"])

@router.post("/submit")
async def submit(
    sealed: UploadFile | None = File(default=None),
    meta: UploadFile | None = File(default=None),
    payload: UploadFile | None = File(default=None),
    wrapped_key: UploadFile | None = File(default=None),
    nonce: UploadFile | None = File(default=None),
    tag: UploadFile | None = File(default=None),
):
    sealed_b = await sealed.read() if sealed else None
    meta_b = await meta.read() if meta else None
    payload_b = await payload.read() if payload else None
    wrapped_b = await wrapped_key.read() if wrapped_key else None
    nonce_b = await nonce.read() if nonce else None
    tag_b = await tag.read() if tag else None
    rec = await forward_submission(meta_b, payload_b, wrapped_b, nonce_b, tag_b, sealed_b)
    return rec