from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Any
import json

class Settings(BaseSettings):
    APP_NAME: str = "Smart Workplace Safety Intelligence Platform"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    DATABASE_URL: str = "sqlite+aiosqlite:///./safety_intelligence.db"
    
    MODEL_PATH: str = "yolov8n.pt"
    MODEL_CONFIDENCE_THRESHOLD: float = 0.5
    MODEL_IOU_THRESHOLD: float = 0.45
    MODEL_INPUT_SIZE: int = 640
    MODEL_DEVICE: str = "auto"
    
    MAX_UPLOAD_SIZE_MB: int = 500
    UPLOAD_DIR: str = "uploads"
    SNAPSHOT_DIR: str = "snapshots"
    VIDEO_FPS_LIMIT: int = 30
    FRAME_SKIP: int = 0
    
    PPE_CONFIDENCE_THRESHOLD: float = 0.28
    OBSTACLE_PERSISTENCE_FRAMES: int = 10
    OBSTACLE_ZONE_OVERLAP_THRESHOLD: float = 0.3
    EVENT_COOLDOWN_SECONDS: float = 30.0
    
    WS_FRAME_QUALITY: int = 70
    WS_MAX_CONNECTIONS: int = 10
    
    # Typed as Any so DotEnvSettingsSource does not attempt strict json.loads
    CORS_ORIGINS: Any = ["*"]
    
    LOG_LEVEL: str = "INFO"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def ensure_async_sqlite(cls, v: str) -> str:
        if isinstance(v, str) and v.startswith("sqlite:///") and not v.startswith("sqlite+aiosqlite:///"):
            return v.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
        return v

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            v_stripped = v.strip()
            if v_stripped.startswith("[") and v_stripped.endswith("]"):
                try:
                    return json.loads(v_stripped)
                except Exception:
                    pass
            if v_stripped == "*":
                return ["*"]
            return [i.strip() for i in v_stripped.split(",") if i.strip()]
        elif isinstance(v, (list, tuple)):
            return [str(i) for i in v]
        return ["*"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
