import json
import logging
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from db.migrations import init_db
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

APP_VERSION = "0.1.0"
app = FastAPI(title="抖音 AI 客服", version=APP_VERSION)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "version": APP_VERSION}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({"type": "connected", "message": "AI 客服已就绪"}))
    logger.info("WebSocket client connected")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
            except json.JSONDecodeError:
                logger.warning("Invalid JSON received: %s", data[:100])
                continue

            if msg.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
                continue

            # Echo mode for Phase 1 (will be replaced in Phase 2)
            await websocket.send_text(
                json.dumps({
                    "type": "ai_reply",
                    "convo_id": msg.get("convo_id", ""),
                    "content": f"收到消息: {msg.get('content', '')}",
                    "intent": "general",
                    "sentiment": "中性",
                })
            )
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")


@app.on_event("startup")
async def startup():
    init_db()
    print(f"Database initialized at {Config.DATABASE_PATH}")


if __name__ == "__main__":
    uvicorn.run(app, host=Config.HOST, port=Config.API_PORT)
