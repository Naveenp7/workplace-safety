export interface Detection {
  object_class: string;
  confidence: number;
  bbox: { x1: number; y1: number; x2: number; y2: number };
  timestamp: string;
}

export interface WorkerPPEStatus {
  worker_id: number;
  bbox: { x1: number; y1: number; x2: number; y2: number };
  has_helmet: boolean;
  has_vest: boolean;
  helmet_confidence: number;
  vest_confidence: number;
  compliance_status: 'compliant' | 'helmet_missing' | 'vest_missing' | 'violation';
}

export interface ObstacleWarning {
  object_class: string;
  confidence: number;
  bbox: { x1: number; y1: number; x2: number; y2: number };
  zone_id: number;
  zone_name: string;
  frames_persisted: number;
}

export interface FaceRecognitionResult {
  name: string;
  confidence: number;
  bbox: number[]; // [x1, y1, x2, y2]
  face_crop_b64: string;
}

export interface DetectionFrame {
  frame_base64: string;
  detections: Detection[];
  ppe_statuses: WorkerPPEStatus[];
  obstacle_warnings: ObstacleWarning[];
  face_recognitions?: FaceRecognitionResult[];
  fps: number;
  latency_ms: number;
  worker_count: number;
  timestamp: string;
}

export interface SafetyEvent {
  id: number;
  event_type: string;
  severity: string;
  camera_id: number | null;
  timestamp: string;
  confidence: number;
  object_class: string;
  zone_name: string | null;
  status: string;
  snapshot_path: string | null;
  details: Record<string, any> | null;
}

export interface SafetyZone {
  id: number;
  name: string;
  zone_type: string;
  points: { x: number; y: number }[] | number[][];
  camera_id: number | null;
  is_active: boolean;
  detection_threshold: number;
  persistence_frames: number;
  color: string;
}

export interface Camera {
  id: number;
  name: string;
  source_type: string;
  source_uri: string;
  status: string;
  created_at: string;
}

export interface DetectionStatus {
  is_running: boolean;
  source_type: string | null;
  source_uri: string | null;
  fps: number;
  latency_ms: number;
  total_frames: number;
  start_time: string | null;
}

export interface SystemStatus {
  model_loaded: boolean;
  detection_running: boolean;
  active_cameras: number;
  uptime: number;
  gpu_available: boolean;
}
