from __future__ import annotations
import time
from typing import List, Dict, Any
from app.schemas.detection import DetectionResult, ObstacleWarning

class DetectionTracker:
    def __init__(self, persistence_threshold: int, cooldown_seconds: float):
        self.persistence_threshold = persistence_threshold
        self.cooldown_seconds = cooldown_seconds
        
        # Maps an approximate center coordinate + class to tracking info
        # Key: "class_x_y", Value: {"frames": int, "last_seen": float, "id": str}
        self._obstacle_tracks: Dict[str, Dict[str, Any]] = {}
        
        # Maps event_key to timestamp of last event generated
        self._event_cooldowns: Dict[str, float] = {}

    def _get_track_key(self, object_class: str, bbox: List[float]) -> str:
        # Simple spatial grouping - round center coordinates to grid
        center_x = (bbox[0] + bbox[2]) / 2.0
        center_y = (bbox[1] + bbox[3]) / 2.0
        grid_x = int(center_x / 50) * 50
        grid_y = int(center_y / 50) * 50
        return f"{object_class}_{grid_x}_{grid_y}"

    def get_persistent_obstacles(self, obstacles: List[ObstacleWarning]) -> List[ObstacleWarning]:
        current_time = time.time()
        persistent = []
        
        # Track new detections
        current_keys = set()
        
        for obs in obstacles:
            key = self._get_track_key(obs.object_class, obs.bbox)
            current_keys.add(key)
            
            if key not in self._obstacle_tracks:
                self._obstacle_tracks[key] = {"frames": 1, "last_seen": current_time}
            else:
                self._obstacle_tracks[key]["frames"] += 1
                self._obstacle_tracks[key]["last_seen"] = current_time
                
            frames = self._obstacle_tracks[key]["frames"]
            obs.frames_persisted = frames
            
            if frames >= self.persistence_threshold:
                persistent.append(obs)
                
        # Cleanup tracks not seen in this frame? Usually better to do it periodically
        # but we can age them out in cleanup_stale
        return persistent

    def should_create_event(self, event_key: str) -> bool:
        current_time = time.time()
        last_event_time = self._event_cooldowns.get(event_key, 0)
        
        if current_time - last_event_time > self.cooldown_seconds:
            self._event_cooldowns[event_key] = current_time
            return True
        return False

    def cleanup_stale(self, max_age_seconds: float = 10.0) -> None:
        current_time = time.time()
        
        # Cleanup obstacles
        stale_tracks = [k for k, v in self._obstacle_tracks.items() if current_time - v["last_seen"] > max_age_seconds]
        for k in stale_tracks:
            del self._obstacle_tracks[k]
            
        # Cleanup cooldowns
        stale_cooldowns = [k for k, t in self._event_cooldowns.items() if current_time - t > self.cooldown_seconds * 2]
        for k in stale_cooldowns:
            del self._event_cooldowns[k]
