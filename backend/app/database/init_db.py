from __future__ import annotations
from app.database.session import engine, Base
import app.models  # Import all models so they register with Base.metadata

async def init_db() -> None:
    """Create all tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
