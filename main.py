import json
import logging
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from db.migrations import init_db
from db.models import Conversation, Knowledge, Analytics
from config import Config
from core.message_handler import MessageHandler
from api.knowledge import router as knowledge_router
from api.analytics import router as analytics_router
from api.orders import router as orders_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

APP_VERSION = "0.1.0"
app = FastAPI(title="抖音 AI 客服", version=APP_VERSION)
app.mount("/static", StaticFiles(directory="web/static"), name="static")
app.include_router(knowledge_router)
app.include_router(analytics_router)
app.include_router(orders_router)
templates = Jinja2Templates(directory="web/templates")
handler = MessageHandler()


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "version": APP_VERSION}


@app.get("/admin")
async def admin_dashboard(request: Request):
    from datetime import date
    today = Analytics.get_or_none(Analytics.date == date.today())
    stats = {
        "convo_count": today.convo_count if today else 0,
        "avg_response": today.avg_response if today else 0.0,
        "pos_ratio": today.pos_ratio if today else 0.0,
        "top_questions": json.loads(today.top_questions) if today else [],
    }
    active_count = Conversation.select().where(Conversation.status == "active").count()
    return templates.TemplateResponse("dashboard.html", {
        "request": request, "stats": stats, "active_count": active_count
    })


@app.get("/admin/conversations")
async def admin_conversations(request: Request):
    convos = (Conversation.select().order_by(Conversation.updated_at.desc()).limit(50))
    return templates.TemplateResponse("conversations.html", {
        "request": request, "conversations": convos
    })


@app.get("/admin/knowledge")
async def admin_knowledge(request: Request):
    items = Knowledge.select().order_by(Knowledge.created_at.desc())
    return templates.TemplateResponse("knowledge.html", {
        "request": request, "items": items
    })


@app.get("/admin/settings")
async def admin_settings(request: Request):
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "version": APP_VERSION,
        "primary_model": Config.PRIMARY_MODEL,
        "embedding_model": Config.EMBEDDING_MODEL,
        "db_path": Config.DATABASE_PATH,
        "ds_configured": bool(Config.DEEPSEEK_API_KEY),
        "qwen_configured": bool(Config.QWEN_API_KEY),
        "kimi_configured": bool(Config.KIMI_API_KEY),
    })


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

            result = handler.process(msg)
            await websocket.send_text(
                json.dumps({
                    "type": "ai_reply",
                    "convo_id": result["convo_id"],
                    "content": result["reply"],
                    "intent": result["intent"],
                    "sentiment": result["sentiment"],
                    "handoff": result.get("handoff", False),
                })
            )
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")


@app.on_event("startup")
async def startup():
    init_db()
    logger.info("Database initialized at %s", Config.DATABASE_PATH)


if __name__ == "__main__":
    uvicorn.run(app, host=Config.HOST, port=Config.API_PORT)
