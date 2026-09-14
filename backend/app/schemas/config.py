from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ConfigBase(BaseModel):
    key: str
    value: str
    category: str

class ConfigUpdate(BaseModel):
    value: str

class ConfigResponse(ConfigBase):
    id: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SystemStatus(BaseModel):
    model_loaded: bool
    detection_running: bool
    active_cameras: int
    uptime: float
    cpu_usage: float
    gpu_available: bool
