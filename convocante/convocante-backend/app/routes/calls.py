from fastapi import APIRouter, HTTPException
from ..models import CallIn, CallOut
from ..services.calls_service import add_call, list_calls

router = APIRouter(prefix="/api", tags=["calls"])

@router.post("/calls", response_model=dict, status_code=201)
def create_call(c: CallIn):
    try:
        res = add_call(c.call_id)  # << solo pasamos call_id
        return {
            "ok": True,
            "call_id": res["call_id"],
            "key_id": res["key_id"],
            "rsa_pub_endpoint": f"/convocante/api/keys/{res['key_id']}/rsa_pub.pem",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/calls", response_model=list[CallOut])
def get_calls():
    return list_calls()
