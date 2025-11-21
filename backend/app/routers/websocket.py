from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/ws", tags=["realtime"])

active_connections = []

async def broadcast(message: dict):
    stale = []
    for ws in active_connections:
        try:
            await ws.send_json(message)
        except Exception:
            stale.append(ws)
    for s in stale:
        active_connections.remove(s)

@router.websocket("/live")
async def live(ws: WebSocket):
    await ws.accept()
    active_connections.append(ws)
    try:
        await ws.send_json({"event": "welcome", "msg": "connected"})
        while True:
            # 简单回声/保活
            data = await ws.receive_text()
            await ws.send_json({"event": "echo", "data": data})
    except WebSocketDisconnect:
        if ws in active_connections:
            active_connections.remove(ws)
