from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.safety_zone import SafetyZone
from app.schemas.zone import ZoneCreate, ZoneUpdate
import logging

logger = logging.getLogger(__name__)

class ZoneService:
    async def create_zone(self, db: AsyncSession, zone_data: ZoneCreate) -> SafetyZone:
        # Convert points (List of Pydantic models) to a list of dicts for JSON column
        points_data = [pt.model_dump() for pt in zone_data.points]
        
        db_zone = SafetyZone(
            name=zone_data.name,
            zone_type=zone_data.zone_type,
            points=points_data,
            camera_id=zone_data.camera_id,
            is_active=zone_data.is_active,
            detection_threshold=zone_data.detection_threshold,
            persistence_frames=zone_data.persistence_frames,
            color=zone_data.color
        )
        
        db.add(db_zone)
        await db.commit()
        await db.refresh(db_zone)
        return db_zone

    async def get_zones(self, db: AsyncSession, camera_id: int | None = None) -> list[SafetyZone]:
        query = select(SafetyZone)
        if camera_id is not None:
            query = query.filter(SafetyZone.camera_id == camera_id)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_zone(self, db: AsyncSession, zone_id: int) -> SafetyZone | None:
        query = select(SafetyZone).where(SafetyZone.id == zone_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update_zone(self, db: AsyncSession, zone_id: int, zone_data: ZoneUpdate) -> SafetyZone | None:
        zone = await self.get_zone(db, zone_id)
        if not zone:
            return None
            
        update_data = zone_data.model_dump(exclude_unset=True)
        if 'points' in update_data:
            update_data['points'] = [pt for pt in update_data['points']] # List of dicts if converted
            
        for key, value in update_data.items():
            setattr(zone, key, value)
            
        await db.commit()
        await db.refresh(zone)
        return zone

    async def delete_zone(self, db: AsyncSession, zone_id: int) -> bool:
        zone = await self.get_zone(db, zone_id)
        if zone:
            await db.delete(zone)
            await db.commit()
            return True
        return False

    async def get_active_zones(self, db: AsyncSession, camera_id: int | None = None) -> list[SafetyZone]:
        query = select(SafetyZone).where(SafetyZone.is_active == True)
        if camera_id is not None:
            query = query.filter(SafetyZone.camera_id == camera_id)
        result = await db.execute(query)
        return list(result.scalars().all())
