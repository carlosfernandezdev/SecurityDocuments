import base64
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Submission, Convocatoria, User, Role
from ..schemas import SubmissionIn, SubmissionOut
from ..auth.router import get_current_user
from .service import decrypt_envelope, verify_optional_signature

router = APIRouter(prefix="/submissions", tags=["submissions"])

@router.post("/{conv_id}", response_model=SubmissionOut)
def subir(conv_id: int, body: SubmissionIn, req: Request, db: Session = Depends(get_db)):
    user = get_current_user(req, db)
    # Permitir que el licitante suba incluso desde este backend si quieren unificar URL:
    if not user or user.role != Role.LICITANTE:
        raise HTTPException(status_code=403, detail="Solo licitantes")
    conv = db.get(Convocatoria, conv_id)
    if not conv: raise HTTPException(status_code=404, detail="Convocatoria no existe")

    import base64
    def b64d(s: str) -> bytes: return base64.b64decode(s)
    wrapped_key = b64d(body.wrapped_key_b64)
    nonce       = b64d(body.nonce_b64)
    tag         = b64d(body.tag_b64)
    ciphertext  = b64d(body.ciphertext_b64)
    signature   = b64d(body.signature_b64) if body.signature_b64 else None

    if not verify_optional_signature(body.signer_pk_hex, ciphertext, signature):
        raise HTTPException(status_code=400, detail="Firma inválida")

    sub = Submission(
        convocatoria_id=conv.id,
        licitante_id=user.id,
        payload_sha256=body.payload_sha256,
        content_zip_sha256=body.content_zip_sha256,
        sealed_zip_sha256=body.sealed_zip_sha256,
        wrapped_key=wrapped_key,
        nonce=nonce,
        tag=tag,
        ciphertext=ciphertext,
        signer_pk_hex=body.signer_pk_hex,
        signature=signature
    )
    db.add(sub); db.commit(); db.refresh(sub)
    return sub

@router.post("/{conv_id}/{sub_id}/decrypt")
def decrypt(conv_id: int, sub_id: int, private_key_pem_b64: str, req: Request, db: Session = Depends(get_db)):
    user = get_current_user(req, db)
    if not user or user.role != Role.CONVOCANTE:
        raise HTTPException(status_code=403, detail="Solo convocantes")

    sub = db.get(Submission, sub_id)
    if not sub or sub.convocatoria_id != conv_id:
        raise HTTPException(status_code=404, detail="Submission no existe")
    private_pem = base64.b64decode(private_key_pem_b64)

    plaintext = decrypt_envelope(private_pem, sub.wrapped_key, sub.nonce, sub.tag, sub.ciphertext)
    return {"plaintext_b64": base64.b64encode(plaintext).decode()}
