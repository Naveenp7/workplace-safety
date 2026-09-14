from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database.session import get_db
from app.services.zone_service import ZoneService

router = APIRouter(prefix="/detection", tags=["Detection"])

class StartRequest(BaseModel):
    source_type: str
    source_uri: str
    camera_id: Optional[int] = None

@router.post("/start")
async def start_detection(req: StartRequest, request: Request, db: AsyncSession = Depends(get_db)):
    det_service = request.app.state.detection_service
    zone_service = ZoneService()
    
    # Get active zones for this camera
    zones = await zone_service.get_active_zones(db, req.camera_id)
    
    source = int(req.source_uri) if req.source_uri.isdigit() else req.source_uri
    await det_service.start_detection(source, req.camera_id, zones)
    
    return {"message": "Detection started"}

@router.post("/stop")
async def stop_detection(request: Request):
    det_service = request.app.state.detection_service
    await det_service.stop_detection()
    return {"message": "Detection stopped"}

@router.get("/status")
async def get_status(request: Request):
    det_service = request.app.state.detection_service
    return det_service.get_status()

@router.get("/model-info")
async def get_model_info(request: Request):
    det_service = request.app.state.detection_service
    return det_service.engine.get_model_info()
