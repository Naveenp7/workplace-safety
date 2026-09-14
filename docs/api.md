# API Documentation

## REST Endpoints

### `GET /api/health`
Check API status.
- **Response**: `{"status": "healthy"}`

### `POST /api/video/upload`
Upload a new video for analysis.
- **Request**: `multipart/form-data` with `file`
- **Response**: `{"video_id": "uuid", "status": "processing"}`

### `GET /api/events`
Fetch past safety events.
- **Response**: `[{"event_id": "...", "type": "no_helmet", "timestamp": "...", "frame_url": "..."}]`

## WebSocket Protocol

### `ws://domain/ws/stream/{stream_id}`
Stream real-time processed frames.
- **Client sends**: `{"action": "subscribe"}`
- **Server sends**: Binary frame data or JSON detection metadata (depending on client requested mode).

## Future Authentication
Currently, endpoints are public. JWT-based Bearer auth will be introduced in Phase 5.
