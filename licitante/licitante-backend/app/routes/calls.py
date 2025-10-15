from fastapi import APIRouter
from ..services.calls_proxy import fetch_calls_with_pubkeys
router = APIRouter(prefix="/api", tags=["calls"])
@router.get("/calls")
async def list_calls():
    return await fetch_calls_with_pubkeys()