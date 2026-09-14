import os
from pathlib import Path
from ultralytics import YOLO

def main():
    models_dir = Path(__file__).parent.parent / "ml" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading YOLOv8n to {models_dir}...")
    # This automatically downloads the weights from ultralytics if they don't exist
    model = YOLO("yolov8n.pt")
    
    # Move the model to the correct directory
    if Path("yolov8n.pt").exists():
        Path("yolov8n.pt").rename(models_dir / "yolov8n.pt")
        print("Download verified and saved to ml/models/yolov8n.pt")
        
    print(model.info())

if __name__ == "__main__":
    main()
