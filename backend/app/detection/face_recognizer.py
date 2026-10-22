from __future__ import annotations
"""
Face Recognition Engine using dlib-based face_recognition library.
Stores face encodings to disk (face_data/ directory) as a pickle file.
Supports multiple faces, multiple images per person, retraining, and real-time detection.
"""
import os
import pickle
import logging
import uuid
import base64
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)

FACE_DATA_DIR = Path("face_data")
FACE_IMAGES_DIR = FACE_DATA_DIR / "images"
ENCODINGS_FILE = FACE_DATA_DIR / "encodings.pkl"

# FaceRecord stored on disk
# { "persons": [ { "id": str, "name": str, "image_paths": [str], "encodings": [np.ndarray] } ] }


class FaceRecognizer:
    def __init__(self, tolerance: float = 0.5):
        self.tolerance = tolerance
        self._persons: list[dict] = []   # list of {id, name, image_paths, encodings}
        self._all_encodings: list       = []  # flat list of np.ndarray
        self._all_names: list[str]      = []  # parallel name list
        self._thumbnails_by_name: dict[str, str] = {}  # cache name -> base64 trained thumbnail
        self._loaded = False

        FACE_DATA_DIR.mkdir(exist_ok=True)
        FACE_IMAGES_DIR.mkdir(exist_ok=True)
        self._load_encodings()

    def _load_encodings(self):
        if ENCODINGS_FILE.exists():
            try:
                with open(ENCODINGS_FILE, "rb") as f:
                    data = pickle.load(f)
                self._persons = data.get("persons", [])
                self._rebuild_flat_lists()
                self._loaded = True
                logger.info(f"Loaded {len(self._persons)} persons from encodings file.")
            except Exception as e:
                logger.error(f"Failed to load encodings: {e}")
                self._persons = []
        self._loaded = True

    def _rebuild_flat_lists(self):
        self._all_encodings = []
        self._all_names = []
        self._thumbnails_by_name = {}
        for person in self._persons:
            name = person["name"]
            thumb = self.get_person_thumbnail(person["id"])
            if thumb:
                self._thumbnails_by_name[name] = thumb
            for enc in person.get("encodings", []):
                self._all_encodings.append(enc)
                self._all_names.append(name)

    def _save_encodings(self):
        # Detach encodings from persons before saving (convert to list for pickle safety)
        data = {"persons": self._persons}
        with open(ENCODINGS_FILE, "wb") as f:
            pickle.dump(data, f)
        logger.info(f"Saved {len(self._persons)} persons to disk.")

    def get_all_persons(self) -> list[dict]:
        return [
            {
                "id": p["id"],
                "name": p["name"],
                "image_count": len(p.get("image_paths", [])),
                "encoding_count": len(p.get("encodings", [])),
            }
            for p in self._persons
        ]

    def add_person(self, name: str, image_bytes_list: list[bytes]) -> dict:
        """Add a new person with one or more face images. Returns result dict."""
        import face_recognition

        person_id = str(uuid.uuid4())
        person_img_dir = FACE_IMAGES_DIR / person_id
        person_img_dir.mkdir(exist_ok=True)

        encodings = []
        saved_paths = []
        errors = []

        for i, img_bytes in enumerate(image_bytes_list):
            try:
                # Decode image
                nparr = np.frombuffer(img_bytes, np.uint8)
                import cv2
                img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if img_bgr is None:
                    errors.append(f"Image {i+1}: Could not decode image")
                    continue
                img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

                # Find face encodings
                face_locs = face_recognition.face_locations(img_rgb, model="hog")
                if not face_locs:
                    errors.append(f"Image {i+1}: No face detected")
                    continue

                face_encs = face_recognition.face_encodings(img_rgb, face_locs)
                if not face_encs:
                    errors.append(f"Image {i+1}: Could not encode face")
                    continue

                # Use largest face (by bounding box area)
                areas = [(b-t)*(r-l) for (t,r,b,l) in face_locs]
                best_idx = int(np.argmax(areas))
                encodings.append(face_encs[best_idx])

                # Save image
                img_path = str(person_img_dir / f"face_{i}.jpg")
                cv2.imwrite(img_path, img_bgr)
                saved_paths.append(img_path)

            except Exception as e:
                errors.append(f"Image {i+1}: {str(e)}")

        if not encodings:
            return {"success": False, "errors": errors, "person_id": None}

        person_record = {
            "id": person_id,
            "name": name,
            "image_paths": saved_paths,
            "encodings": encodings,
        }
        self._persons.append(person_record)
        self._rebuild_flat_lists()
        self._save_encodings()

        return {
            "success": True,
            "person_id": person_id,
            "name": name,
            "encodings_added": len(encodings),
            "errors": errors,
        }

    def add_images_to_person(self, person_id: str, image_bytes_list: list[bytes]) -> dict:
        """Add more face images to an existing person."""
        import face_recognition

        person = next((p for p in self._persons if p["id"] == person_id), None)
        if not person:
            return {"success": False, "errors": ["Person not found"]}

        person_img_dir = FACE_IMAGES_DIR / person_id
        person_img_dir.mkdir(exist_ok=True)

        existing_count = len(person.get("image_paths", []))
        encodings_added = 0
        errors = []

        for i, img_bytes in enumerate(image_bytes_list):
            try:
                nparr = np.frombuffer(img_bytes, np.uint8)
                import cv2
                img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if img_bgr is None:
                    errors.append(f"Image {i+1}: Could not decode")
                    continue
                img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

                face_locs = face_recognition.face_locations(img_rgb, model="hog")
                if not face_locs:
                    errors.append(f"Image {i+1}: No face detected")
                    continue

                face_encs = face_recognition.face_encodings(img_rgb, face_locs)
                if not face_encs:
                    continue

                areas = [(b-t)*(r-l) for (t,r,b,l) in face_locs]
                best_idx = int(np.argmax(areas))
                person["encodings"].append(face_encs[best_idx])

                img_path = str(person_img_dir / f"face_{existing_count + i}.jpg")
                cv2.imwrite(img_path, img_bgr)
                person["image_paths"].append(img_path)
                encodings_added += 1

            except Exception as e:
                errors.append(f"Image {i+1}: {str(e)}")

        self._rebuild_flat_lists()
        self._save_encodings()
        return {"success": True, "encodings_added": encodings_added, "errors": errors}

    def delete_person(self, person_id: str) -> bool:
        before = len(self._persons)
        self._persons = [p for p in self._persons if p["id"] != person_id]
        if len(self._persons) < before:
            self._rebuild_flat_lists()
            self._save_encodings()
            # Clean up images
            import shutil
            img_dir = FACE_IMAGES_DIR / person_id
            if img_dir.exists():
                shutil.rmtree(img_dir)
            return True
        return False

    def recognize_faces(self, frame_bgr: np.ndarray) -> list[dict]:
        """
        Detect and recognize all faces in a frame with high-speed downscaling.
        Returns list of {name, confidence, bbox: [x1,y1,x2,y2], face_crop_b64: str, trained_thumbnail_b64: str}
        """
        if not self._all_encodings or frame_bgr is None:
            return []

        try:
            import face_recognition
            import cv2

            # Resize to target width 320 for rapid 10x-faster HOG detection
            h, w = frame_bgr.shape[:2]
            target_w = 320.0
            scale = target_w / float(w) if w > target_w else 1.0
            if scale < 1.0:
                small = cv2.resize(frame_bgr, (int(w * scale), int(h * scale)))
            else:
                small = frame_bgr
            rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

            face_locs = face_recognition.face_locations(rgb_small, model="hog")
            if not face_locs:
                return []

            face_encs = face_recognition.face_encodings(rgb_small, face_locs)
            inv_scale = 1.0 / scale

            results = []
            for (top, right, bottom, left), enc in zip(face_locs, face_encs):
                # Scale back to original frame coordinates
                top_orig = int(round(top * inv_scale))
                right_orig = int(round(right * inv_scale))
                bottom_orig = int(round(bottom * inv_scale))
                left_orig = int(round(left * inv_scale))

                # Compute distances against all stored encodings
                distances = face_recognition.face_distance(self._all_encodings, enc)
                best_idx = int(np.argmin(distances))
                best_dist = float(distances[best_idx])

                if best_dist <= self.tolerance:
                    name = self._all_names[best_idx]
                    confidence = max(0.0, 1.0 - best_dist)
                    trained_thumb = self._thumbnails_by_name.get(name, "")
                else:
                    name = "Unknown"
                    confidence = 0.0
                    trained_thumb = ""

                # Optional tight face crop from live frame
                pad = 10
                fy1 = max(0, top_orig - pad)
                fy2 = min(h, bottom_orig + pad)
                fx1 = max(0, left_orig - pad)
                fx2 = min(w, right_orig + pad)
                face_crop = frame_bgr[fy1:fy2, fx1:fx2]

                # Encode crop to base64
                face_b64 = ""
                if face_crop.size > 0:
                    _, buf = cv2.imencode(".jpg", face_crop, [cv2.IMWRITE_JPEG_QUALITY, 75])
                    face_b64 = base64.b64encode(buf).decode("utf-8")

                results.append({
                    "name": name,
                    "confidence": round(confidence, 3),
                    "bbox": [left_orig, top_orig, right_orig, bottom_orig],
                    "face_crop_b64": face_b64,
                    "trained_thumbnail_b64": trained_thumb,
                })

            return results
        except Exception as e:
            logger.error(f"Face recognition error: {e}", exc_info=True)
            return []

    def get_person_thumbnail(self, person_id: str) -> Optional[str]:
        """Returns base64 JPEG of first saved face image for a person."""
        import cv2
        person = next((p for p in self._persons if p["id"] == person_id), None)
        if not person or not person.get("image_paths"):
            return None
        img_path = person["image_paths"][0]
        if not os.path.exists(img_path):
            return None
        img = cv2.imread(img_path)
        if img is None:
            return None
        # Crop a small thumbnail
        img = cv2.resize(img, (80, 80))
        _, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 80])
        return base64.b64encode(buf).decode("utf-8")

    @property
    def is_trained(self) -> bool:
        return len(self._all_encodings) > 0
