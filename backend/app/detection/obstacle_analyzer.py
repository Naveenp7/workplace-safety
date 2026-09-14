from __future__ import annotations
from typing import List, Tuple
from shapely.geometry import Polygon, box
from app.schemas.detection import DetectionResult, ObstacleWarning
from app.models.safety_zone import SafetyZone
import logging

logger = logging.getLogger(__name__)

class ObstacleAnalyzer:
    def __init__(self, overlap_threshold: float):
        self.overlap_threshold = overlap_threshold
        # Classes that we shouldn't treat as obstacles
        self.exclude_classes = {'person', 'helmet', 'safety-vest', 'car', 'truck'}

    def analyze(self, detections: List[DetectionResult], zones: List[SafetyZone], frame_shape: Tuple[int, ...]) -> List[ObstacleWarning]:
        warnings = []
        if not zones:
            return warnings
            
        height, width = frame_shape[:2]
        
        # Prepare zone polygons
        zone_polys = []
        for z in zones:
            if not z.is_active:
                continue
            # Scale normalized points to frame size
            points = [(pt['x'] * width, pt['y'] * height) for pt in z.points]
            if len(points) >= 3:
                zone_polys.append((z, Polygon(points)))
                
        if not zone_polys:
            return warnings

        # Filter out persons and PPE
        obstacles = [d for d in detections if d.object_class not in self.exclude_classes]
        
        for obs in obstacles:
            obs_box = box(obs.bbox[0], obs.bbox[1], obs.bbox[2], obs.bbox[3])
            
            for zone, poly in zone_polys:
                if not poly.is_valid:
                    continue
                    
                intersection = obs_box.intersection(poly)
                overlap_ratio = intersection.area / obs_box.area
                
                if overlap_ratio >= self.overlap_threshold:
                    warnings.append(ObstacleWarning(
                        object_class=obs.object_class,
                        confidence=obs.confidence,
                        bbox=obs.bbox,
                        zone_id=zone.id,
                        zone_name=zone.name,
                        frames_persisted=1 # Will be updated by tracker
                    ))
                    break # Only associate with one zone

        return warnings
