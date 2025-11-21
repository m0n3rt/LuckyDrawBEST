from fastapi import FastAPI
from .routers import participants, draw, websocket, frontend

app = FastAPI(title="LuckyDraw Backend", version="0.1.0")

app.include_router(participants.router)
app.include_router(draw.router)
app.include_router(websocket.router)
app.include_router(frontend.router)

@app.get("/health")
def health():
    return {"status": "ok"}
