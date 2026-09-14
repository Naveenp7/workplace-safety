from __future__ import annotations
import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.video.utils import validate_video_file, get_video_info
from app.database.session import get_db
from app.models.camera import Camera

router = APIRouter(prefix="/video", tags=["Video"])

@router.post("/upload")
async def upload_video(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    if not validate_video_file(file.filename, settings.MAX_UPLOAD_SIZE_MB):
        raise HTTPException(status_code=400, detail="Invalid file type or size")
        
    ext = os.path.splitext(file.filename)[1]
    filename = f"vid_{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Get info
    info = get_video_info(filepath)
    if not info:
        os.remove(filepath)
        raise HTTPException(status_code=400, detail="Failed to read video file")
        
    # Create camera entry
    camera = Camera(
        name=f"Upload: {file.filename}",
        source_type="file",
        source_uri=filepath,
        status="inactive"
    )
    db.add(camera)
    await db.commit()
    await db.refresh(camera)
    
    return {
        "camera_id": camera.id,
        "filename": filename,
        "path": filepath,
        "info": info
    }
