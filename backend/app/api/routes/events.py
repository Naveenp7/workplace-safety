from __future__ import annotations
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from app.database.session import get_db
from app.services.event_service import EventService
from app.schemas.event import SafetyEventListResponse, EventFilter, SafetyEventResponse
from pydantic import BaseModel

router = APIRouter(prefix="/events", tags=["Events"])
event_service = EventService()

class StatusUpdate(BaseModel):
    status: str

@router.get("", response_model=SafetyEventListResponse)
async def list_events(
    type: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    filters = EventFilter(
        type=type, severity=severity, status=status,
        date_from=date_from, date_to=date_to
    )
    events = await event_service.get_events(db, filters, skip, limit)
    # Getting total count would require another query, returning length of fetched list for simplicity
    return SafetyEventListResponse(items=events, total=len(events))

@router.get("/stats/summary")
async def get_event_stats(db: AsyncSession = Depends(get_db)):
    return await event_service.get_event_stats(db)

@router.get("/{id}", response_model=SafetyEventResponse)
async def get_event(id: int, db: AsyncSession = Depends(get_db)):
    event = await event_service.get_event(db, id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.patch("/{id}/status", response_model=SafetyEventResponse)
async def update_event_status(id: int, status_update: StatusUpdate, db: AsyncSession = Depends(get_db)):
    event = await event_service.update_event_status(db, id, status_update.status)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
