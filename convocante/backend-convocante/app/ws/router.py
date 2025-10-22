from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .hub import hub

router = APIRouter()

@router.websocket("/ws/licitante")
async def licitante_ws(ws: WebSocket):
    await ws.accept()
    await hub.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        hub.disconnect(ws)
