from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.database.session import get_db
from app.services.zone_service import ZoneService
from app.schemas.zone import ZoneCreate, ZoneUpdate, ZoneResponse

router = APIRouter(prefix="/zones", tags=["Zones"])
zone_service = ZoneService()

@router.get("", response_model=List[ZoneResponse])
async def list_zones(camera_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    return await zone_service.get_zones(db, camera_id)

@router.post("", response_model=ZoneResponse)
async def create_zone(zone: ZoneCreate, db: AsyncSession = Depends(get_db)):
    return await zone_service.create_zone(db, zone)

@router.get("/{id}", response_model=ZoneResponse)
async def get_zone(id: int, db: AsyncSession = Depends(get_db)):
    zone = await zone_service.get_zone(db, id)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return zone

@router.put("/{id}", response_model=ZoneResponse)
async def update_zone(id: int, zone_update: ZoneUpdate, db: AsyncSession = Depends(get_db)):
    zone = await zone_service.update_zone(db, id, zone_update)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return zone

@router.delete("/{id}")
async def delete_zone(id: int, db: AsyncSession = Depends(get_db)):
    success = await zone_service.delete_zone(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Zone not found")
    return {"message": "Zone deleted successfully"}
