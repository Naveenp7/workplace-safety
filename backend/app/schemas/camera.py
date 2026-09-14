from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class CameraBase(BaseModel):
    name: str
    source_type: str
    source_uri: str
    status: Optional[str] = "inactive"

class CameraCreate(CameraBase):
    pass

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    source_type: Optional[str] = None
    source_uri: Optional[str] = None
    status: Optional[str] = None

class CameraResponse(CameraBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CameraListResponse(BaseModel):
    items: list[CameraResponse]
    total: int
