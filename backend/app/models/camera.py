from __future__ import annotations
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from app.database.session import Base

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    source_type = Column(String(20), nullable=False) # 'file', 'webcam', 'rtsp'
    source_uri = Column(String(500), nullable=False)
    status = Column(String(20), default="inactive") # 'active', 'inactive', 'error'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
