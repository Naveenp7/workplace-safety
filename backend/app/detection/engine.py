from __future__ import annotations
import time
import numpy as np
import os
from pathlib import Path
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

import logging
from ultralytics import YOLO
from datetime import datetime, timezone
from typing import Tuple, List, Dict
from app.schemas.detection import DetectionResult

logger = logging.getLogger(__name__)

class DetectionEngine:
    def __init__(self, model_path: str, device: str, conf_threshold: float, iou_threshold: float, input_size: int):
        self.model_path = model_path
        self.device = device
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.input_size = input_size
        self._model = None
        self._ppe_model = None
        
        # Mapping COCO classes to our logic
        self.class_mapping = {
            0: 'person',
            24: 'backpack',
            27: 'tie',
            28: 'suitcase',
            39: 'bottle',
            56: 'chair',
            57: 'couch',
            58: 'potted plant',
            59: 'bed',
            60: 'dining table',
        }

    async def load_model(self) -> None:
        """Load and warm up the base model and dedicated PPE model if present."""
        try:
            device = 'cuda' if torch.cuda.is_available() and self.device in ['auto', 'cuda'] else 'cpu'
            logger.info(f"Loading primary model {self.model_path} on device {device}")
            self._model = YOLO(self.model_path)
            self._model.to(device)
            
            # Check for dedicated Hardhat / PPE model
            root_dir = Path(__file__).resolve().parents[3]
            candidates = [
                root_dir / "ml" / "models" / "hardhat_model.pt",
                Path(__file__).resolve().parents[2] / "models" / "hardhat_model.pt",
                Path("models/hardhat_model.pt"),
                Path("ml/models/hardhat_model.pt"),
                Path("hardhat_model.pt"),
                root_dir / "ml" / "models" / "ppe_model.pt",
            ]
            for c in candidates:
                if c.exists():
                    resolved_path = str(c.resolve())
                    logger.info(f"SUCCESS: Loaded dedicated Hardhat / PPE model from: {resolved_path}")
                    print(f"[YOLO ENGINE] Successfully loaded dedicated Hardhat model from: {resolved_path}")
                    self._ppe_model = YOLO(resolved_path)
                    self._ppe_model.to(device)
                    break

            # Warm up
            dummy_img = np.zeros((self.input_size, self.input_size, 3), dtype=np.uint8)
            self._model(dummy_img, verbose=False)
            if self._ppe_model:
                self._ppe_model(dummy_img, verbose=False)

            logger.info("Detection engines loaded and warmed up successfully.")
        except Exception as e:
            logger.error(f"Failed to load detection model: {e}")
            raise

    def detect(self, frame: np.ndarray) -> Tuple[List[DetectionResult], float]:
        """Runs inference across primary model and PPE model."""
        if not self.is_loaded:
            raise RuntimeError("Model is not loaded")
            
        start_time = time.perf_counter()
        now = datetime.now(timezone.utc)
        detections: List[DetectionResult] = []
        
        # 1. Primary Model: detects persons and general obstacles
        results = self._model(frame, conf=self.conf_threshold, iou=self.iou_threshold, verbose=False)[0]
        for box in results.boxes:
            cls_id = int(box.cls[0].item())
            conf = float(box.conf[0].item())
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            
            class_name = self.class_mapping.get(cls_id, self._model.names.get(cls_id, f"class_{cls_id}"))
            
            detections.append(DetectionResult(
                object_class=class_name,
                confidence=conf,
                bbox=[x1, y1, x2, y2],
                timestamp=now
            ))

        # 2. PPE Model: detects hardhats, helmets, vests
        if self._ppe_model is not None:
            try:
                ppe_results = self._ppe_model(frame, conf=0.25, iou=0.45, verbose=False)[0]
                for box in ppe_results.boxes:
                    cls_id = int(box.cls[0].item())
                    conf = float(box.conf[0].item())
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    raw_name = self._ppe_model.names.get(cls_id, "").lower()

                    if "hardhat" in raw_name and "no" not in raw_name:
                        detections.append(DetectionResult(
                            object_class="helmet",
                            confidence=conf,
                            bbox=[x1, y1, x2, y2],
                            timestamp=now
                        ))
                    elif "helmet" in raw_name and "no" not in raw_name:
                        detections.append(DetectionResult(
                            object_class="helmet",
                            confidence=conf,
                            bbox=[x1, y1, x2, y2],
                            timestamp=now
                        ))
                    elif "vest" in raw_name and "no" not in raw_name:
                        detections.append(DetectionResult(
                            object_class="safety-vest",
                            confidence=conf,
                            bbox=[x1, y1, x2, y2],
                            timestamp=now
                        ))
            except Exception as e:
                logger.error(f"Error running PPE inference: {e}")
        
        inference_time_ms = (time.perf_counter() - start_time) * 1000
        return detections, inference_time_ms

    def get_model_info(self) -> dict:
        return {
            "model_path": self.model_path,
            "device": self._model.device.type if self._model else "none",
            "is_loaded": self.is_loaded,
            "has_ppe_model": self._ppe_model is not None
        }

    @property
    def is_loaded(self) -> bool:
        return self._model is not None
