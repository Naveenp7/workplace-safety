from __future__ import annotations
import cv2
import numpy as np
import base64
import os
from typing import List, Optional
from app.schemas.detection import DetectionResult, WorkerPPEStatus, ObstacleWarning, FaceRecognitionResult
from app.models.safety_zone import SafetyZone

def encode_frame_to_base64(frame: np.ndarray, quality: int = 70) -> str:
    """Encode OpenCV frame to base64 JPEG string."""
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    ret, buffer = cv2.imencode('.jpg', frame, encode_params)
    if not ret:
        return ""
    return base64.b64encode(buffer).decode('utf-8')

def draw_detections(
    frame: np.ndarray,
    detections: List[DetectionResult],
    ppe_statuses: List[WorkerPPEStatus],
    obstacle_warnings: List[ObstacleWarning],
    zones: List[SafetyZone],
    face_recognitions: Optional[List[FaceRecognitionResult]] = None,
    include_boxes: bool = True,
) -> np.ndarray:
    """Draw bounding boxes, labels, and zones on the frame."""
    out_frame = frame.copy()
    height, width = out_frame.shape[:2]

    # BGR Colors
    GREEN = (0, 200, 50)
    AMBER = (0, 165, 255)
    RED = (0, 0, 230)
    CYAN = (255, 220, 0)
    BLUE = (220, 100, 0)
    # Purple/Violet for face recognition (BGR: 237, 58, 124 → approx #7c3aed in RGB)
    VIOLET = (237, 58, 124)

    # Draw zones
    for zone in zones:
        if not zone.is_active or not zone.points:
            continue
        try:
            points = np.array([[(pt['x'] * width), (pt['y'] * height)] for pt in zone.points], np.int32)
            points = points.reshape((-1, 1, 2))

            # Draw translucent polygon overlay
            overlay = out_frame.copy()
            cv2.fillPoly(overlay, [points], BLUE)
            cv2.addWeighted(overlay, 0.25, out_frame, 0.75, 0, out_frame)
            cv2.polylines(out_frame, [points], True, BLUE, 2)

            # Zone name
            cv2.putText(out_frame, zone.name, (points[0][0][0], max(20, points[0][0][1] - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, BLUE, 2)
        except Exception:
            pass

    # If boxes should not be drawn into the bitmap (e.g. for live streaming where frontend canvas renders them)
    if not include_boxes:
        return out_frame

    # Draw individual gear items (Helmets in Cyan)
    for d in detections:
        if d.object_class == 'helmet':
            x1, y1, x2, y2 = map(int, d.bbox)
            cv2.rectangle(out_frame, (x1, y1), (x2, y2), CYAN, 2)
            cv2.putText(out_frame, f"Hard Hat {int(d.confidence*100)}%", (x1, max(18, y1 - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, CYAN, 2)

    # Draw PPE Statuses
    for ppe in ppe_statuses:
        x1, y1, x2, y2 = map(int, ppe.bbox)
        if ppe.compliance_status == 'compliant':
            color = GREEN
            label = "PPE Compliant"
        elif ppe.has_helmet:
            color = AMBER
            label = "Helmet OK (Vest Missing)"
        elif ppe.has_vest:
            color = AMBER
            label = "Vest OK (Helmet Missing)"
        else:
            color = RED
            label = "No Helmet / No Vest"

        cv2.rectangle(out_frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(out_frame, label, (x1, max(20, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # Draw Obstacles
    for obs in obstacle_warnings:
        x1, y1, x2, y2 = map(int, obs.bbox)
        cv2.rectangle(out_frame, (x1, y1), (x2, y2), AMBER, 2)

        label = f"Hazard: {obs.object_class} in {obs.zone_name}"
        cv2.putText(out_frame, label, (x1, max(20, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, AMBER, 2)

    # Draw Face Recognitions (purple/violet boxes with name label)
    if face_recognitions:
        for face in face_recognitions:
            try:
                x1, y1, x2, y2 = map(int, face.bbox)
                conf_pct = int(face.confidence * 100)
                label = f"{face.name} ({conf_pct}%)" if face.name != "Unknown" else "Unknown"

                # Draw bounding box
                cv2.rectangle(out_frame, (x1, y1), (x2, y2), VIOLET, 2)

                # Filled label bar at top of box
                label_h = 20
                label_y = max(y1 - label_h, 0)
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.52
                thickness = 1
                (text_w, text_h), baseline = cv2.getTextSize(label, font, font_scale, thickness)

                cv2.rectangle(out_frame, (x1, label_y), (x1 + text_w + 8, label_y + label_h), VIOLET, -1)
                cv2.putText(out_frame, label, (x1 + 4, label_y + label_h - 5),
                            font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
            except Exception:
                pass

    return out_frame

def validate_video_file(filename: str, max_size_mb: int) -> bool:
    """Validate uploaded video file extension and size."""
    allowed_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
    ext = os.path.splitext(filename)[1].lower()
    return ext in allowed_extensions

def get_video_info(path: str) -> dict:
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return {}
        
    info = {
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "fps": float(cap.get(cv2.CAP_PROP_FPS)),
        "total_frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        "duration": int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / max(cap.get(cv2.CAP_PROP_FPS), 1.0))
    }
    cap.release()
    return info
