from __future__ import annotations
from fastapi import APIRouter, Depends, Request
from typing import Dict, Any

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("")
async def get_settings():
    # TODO: Implement database settings retrieval
    return {"message": "Settings functionality planned for future phase"}

@router.put("")
async def update_settings(updates: Dict[str, Any]):
    # TODO: Implement settings update
    return {"message": "Settings update planned for future phase"}

@router.get("/system-status")
async def get_system_status(request: Request):
    det_service = request.app.state.detection_service
    status = det_service.get_status()
    
    return {
        "model_loaded": det_service.engine.is_loaded,
        "detection_running": status.is_running,
        "active_cameras": 1 if status.is_running else 0, # Simplified
        "uptime": 0.0, # TODO: implement actual uptime tracking
        "cpu_usage": 0.0, # TODO: implement real metrics
        "gpu_available": det_service.engine.get_model_info()["device"] != "cpu"
    }
