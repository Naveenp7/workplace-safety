# Workplace Safety Datasets

This directory contains the dataset preparation and configuration files for training the YOLO model.

## Recommended Datasets
- **Roboflow PPE Datasets**: Useful for identifying hardhats and safety vests.
- **COCO Dataset**: General objects, useful for person detection.
- **Construction Safety Datasets (Kaggle/Open Source)**: Contains various scenarios of construction workers and obstacles.

## Structure
We expect the YOLO dataset format:
```
datasets/
  images/
    train/
    val/
    test/
  labels/
    train/
    val/
    test/
  data.yaml
```

## Annotation Format
YOLO format: `<class_id> <x_center> <y_center> <width> <height>` (normalized 0 to 1).

## Required Classes
```yaml
0: person
1: helmet
2: no-helmet
3: safety-vest
4: no-vest
```

## Data Split & Augmentation
- **Train/Val/Test Split**: 70/20/10 ratio is recommended.
- **Augmentation**: Use mosaic, mixup, random flip, and color jitter for better generalization across varying lighting conditions.
