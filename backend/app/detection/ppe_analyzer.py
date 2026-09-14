from __future__ import annotations
from typing import List, Tuple
from app.schemas.detection import DetectionResult, WorkerPPEStatus
import logging

logger = logging.getLogger(__name__)

class PPEAnalyzer:
    def __init__(self, confidence_threshold: float = 0.28):
        self.confidence_threshold = confidence_threshold

    def _is_inside_or_near(self, item_box: List[float], person_box: List[float], is_helmet: bool = False) -> bool:
        """
        Check if safety item (helmet/vest) belongs to the person based on spatial containment.
        Uses item-relative intersection area and center-point inclusion.
        """
        ix1, iy1, ix2, iy2 = item_box
        px1, py1, px2, py2 = person_box

        item_w = max(0.0, ix2 - ix1)
        item_h = max(0.0, iy2 - iy1)
        item_area = item_w * item_h
        if item_area <= 0:
            return False

        # Center of the item
        item_cx = (ix1 + ix2) / 2.0
        item_cy = (iy1 + iy2) / 2.0

        person_width = max(1.0, px2 - px1)
        person_height = max(1.0, py2 - py1)
        
        # Horizontal tolerance (helmets or persons at slight angle)
        tolerant_px1 = px1 - (0.15 * person_width)
        tolerant_px2 = px2 + (0.15 * person_width)
        
        # Person bounds with tolerance for helmets that sit slightly above bounding box
        tolerant_py1 = py1 - (0.25 * person_height if is_helmet else 0.0)

        # 1. Center inclusion check
        if (tolerant_px1 <= item_cx <= tolerant_px2) and (tolerant_py1 <= item_cy <= py2):
            # For helmets, ensure it is within the upper portion of the person
            if is_helmet:
                return item_cy <= py1 + (person_height * 0.65)
            return True

        # 2. Area overlap with respect to the item
        inter_x1 = max(ix1, tolerant_px1)
        inter_y1 = max(iy1, tolerant_py1)
        inter_x2 = min(ix2, tolerant_px2)
        inter_y2 = min(iy2, py2)

        if inter_x2 > inter_x1 and inter_y2 > inter_y1:
            intersection = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
            ratio = intersection / item_area
            if ratio >= 0.20:
                if is_helmet:
                    return item_cy <= py1 + (person_height * 0.65)
                return True

        return False

    def analyze(self, detections: List[DetectionResult], frame_shape: Tuple[int, ...]) -> List[WorkerPPEStatus]:
        persons = [d for d in detections if d.object_class == 'person']
        helmets = [d for d in detections if d.object_class == 'helmet' and d.confidence >= self.confidence_threshold]
        vests = [d for d in detections if d.object_class == 'safety-vest' and d.confidence >= self.confidence_threshold]

        results = []
        for i, person in enumerate(persons):
            has_helmet = False
            has_vest = False
            helmet_conf = 0.0
            vest_conf = 0.0
            
            # Find associated helmet
            for helmet in helmets:
                if self._is_inside_or_near(helmet.bbox, person.bbox, is_helmet=True):
                    has_helmet = True
                    helmet_conf = max(helmet_conf, helmet.confidence)
                    
            # Find associated vest
            for vest in vests:
                if self._is_inside_or_near(vest.bbox, person.bbox, is_helmet=False):
                    has_vest = True
                    vest_conf = max(vest_conf, vest.confidence)
                    
            if has_helmet and has_vest:
                status = 'compliant'
            elif not has_helmet and not has_vest:
                status = 'violation'
            elif not has_helmet:
                status = 'helmet_missing'
            else:
                status = 'vest_missing'
            
            results.append(WorkerPPEStatus(
                worker_id=i,
                bbox=person.bbox,
                has_helmet=has_helmet,
                has_vest=has_vest,
                helmet_confidence=helmet_conf,
                vest_confidence=vest_conf,
                compliance_status=status
            ))
            
        return results
