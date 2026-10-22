"""
Helmet + Safety Vest Detector (Windows-friendly setup)
------------------------------------------------------
Run START_DETECTOR.bat by double-clicking it.

It creates a project-local virtual environment and installs dependencies there,
avoiding writes to C:\\Program Files\\Python... and avoiding the unrelated PyPI
package named "clip".

Requirements: Windows, Python 3.10/3.11/3.12 installed and available as `py`,
internet for first-time setup/model download, webcam or video file.

Important: YOLO-World is open-vocabulary, so results are approximate and must
not be used as a real safety system without validation.
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VENV_PY = ROOT / ".venv" / "Scripts" / "python.exe"


def run_setup():
    """Create isolated environment and install the exact required packages."""
    if not VENV_PY.exists():
        print("Setting up a private Python environment for this project...")
        try:
            subprocess.check_call(["py", "-3", "-m", "venv", str(ROOT / ".venv")])
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("\nPython was not found. Install Python 3.10–3.12 from:")
            print("https://www.python.org/downloads/windows/")
            print("During installation, enable 'Add Python to PATH'.")
            input("\nPress Enter to close...")
            raise SystemExit(1)

    # Install into this project's .venv, never into protected Program Files.
    packages = [
        "ultralytics",
        "opencv-python",
        # Install the CLIP implementation expected by Ultralytics from its source.
        "git+https://github.com/ultralytics/CLIP.git",
    ]
    marker = ROOT / ".venv" / ".setup_complete"
    if not marker.exists():
        print("\nInstalling required AI and video packages. This may take several minutes.")
        print("Large AI libraries may require several GB of download/storage.")
        try:
            subprocess.check_call(
                [str(VENV_PY), "-m", "pip", "install", "--upgrade", "pip"]
            )
            subprocess.check_call(
                [str(VENV_PY), "-m", "pip", "install", *packages]
            )
            marker.write_text("ok", encoding="utf-8")
        except subprocess.CalledProcessError:
            print("\nAutomatic setup failed.")
            print("Check internet access and ensure Git is installed:")
            print("https://git-scm.com/download/win")
            print("Then double-click START_DETECTOR.bat again.")
            input("\nPress Enter to close...")
            raise SystemExit(1)

    # Re-run this file under the isolated environment.
    if Path(sys.executable).resolve() != VENV_PY.resolve():
        subprocess.check_call([str(VENV_PY), str(Path(__file__).resolve()), *sys.argv[1:]])
        raise SystemExit(0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="0", help="Webcam index, video path, or stream URL")
    parser.add_argument("--conf", type=float, default=0.20)
    parser.add_argument("--imgsz", type=int, default=640)
    args = parser.parse_args()

    if not 0 <= args.conf <= 1:
        parser.error("--conf must be between 0 and 1")

    import cv2
    from ultralytics import YOLOWorld

    print("Loading pretrained YOLO-World weights (first run downloads them)...")
    model = YOLOWorld("yolov8s-worldv2.pt")
    model.set_classes(["helmet", "safety vest"])

    source = int(args.source) if args.source.isdigit() else args.source
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise SystemExit(f"Could not open source {args.source}. Try --source 0 or --source 1.")

    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    last_t = time.perf_counter()
    fps_smooth = 0.0
    print("Running. Press Q or ESC in the video window to quit.")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            result = model.predict(frame, conf=args.conf, imgsz=args.imgsz, verbose=False)[0]
            found = set()

            if result.boxes is not None:
                for box in result.boxes:
                    class_id = int(box.cls[0].item())
                    label = str(result.names.get(class_id, "")).lower()
                    if "helmet" in label or "hard hat" in label:
                        name = "Helmet"
                    elif "vest" in label:
                        name = "Safety Vest"
                    else:
                        continue

                    found.add(name)
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    confidence = float(box.conf[0].item())
                    color = (40, 160, 70)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, f"{name} {confidence:.0%}",
                                (x1, max(22, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX,
                                0.65, color, 2, cv2.LINE_AA)

            if {"Helmet", "Safety Vest"} <= found:
                status = "BOTH DETECTED"
            elif "Helmet" in found:
                status = "HELMET DETECTED"
            elif "Safety Vest" in found:
                status = "SAFETY VEST DETECTED"
            else:
                status = "NO HELMET OR VEST DETECTED"

            now = time.perf_counter()
            current_fps = 1.0 / max(now - last_t, 1e-6)
            fps_smooth = current_fps if fps_smooth == 0 else 0.85 * fps_smooth + 0.15 * current_fps
            last_t = now

            cv2.rectangle(frame, (0, 0), (frame.shape[1], 82), (30, 35, 45), -1)
            cv2.putText(frame, "HELMET & SAFETY VEST", (16, 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (230, 230, 230), 2)
            cv2.putText(frame, status, (16, 64),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.85,
                        (80, 230, 130) if found else (70, 190, 255), 2)
            cv2.putText(frame, f"FPS {fps_smooth:.1f}",
                        (max(16, frame.shape[1] - 130), 32),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.imshow("Helmet + Safety Vest Detector", frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    run_setup()
    main()
