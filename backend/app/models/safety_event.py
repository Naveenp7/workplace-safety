from __future__ import annotations
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from datetime import datetime, timezone
from app.database.session import Base

class SafetyEvent(Base):
    __tablename__ = "safety_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    confidence = Column(Float, nullable=False)
    object_class = Column(String(50), nullable=False)
    bbox = Column(JSON, nullable=True)
    zone_id = Column(Integer, ForeignKey("safety_zones.id"), nullable=True)
    zone_name = Column(String(100), nullable=True)
    status = Column(String(20), default="active")
    snapshot_path = Column(String(500), nullable=True)
    details = Column(JSON, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
