# Obstacle Detection Methodology

## Approach
Obstacle detection operates by merging **object detection**, **safety zone intersection**, and **temporal persistence**.

## Safety Zones
Users can define polygonal areas via the UI. These zones signify restricted spaces or critical paths (e.g., forklift paths).

## Overlap Calculation (Shapely)
The detected bounding box of an obstacle is converted into a polygon. The `Shapely` library calculates the Intersection over Union (IoU) or raw intersection area against the predefined safety zones.
If intersection > `obstacle_zone_overlap` threshold, it flags.

## Temporal Confirmation Logic
To prevent false positives from transient misclassifications or temporary passing objects, an obstacle must persist in the zone for a minimum of `obstacle_persistence_frames` (default: 10 frames).

## Event Generation & False Positive Reduction
- Event generated only after temporal persistence is met.
- Cooldown period (`event_cooldown_seconds`) prevents event spam.
- Limitations: Lighting changes, occlusions. Future improvements will incorporate optical flow.
