from __future__ import annotations
import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging

from app.config import settings
from app.core.logging import setup_logging
from app.database.init_db import init_db
from app.database.session import AsyncSessionLocal
from app.detection.engine import DetectionEngine
from app.detection.face_recognizer import FaceRecognizer
from app.services.detection_service import DetectionService
from app.services.event_service import EventService
from app.api.websocket import ConnectionManager

from app.api.routes import health, video, detection, events, zones, cameras, settings as settings_routes
from app.api.routes import faces as faces_routes

setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Global instances
ws_manager = ConnectionManager(max_connections=settings.WS_MAX_CONNECTIONS)
event_service = EventService()
face_recognizer = FaceRecognizer()
engine = DetectionEngine(
    model_path=settings.MODEL_PATH,
    device=settings.MODEL_DEVICE,
    conf_threshold=settings.MODEL_CONFIDENCE_THRESHOLD,
    iou_threshold=settings.MODEL_IOU_THRESHOLD,
    input_size=settings.MODEL_INPUT_SIZE
)
detection_service = DetectionService(engine, settings)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up application...")
    
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.SNAPSHOT_DIR, exist_ok=True)
    
    await init_db()
    
    # Load YOLO Model
    await engine.load_model()
    
    # Inject dependencies into detection service
    detection_service.inject_dependencies(
        event_service=event_service,
        ws_manager=ws_manager,
        db_session_maker=AsyncSessionLocal,
        face_recognizer=face_recognizer
    )
    
    app.state.detection_service = detection_service
    app.state.face_recognizer = face_recognizer
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await detection_service.stop_detection()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files for snapshots
app.mount("/snapshots", StaticFiles(directory=settings.SNAPSHOT_DIR), name="snapshots")

# Include Routers
api_router = FastAPI() # Can use APIRouter too
app.include_router(health.router, prefix="/api")
app.include_router(video.router, prefix="/api")
app.include_router(detection.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(zones.router, prefix="/api")
app.include_router(cameras.router, prefix="/api")
app.include_router(settings_routes.router, prefix="/api")
app.include_router(faces_routes.router, prefix="/api")

@app.api_route("/predict", methods=["GET", "POST"])
async def predict_fallback():
    return {"status": "ok", "message": "Predict endpoint active", "predictions": []}

@app.websocket("/ws/detection")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # We don't really expect client to send messages, but if they do:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
