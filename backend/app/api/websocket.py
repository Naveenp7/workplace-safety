from __future__ import annotations
from fastapi import WebSocket
import logging
import asyncio
from app.schemas.detection import DetectionFrame

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self, max_connections: int = 10):
        self.active_connections: list[WebSocket] = []
        self.max_connections = max_connections

    async def connect(self, websocket: WebSocket) -> None:
        if len(self.active_connections) >= self.max_connections:
            await websocket.close(code=1008, reason="Max connections reached")
            return
            
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict) -> None:
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                dead_connections.append(connection)
                
        for connection in dead_connections:
            self.disconnect(connection)

    async def broadcast_frame(self, frame_data: DetectionFrame) -> None:
        # Convert to json compatible dict (handles datetime, etc.)
        data = frame_data.model_dump(mode='json')
        await self.broadcast({"type": "frame", "data": data})

    @property
    def active_connections_count(self) -> int:
        return len(self.active_connections)
