from __future__ import annotations
import asyncio
import time
import logging
from datetime import datetime, timezone
from typing import List, Optional

from app.detection.engine import DetectionEngine
from app.detection.ppe_analyzer import PPEAnalyzer
from app.detection.obstacle_analyzer import ObstacleAnalyzer
from app.detection.tracker import DetectionTracker
from app.video.processor import VideoProcessor
from app.video.utils import encode_frame_to_base64, draw_detections
from app.schemas.detection import DetectionStatus, DetectionFrame

logger = logging.getLogger(__name__)

class DetectionService:
    def __init__(self, engine: DetectionEngine, settings):
        self.engine = engine
        self.settings = settings
        self.processor: Optional[VideoProcessor] = None
        self.task: Optional[asyncio.Task] = None
        
        self.ppe_analyzer = PPEAnalyzer(self.settings.PPE_CONFIDENCE_THRESHOLD)
        self.obstacle_analyzer = ObstacleAnalyzer(self.settings.OBSTACLE_ZONE_OVERLAP_THRESHOLD)
        self.tracker = DetectionTracker(
            persistence_threshold=self.settings.OBSTACLE_PERSISTENCE_FRAMES,
            cooldown_seconds=self.settings.EVENT_COOLDOWN_SECONDS
        )
        
        self._status = DetectionStatus(
            is_running=False,
            fps=0.0,
            latency_ms=0.0,
            total_frames=0
        )
        
        self._zones = []
        self._camera_id = None
        
        # Dependencies injected later
        self.event_service = None
        self.ws_manager = None
        self.db_session_maker = None

    def inject_dependencies(self, event_service, ws_manager, db_session_maker):
        self.event_service = event_service
        self.ws_manager = ws_manager
        self.db_session_maker = db_session_maker

    async def start_detection(self, source: str | int, camera_id: int | None, zones: List) -> None:
        if self.processor and self.processor.is_running:
            await self.stop_detection()
            
        self._camera_id = camera_id
        self._zones = zones
        
        self.processor = VideoProcessor(
            source=source,
            fps_limit=self.settings.VIDEO_FPS_LIMIT,
            frame_skip=self.settings.FRAME_SKIP
        )
        
        await self.processor.start()
        
        self._status.is_running = True
        self._status.source_type = "file" if isinstance(source, str) else "webcam"
        self._status.source_uri = str(source)
        self._status.start_time = datetime.now(timezone.utc)
        self._status.total_frames = 0
        
        self.task = asyncio.create_task(self._detection_loop())
        logger.info(f"Started detection for camera {camera_id}")

    async def stop_detection(self) -> None:
        if self.processor:
            await self.processor.stop()
            
        self._status.is_running = False
        
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None
            
        logger.info("Stopped detection")

    def get_status(self) -> DetectionStatus:
        return self._status

    async def _detection_loop(self) -> None:
        loop_start = time.perf_counter()
        frames_processed = 0
        
        try:
            while self._status.is_running and self.processor:
                frame_start = time.perf_counter()
                
                # Yield to event loop
                await asyncio.sleep(0.001)
                
                ret, frame = self.processor.read_frame()
                if not ret:
                    logger.info("End of video stream reached")
                    break
                    
                # Detect
                detections, inference_time = self.engine.detect(frame)
                
                # Analyze PPE
                ppe_statuses = self.ppe_analyzer.analyze(detections, frame.shape)
                
                # Analyze Obstacles
                raw_warnings = self.obstacle_analyzer.analyze(detections, self._zones, frame.shape)
                
                # Track and Filter
                persistent_warnings = self.tracker.get_persistent_obstacles(raw_warnings)
                self.tracker.cleanup_stale()
                
                # Event Generation (async)
                if self.event_service and self.db_session_maker:
                    asyncio.create_task(self._generate_events(ppe_statuses, persistent_warnings, frame))
                
                # Annotate Frame
                annotated_frame = draw_detections(frame, detections, ppe_statuses, persistent_warnings, self._zones)
                
                # Encode and Broadcast
                if self.ws_manager and self.ws_manager.active_connections_count > 0:
                    b64_frame = encode_frame_to_base64(annotated_frame, self.settings.WS_FRAME_QUALITY)
                    
                    frame_data = DetectionFrame(
                        frame_base64=b64_frame,
                        detections=detections,
                        ppe_statuses=ppe_statuses,
                        obstacle_warnings=persistent_warnings,
                        fps=self._status.fps,
                        latency_ms=inference_time,
                        worker_count=len(ppe_statuses),
                        timestamp=datetime.now(timezone.utc)
                    )
                    await self.ws_manager.broadcast_frame(frame_data)
                
                # Stats update
                self._status.total_frames += 1
                frames_processed += 1
                
                elapsed = time.perf_counter() - loop_start
                if elapsed > 1.0:
                    self._status.fps = frames_processed / elapsed
                    loop_start = time.perf_counter()
                    frames_processed = 0
                    
                self._status.latency_ms = inference_time
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in detection loop: {e}", exc_info=True)
        finally:
            await self.stop_detection()

    async def _generate_events(self, ppe_statuses, obstacle_warnings, frame):
        from app.schemas.event import SafetyEventCreate
        
        try:
            async with self.db_session_maker() as db:
                # Check PPE Violations (both missing, helmet missing, or vest missing)
                for ppe in ppe_statuses:
                    if ppe.compliance_status in ('violation', 'helmet_missing', 'vest_missing'):
                        event_key = f"ppe_violation_{self._camera_id}_{ppe.worker_id}"
                        if self.tracker.should_create_event(event_key):
                            missing_items = [k for k, v in {"helmet": not ppe.has_helmet, "vest": not ppe.has_vest}.items() if v]
                            severity = "high" if not ppe.has_helmet else "medium"
                            event = SafetyEventCreate(
                                event_type="ppe_violation",
                                severity=severity,
                                camera_id=self._camera_id,
                                confidence=1.0,
                                object_class="person",
                                bbox=ppe.bbox,
                                details={"missing": missing_items}
                            )
                            await self.event_service.create_event(db, event, frame)
                            
                # Check Obstacles
                for obs in obstacle_warnings:
                    event_key = f"obstacle_{self._camera_id}_{obs.zone_id}_{obs.object_class}"
                    if self.tracker.should_create_event(event_key):
                        event = SafetyEventCreate(
                            event_type="obstacle_detected",
                            severity="medium",
                            camera_id=self._camera_id,
                            confidence=obs.confidence,
                            object_class=obs.object_class,
                            bbox=obs.bbox,
                            zone_id=obs.zone_id,
                            zone_name=obs.zone_name
                        )
                        await self.event_service.create_event(db, event, frame)
        except Exception as e:
            logger.error(f"Error in _generate_events: {e}", exc_info=True)
