# PPE Detection Methodology

## Approach
Our pipeline relies on an associative approach:
1. Detect `person` class.
2. Detect PPE items (`helmet`, `safety-vest`).
3. Compute spatial proximity.

## Worker-PPE Association Algorithm
We determine if a worker is wearing PPE by checking bounding box intersections. If a `helmet` bounding box is largely contained within the upper 30% of a `person` bounding box, it is associated.
Similar logic applies to `safety-vest` for the torso region.

## Compliance Determination
- If person + helmet + vest: **Compliant**
- If person + missing item: **Non-Compliant Alert**

## Confidence Thresholds
Minimum `ppe_confidence: 0.45` is required for valid association.

## Supported & Future Classes
- **Current**: helmet, safety-vest
- **Future**: gloves, goggles, masks

## Limitations
Occlusions and extreme angles can cause misassociations. Heavy crowding reduces accuracy.
