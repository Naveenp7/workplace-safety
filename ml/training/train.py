#!/usr/bin/env python3
"""Training script for workplace safety object detection model."""
import argparse
import yaml
from pathlib import Path
from ultralytics import YOLO
import shutil

def parse_args():
    parser = argparse.ArgumentParser(description="Train YOLOv8 for Workplace Safety")
    parser.add_argument("--data", type=str, required=True, help="Path to data.yaml")
    parser.add_argument("--model", type=str, default="yolov8n.pt", help="Base model to use")
    parser.add_argument("--epochs", type=int, default=100, help="Number of training epochs")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--device", type=str, default="auto", help="Device to use (cuda/cpu/auto)")
    parser.add_argument("--project", type=str, default="runs/train", help="Project name")
    parser.add_argument("--name", type=str, default="workplace_safety", help="Experiment name")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config file for hyperparameters")
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Load config if exists
    config = {}
    if Path(args.config).exists():
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
            
    # Initialize model
    model = YOLO(args.model)
    
    print(f"Starting training for {args.epochs} epochs with batch size {args.batch}...")
    
    # Train model
    results = model.train(
        data=args.data,
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        device=args.device,
        project=args.project,
        name=args.name,
        optimizer=config.get('optimizer', 'AdamW'),
        lr0=config.get('lr0', 0.01),
        lrf=config.get('lrf', 0.01),
        patience=config.get('patience', 20),
        workers=8,
        mosaic=config.get('augment', {}).get('mosaic', 1.0),
        mixup=config.get('augment', {}).get('mixup', 0.1),
        hsv_h=config.get('augment', {}).get('hsv_h', 0.015),
        hsv_s=config.get('augment', {}).get('hsv_s', 0.7),
        hsv_v=config.get('augment', {}).get('hsv_v', 0.4),
        flipud=config.get('augment', {}).get('flipud', 0.0),
        fliplr=config.get('augment', {}).get('fliplr', 0.5),
        scale=config.get('augment', {}).get('scale', 0.5),
        translate=config.get('augment', {}).get('translate', 0.1),
        perspective=config.get('augment', {}).get('perspective', 0.0001)
    )
    
    print("Training completed. Exporting to ONNX...")
    model.export(format="onnx")
    
    # Save config alongside model
    save_dir = Path(args.project) / args.name
    if Path(args.config).exists() and save_dir.exists():
        shutil.copy(args.config, save_dir / "config.yaml")

if __name__ == "__main__":
    main()
