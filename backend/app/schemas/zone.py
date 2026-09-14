from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class ZonePoint(BaseModel):
    x: float
    y: float

class ZoneBase(BaseModel):
    name: str
    zone_type: str
    points: List[ZonePoint]
    camera_id: Optional[int] = None
    is_active: Optional[bool] = True
    detection_threshold: Optional[float] = 0.3
    persistence_frames: Optional[int] = 10
    color: str

class ZoneCreate(ZoneBase):
    pass

class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    zone_type: Optional[str] = None
    points: Optional[List[ZonePoint]] = None
    camera_id: Optional[int] = None
    is_active: Optional[bool] = None
    detection_threshold: Optional[float] = None
    persistence_frames: Optional[int] = None
    color: Optional[str] = None

class ZoneResponse(ZoneBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
