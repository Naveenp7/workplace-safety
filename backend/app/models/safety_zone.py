from __future__ import annotations
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean
from datetime import datetime, timezone
from app.database.session import Base

class SafetyZone(Base):
    __tablename__ = "safety_zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    zone_type = Column(String(30), nullable=False)
    points = Column(JSON, nullable=False)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    detection_threshold = Column(Float, default=0.3)
    persistence_frames = Column(Integer, default=10)
    color = Column(String(7), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
