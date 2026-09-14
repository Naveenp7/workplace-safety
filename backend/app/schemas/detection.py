from __future__ import annotations
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DetectionResult(BaseModel):
    object_class: str
    confidence: float
    bbox: List[float] # [x1, y1, x2, y2]
    timestamp: datetime

class WorkerPPEStatus(BaseModel):
    worker_id: int
    bbox: List[float]
    has_helmet: bool
    has_vest: bool
    helmet_confidence: float
    vest_confidence: float
    compliance_status: str # 'compliant', 'violation'

class ObstacleWarning(BaseModel):
    object_class: str
    confidence: float
    bbox: List[float]
    zone_id: int
    zone_name: str
    frames_persisted: int

class DetectionFrame(BaseModel):
    frame_base64: str
    detections: List[DetectionResult]
    ppe_statuses: List[WorkerPPEStatus]
    obstacle_warnings: List[ObstacleWarning]
    fps: float
    latency_ms: float
    worker_count: int
    timestamp: datetime

class DetectionStatus(BaseModel):
    is_running: bool
    source_type: Optional[str] = None
    source_uri: Optional[str] = None
    fps: float
    latency_ms: float
    total_frames: int
    start_time: Optional[datetime] = None
