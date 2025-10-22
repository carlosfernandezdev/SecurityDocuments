import base64
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Submission, Convocatoria, User, Role
from ..schemas import SubmissionIn, SubmissionOut
from ..auth.router import get_current_user
from .service import verify_optional_signature

router = APIRouter(prefix="/submissions", tags=["submissions"])

def b64d(s: str) -> bytes: return base64.b64decode(s)

@router.post("/{conv_id}", response_model=SubmissionOut)
def subir(conv_id: int, body: SubmissionIn, req: Request, db: Session = Depends(get_db)):
    user = get_current_user(req, db)
    if not user or user.role != Role.LICITANTE:
        raise HTTPException(status_code=403, detail="Solo licitantes")
    conv = db.get(Convocatoria, conv_id)
    if not conv: raise HTTPException(status_code=404, detail="Convocatoria no existe")

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
