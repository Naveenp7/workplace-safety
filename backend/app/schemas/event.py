from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Optional, Any, List, Dict
from datetime import datetime

class SafetyEventBase(BaseModel):
    event_type: str
    severity: str
    camera_id: Optional[int] = None
    confidence: float
    object_class: str
    bbox: Optional[List[float]] = None
    zone_id: Optional[int] = None
    zone_name: Optional[str] = None
    status: Optional[str] = "active"
    snapshot_path: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class SafetyEventCreate(SafetyEventBase):
    pass

class SafetyEventResponse(SafetyEventBase):
    id: int
    timestamp: datetime
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class SafetyEventListResponse(BaseModel):
    items: List[SafetyEventResponse]
    total: int

class EventFilter(BaseModel):
    type: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
