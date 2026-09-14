import argparse
import time
import json
from pathlib import Path
from ultralytics import YOLO

def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate YOLO Model")
    parser.add_argument("--model", type=str, required=True, help="Path to model weights")
    parser.add_argument("--data", type=str, required=True, help="Path to data.yaml")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", type=str, default="auto")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    return parser.parse_args()

def main():
    print("NOTE: Run this script after training to generate real evaluation metrics. Do NOT fabricate results.")
    args = parse_args()
    
    model = YOLO(args.model)
    
    start_time = time.time()
    results = model.val(
        data=args.data,
        imgsz=args.imgsz,
        device=args.device,
        conf=args.conf,
        iou=args.iou,
        split='test'
    )
    end_time = time.time()
    
    # Process results
    metrics = {
        "mAP50": float(results.box.map50),
        "mAP50-95": float(results.box.map),
        "precision": float(results.box.mp),
        "recall": float(results.box.mr),
        "f1": float(results.box.f1.mean() if len(results.box.f1) > 0 else 0),
        "inference_speed_ms": results.speed['inference'],
        "fps": 1000.0 / results.speed['inference'] if results.speed['inference'] > 0 else 0
    }
    
    print("\nEvaluation Results:")
    print("-" * 30)
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")
        
    with open("eval_results.json", "w") as f:
        json.dump(metrics, f, indent=4)
        
if __name__ == "__main__":
    main()
