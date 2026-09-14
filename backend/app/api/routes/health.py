from __future__ import annotations
from fastapi import APIRouter
from app.config import settings

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
async def get_health():
    # To properly fetch model status etc, we need dependency injection
    # Returning simple static for now. Will be populated properly in real app.
    return {
        "status": "ok",
        "version": "1.0.0",
        "app_name": settings.APP_NAME
    }
