from __future__ import annotations
import os
import cv2
import uuid
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime
from app.models.safety_event import SafetyEvent
from app.schemas.event import SafetyEventCreate, EventFilter
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class EventService:
    async def create_event(self, db: AsyncSession, event_data: SafetyEventCreate, snapshot_frame: np.ndarray | None) -> SafetyEvent:
        snapshot_path = None
        
        if snapshot_frame is not None:
            filename = f"event_{uuid.uuid4().hex}.jpg"
            filepath = os.path.join(settings.SNAPSHOT_DIR, filename)
            try:
                cv2.imwrite(filepath, snapshot_frame)
                snapshot_path = f"/snapshots/{filename}"
            except Exception as e:
                logger.error(f"Failed to save snapshot: {e}")
                
        event_dict = event_data.model_dump()
        if snapshot_path is not None:
            event_dict["snapshot_path"] = snapshot_path
        db_event = SafetyEvent(**event_dict)
        
        db.add(db_event)
        await db.commit()
        await db.refresh(db_event)
        return db_event

    async def get_events(self, db: AsyncSession, filters: EventFilter, skip: int = 0, limit: int = 100) -> list[SafetyEvent]:
        query = select(SafetyEvent)
        
        if filters.type:
            query = query.filter(SafetyEvent.event_type == filters.type)
        if filters.severity:
            query = query.filter(SafetyEvent.severity == filters.severity)
        if filters.status:
            query = query.filter(SafetyEvent.status == filters.status)
        if filters.date_from:
            query = query.filter(SafetyEvent.timestamp >= filters.date_from)
        if filters.date_to:
            query = query.filter(SafetyEvent.timestamp <= filters.date_to)
            
        query = query.order_by(desc(SafetyEvent.timestamp)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_event(self, db: AsyncSession, event_id: int) -> SafetyEvent | None:
        query = select(SafetyEvent).where(SafetyEvent.id == event_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update_event_status(self, db: AsyncSession, event_id: int, status: str) -> SafetyEvent | None:
        event = await self.get_event(db, event_id)
        if event:
            event.status = status
            if status == "resolved":
                event.resolved_at = datetime.utcnow()
            await db.commit()
            await db.refresh(event)
        return event

    async def get_event_stats(self, db: AsyncSession) -> dict:
        # Simplified stats for now
        result = await db.execute(select(SafetyEvent))
        events = result.scalars().all()
        
        stats = {
            "total": len(events),
            "by_type": {},
            "by_severity": {}
        }
        
        for e in events:
            stats["by_type"][e.event_type] = stats["by_type"].get(e.event_type, 0) + 1
            stats["by_severity"][e.severity] = stats["by_severity"].get(e.severity, 0) + 1
            
        return stats
