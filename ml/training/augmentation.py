import cv2
import albumentations as A
import os
import argparse
from pathlib import Path

def get_augmentation_pipeline():
    return A.Compose([
        A.RandomBrightnessContrast(p=0.5),
        A.GaussianBlur(p=0.3),
        A.GaussNoise(p=0.3),
        A.ColorJitter(p=0.3),
        A.CLAHE(p=0.3),
        A.RandomCrop(width=450, height=450, p=0.3),
        A.RandomRain(p=0.1),
        A.RandomFog(p=0.1),
    ], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))

def process_image(image_path, label_path, output_dir, pipeline):
    image = cv2.imread(str(image_path))
    
    boxes = []
    class_labels = []
    if label_path.exists():
        with open(label_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 5:
                    class_labels.append(int(parts[0]))
                    boxes.append([float(x) for x in parts[1:]])
                    
    try:
        augmented = pipeline(image=image, bboxes=boxes, class_labels=class_labels)
        
        base_name = image_path.stem
        new_img_name = f"{base_name}_aug.jpg"
        new_lbl_name = f"{base_name}_aug.txt"
        
        cv2.imwrite(str(output_dir / "images" / new_img_name), augmented['image'])
        
        with open(output_dir / "labels" / new_lbl_name, 'w') as f:
            for bbox, label in zip(augmented['bboxes'], augmented['class_labels']):
                f.write(f"{label} {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]}\n")
    except Exception as e:
        print(f"Skipping {image_path.name} due to error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()
    
    in_dir = Path(args.input)
    out_dir = Path(args.output)
    
    (out_dir / "images").mkdir(parents=True, exist_ok=True)
    (out_dir / "labels").mkdir(parents=True, exist_ok=True)
    
    pipeline = get_augmentation_pipeline()
    
    img_dir = in_dir / "images"
    lbl_dir = in_dir / "labels"
    
    for img_path in img_dir.glob("*.jpg"):
        lbl_path = lbl_dir / f"{img_path.stem}.txt"
        process_image(img_path, lbl_path, out_dir, pipeline)
