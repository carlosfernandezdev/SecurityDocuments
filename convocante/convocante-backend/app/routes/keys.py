from fastapi import APIRouter, HTTPException, Response
from ..services.calls_service import get_pubkey_path

router = APIRouter(prefix="/api", tags=["keys"])

@router.get("/keys/{key_id}/rsa_pub.pem")
def get_rsa_pub(key_id: str):
    path = get_pubkey_path(key_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail="public key not found")
    pem = path.read_text(encoding="utf-8")
    return Response(content=pem, media_type="application/x-pem-file")
