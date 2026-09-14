import { SystemStatus, DetectionStatus, SafetyEvent, SafetyZone, Camera } from '../types';

const API_BASE = '/api';

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, options);
  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

export const api = {
  fetchHealth: () => fetchJSON<{ status: string }>('/health'),
  
  uploadVideo: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(`${API_BASE}/video/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) throw new Error('Upload failed');
    return response.json();
  },

  startDetection: (sourceType: string, sourceUri: string, cameraId?: number) => 
    fetchJSON('/detection/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source_type: sourceType, source_uri: sourceUri, camera_id: cameraId }),
    }),

  stopDetection: () => fetchJSON('/detection/stop', { method: 'POST' }),
  
  getDetectionStatus: () => fetchJSON<DetectionStatus>('/detection/status'),

  getEvents: async (filters?: Record<string, string>) => {
    const params = new URLSearchParams(filters || {}).toString();
    const response = await fetchJSON<{ items: SafetyEvent[]; total: number }>(`/events${params ? `?${params}` : ''}`);
    return response.items;
  },

  getEventStats: () => fetchJSON<any>('/events/stats/summary'),

  getZones: (cameraId?: number) => {
    const params = cameraId ? `?camera_id=${cameraId}` : '';
    return fetchJSON<SafetyZone[]>(`/zones${params}`);
  },

  createZone: (data: Partial<SafetyZone>) => 
    fetchJSON<SafetyZone>('/zones', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }),

  updateZone: (id: number, data: Partial<SafetyZone>) => 
    fetchJSON<SafetyZone>(`/zones/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }),

  deleteZone: (id: number) => fetchJSON(`/zones/${id}`, { method: 'DELETE' }),

  getCameras: () => fetchJSON<Camera[]>('/cameras'),

  createCamera: (data: Partial<Camera>) => 
    fetchJSON<Camera>('/cameras', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }),

  deleteCamera: (id: number) => fetchJSON(`/cameras/${id}`, { method: 'DELETE' }),

  getSettings: () => fetchJSON<any>('/settings'),

  updateSettings: (data: any) => 
    fetchJSON<any>('/settings', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }),

  getSystemStatus: () => fetchJSON<SystemStatus>('/settings/system-status'),
};
