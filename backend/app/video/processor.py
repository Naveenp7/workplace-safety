from __future__ import annotations
import cv2
import numpy as np
import asyncio
import logging
from typing import Tuple, Dict, Any, Union

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self, source: Union[str, int], fps_limit: int = 30, frame_skip: int = 0):
        self.source = source
        self.fps_limit = fps_limit
        self.frame_skip = frame_skip
        self._cap = None
        self._running = False
        self._frame_count = 0
        self._info = {}

    async def start(self) -> None:
        logger.info(f"Starting video processor for source: {self.source}")
        
        # Execute blocking cv2.VideoCapture in a thread to not block event loop
        loop = asyncio.get_running_loop()
        self._cap = await loop.run_in_executor(None, self._init_capture)
        
        if not self._cap.isOpened():
            raise RuntimeError(f"Failed to open video source: {self.source}")
            
        self._running = True
        
        # Read info
        self._info = {
            "width": int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": float(self._cap.get(cv2.CAP_PROP_FPS)),
            "total_frames": int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        }

    def _init_capture(self) -> cv2.VideoCapture:
        # source can be string (file/rtsp) or int (webcam)
        src = int(self.source) if (isinstance(self.source, str) and self.source.isdigit()) else self.source
        if isinstance(src, int):
            cap = None
            try:
                cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)
                if not cap.isOpened():
                    cap = None
            except Exception:
                cap = None
            if cap is None:
                cap = cv2.VideoCapture(src)

            if cap.isOpened():
                # Crucial for low latency on Windows: discard queued buffered frames
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                # Standardize resolution to 640x480 for fast capture and minimal USB bus overhead
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            return cap
        return cv2.VideoCapture(self.source)

    async def stop(self) -> None:
        self._running = False
        if self._cap:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._cap.release)
            self._cap = None
        logger.info("Video processor stopped")

    def read_frame(self) -> Tuple[bool, np.ndarray | None]:
        if not self._running or not self._cap:
            return False, None
            
        ret, frame = self._cap.read()
        self._frame_count += 1
        
        # Handle frame skip
        if self.frame_skip > 0 and self._frame_count % (self.frame_skip + 1) != 0:
            return self.read_frame() # Recursive read to skip
            
        return ret, frame

    def get_info(self) -> Dict[str, Any]:
        return self._info

    @property
    def is_running(self) -> bool:
        return self._running
