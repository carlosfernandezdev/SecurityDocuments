# app/routes/keys.py (reemplaza el archivo)
from fastapi import APIRouter, Response
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from ..config import settings

router = APIRouter(tags=["keys"])

KEYS_DIR = settings.KEYS_DIR
PRIV = KEYS_DIR / "rsa_private.pem"
PUB  = KEYS_DIR / "rsa_public.pem"

def _ensure_keys():
    KEYS_DIR.mkdir(parents=True, exist_ok=True)
    if PRIV.exists() and PUB.exists():
        return
    key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    PRIV.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    PUB.write_bytes(
        key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )

@router.get("/public/keys/{call_id}/{key_id}/rsa_pub.pem")
def get_rsa_pub(call_id: str, key_id: str):
    _ensure_keys()
    pem = PUB.read_bytes()
    return Response(
        content=pem,
        media_type="application/x-pem-file",
        headers={"Content-Disposition": 'attachment; filename="rsa_pub.pem"'}
    )
