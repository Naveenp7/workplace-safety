import sys
from pathlib import Path
from datetime import datetime, timezone
import pytest
import torch

# PyTorch 2.6+ compatibility for Ultralytics weights loading
try:
    _orig_torch_load = torch.load
    def _compat_torch_load(*args, **kwargs):
        if "weights_only" not in kwargs:
            kwargs["weights_only"] = False
        return _orig_torch_load(*args, **kwargs)
    torch.load = _compat_torch_load
except Exception:
    pass

# Ensure backend directory is in sys.path
backend_path = Path(__file__).resolve().parent.parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.schemas.detection import DetectionResult, ObstacleWarning
from app.models.safety_zone import SafetyZone
from app.detection.ppe_analyzer import PPEAnalyzer
from app.detection.obstacle_analyzer import ObstacleAnalyzer
from app.detection.tracker import DetectionTracker
from app.detection.engine import DetectionEngine


import asyncio

def test_model_loading():
    model_path = Path("ml/models/yolov8n.pt")
    if not model_path.exists():
        pytest.skip("Model not downloaded, skipping load test.")
    
    engine = DetectionEngine(str(model_path), "cpu", 0.5, 0.45, 640)
    asyncio.run(engine.load_model())
    assert engine.is_loaded is True
    assert engine.get_model_info()["is_loaded"] is True


def test_ppe_analyzer_compliant():
    """Test when worker has both helmet and safety-vest within bounds -> compliant."""
    analyzer = PPEAnalyzer(confidence_threshold=0.45)
    now = datetime.now(timezone.utc)
    
    detections = [
        DetectionResult(object_class="person", confidence=0.92, bbox=[100.0, 100.0, 300.0, 500.0], timestamp=now),
        DetectionResult(object_class="helmet", confidence=0.88, bbox=[140.0, 100.0, 260.0, 180.0], timestamp=now),
        DetectionResult(object_class="safety-vest", confidence=0.85, bbox=[120.0, 180.0, 280.0, 350.0], timestamp=now),
    ]
    
    results = analyzer.analyze(detections, frame_shape=(720, 1280, 3))
    assert len(results) == 1
    worker = results[0]
    assert worker.has_helmet is True
    assert worker.has_vest is True
    assert worker.compliance_status == "compliant"


def test_ppe_analyzer_helmet_missing():
    """Test when worker is missing a helmet -> helmet_missing."""
    analyzer = PPEAnalyzer(confidence_threshold=0.45)
    now = datetime.now(timezone.utc)
    
    detections = [
        DetectionResult(object_class="person", confidence=0.92, bbox=[100.0, 100.0, 300.0, 500.0], timestamp=now),
        DetectionResult(object_class="safety-vest", confidence=0.85, bbox=[120.0, 180.0, 280.0, 350.0], timestamp=now),
    ]
    
    results = analyzer.analyze(detections, frame_shape=(720, 1280, 3))
    assert len(results) == 1
    worker = results[0]
    assert worker.has_helmet is False
    assert worker.has_vest is True
    assert worker.compliance_status == "helmet_missing"


def test_ppe_analyzer_vest_missing():
    """Test when worker is missing a safety vest -> vest_missing."""
    analyzer = PPEAnalyzer(confidence_threshold=0.45)
    now = datetime.now(timezone.utc)
    
    detections = [
        DetectionResult(object_class="person", confidence=0.92, bbox=[100.0, 100.0, 300.0, 500.0], timestamp=now),
        DetectionResult(object_class="helmet", confidence=0.88, bbox=[140.0, 100.0, 260.0, 180.0], timestamp=now),
    ]
    
    results = analyzer.analyze(detections, frame_shape=(720, 1280, 3))
    assert len(results) == 1
    worker = results[0]
    assert worker.has_helmet is True
    assert worker.has_vest is False
    assert worker.compliance_status == "vest_missing"


def test_ppe_analyzer_full_violation():
    """Test when worker has neither helmet nor vest -> violation."""
    analyzer = PPEAnalyzer(confidence_threshold=0.45)
    now = datetime.now(timezone.utc)
    
    detections = [
        DetectionResult(object_class="person", confidence=0.92, bbox=[100.0, 100.0, 300.0, 500.0], timestamp=now),
    ]
    
    results = analyzer.analyze(detections, frame_shape=(720, 1280, 3))
    assert len(results) == 1
    worker = results[0]
    assert worker.has_helmet is False
    assert worker.has_vest is False
    assert worker.compliance_status == "violation"


def test_obstacle_zone_overlap():
    """Test obstacle analyzer detecting object inside defined safety zone."""
    analyzer = ObstacleAnalyzer(overlap_threshold=0.3)
    now = datetime.now(timezone.utc)
    frame_shape = (1000, 1000, 3)  # 1000x1000 for clean normalized coords

    # Create a safety zone covering normalized [0.2, 0.2] to [0.6, 0.6]
    zone = SafetyZone(
        id=1,
        name="Walkway A",
        zone_type="walkway",
        points=[
            {"x": 0.2, "y": 0.2},
            {"x": 0.6, "y": 0.2},
            {"x": 0.6, "y": 0.6},
            {"x": 0.2, "y": 0.6},
        ],
        is_active=True,
        detection_threshold=0.3,
        persistence_frames=5,
        color="#3b82f6",
    )

    # Object 1: backpack inside the zone (pixels 300, 300 to 400, 400)
    # Object 2: backpack outside the zone (pixels 800, 800 to 900, 900)
    # Object 3: person inside the zone (should be excluded from obstacles)
    detections = [
        DetectionResult(object_class="backpack", confidence=0.85, bbox=[300.0, 300.0, 400.0, 400.0], timestamp=now),
        DetectionResult(object_class="backpack", confidence=0.80, bbox=[800.0, 800.0, 900.0, 900.0], timestamp=now),
        DetectionResult(object_class="person", confidence=0.90, bbox=[320.0, 320.0, 420.0, 480.0], timestamp=now),
    ]

    warnings = analyzer.analyze(detections, [zone], frame_shape)
    assert len(warnings) == 1
    assert warnings[0].object_class == "backpack"
    assert warnings[0].zone_name == "Walkway A"
    assert warnings[0].zone_id == 1


def test_tracker_persistence_and_cooldown():
    """Test detection tracker persistence frames requirement and event cooldown."""
    tracker = DetectionTracker(persistence_threshold=3, cooldown_seconds=2.0)
    
    obs = ObstacleWarning(
        object_class="box",
        confidence=0.88,
        bbox=[200.0, 200.0, 260.0, 260.0],
        zone_id=1,
        zone_name="Walkway",
        frames_persisted=1
    )

    # Frame 1: count=1 < threshold(3) -> not persistent
    res1 = tracker.get_persistent_obstacles([obs])
    assert len(res1) == 0

    # Frame 2: count=2 < threshold(3) -> not persistent
    res2 = tracker.get_persistent_obstacles([obs])
    assert len(res2) == 0

    # Frame 3: count=3 == threshold(3) -> persistent!
    res3 = tracker.get_persistent_obstacles([obs])
    assert len(res3) == 1
    assert res3[0].frames_persisted == 3

    # Cooldown verification
    event_key = "obstacle_camera1_zone1_box"
    assert tracker.should_create_event(event_key) is True
    # Immediate duplicate event should be blocked by cooldown
    assert tracker.should_create_event(event_key) is False
