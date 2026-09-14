import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import { useApi } from '../hooks/useApi';
import { api } from '../services/api';
import {
  Settings as SettingsIcon,
  Cpu,
  Eye,
  Shield,
  Video,
  Info,
} from 'lucide-react';

export default function SettingsPage() {
  const { data: systemStatus } = useApi(api.getSystemStatus);

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Settings</h1>
        <p className="text-slate-500 text-sm mt-0.5">
          System configuration and detection parameters
        </p>
      </div>

      {/* System Info */}
      <Card>
        <CardHeader className="flex flex-row items-center gap-3">
          <Cpu className="w-5 h-5 text-slate-400" />
          <CardTitle>System Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-3 rounded-lg bg-slate-50">
              <p className="text-xs text-slate-500 mb-1">Detection Engine</p>
              <StatusBadge
                status={systemStatus?.model_loaded ? 'safe' : 'inactive'}
                label={systemStatus?.model_loaded ? 'Loaded' : 'Not Loaded'}
              />
            </div>
            <div className="p-3 rounded-lg bg-slate-50">
              <p className="text-xs text-slate-500 mb-1">Detection Status</p>
              <StatusBadge
                status={systemStatus?.detection_running ? 'safe' : 'inactive'}
                label={systemStatus?.detection_running ? 'Running' : 'Stopped'}
              />
            </div>
            <div className="p-3 rounded-lg bg-slate-50">
              <p className="text-xs text-slate-500 mb-1">GPU Acceleration</p>
              <StatusBadge
                status={systemStatus?.gpu_available ? 'safe' : 'warning'}
                label={systemStatus?.gpu_available ? 'Available' : 'CPU Only'}
              />
            </div>
            <div className="p-3 rounded-lg bg-slate-50">
              <p className="text-xs text-slate-500 mb-1">Active Cameras</p>
              <p className="text-lg font-semibold text-slate-900">
                {systemStatus?.active_cameras ?? 0}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Detection Settings */}
      <Card>
        <CardHeader className="flex flex-row items-center gap-3">
          <Eye className="w-5 h-5 text-slate-400" />
          <CardTitle>Detection Settings</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-5">
            <SettingRow
              label="Confidence Threshold"
              description="Minimum confidence score for object detection"
              value="0.50"
              type="text"
              disabled
            />
            <SettingRow
              label="IOU Threshold"
              description="Intersection over union threshold for NMS"
              value="0.45"
              type="text"
              disabled
            />
            <SettingRow
              label="Input Resolution"
              description="Model input size in pixels"
              value="640"
              type="text"
              disabled
            />
            <SettingRow
              label="Model"
              description="Active detection model"
              value="YOLOv8n (COCO)"
              type="text"
              disabled
            />
          </div>
          <p className="text-xs text-slate-400 mt-4 italic">
            Live settings editing is planned for Phase 2. Currently configured via .env file.
          </p>
        </CardContent>
      </Card>

      {/* Video Settings */}
      <Card>
        <CardHeader className="flex flex-row items-center gap-3">
          <Video className="w-5 h-5 text-slate-400" />
          <CardTitle>Video Processing</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-5">
            <SettingRow label="FPS Limit" description="Maximum frames per second" value="30" type="text" disabled />
            <SettingRow label="Frame Skip" description="Skip N frames between processed frames" value="0" type="text" disabled />
            <SettingRow label="Max Upload Size" description="Maximum video file size" value="500 MB" type="text" disabled />
          </div>
        </CardContent>
      </Card>

      {/* Safety Rules */}
      <Card>
        <CardHeader className="flex flex-row items-center gap-3">
          <Shield className="w-5 h-5 text-slate-400" />
          <CardTitle>Safety Rules</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-5">
            <SettingRow label="PPE Confidence" description="Minimum confidence for PPE detection" value="0.45" type="text" disabled />
            <SettingRow label="Obstacle Persistence" description="Frames object must persist before alert" value="10 frames" type="text" disabled />
            <SettingRow label="Zone Overlap Threshold" description="Minimum overlap ratio with safety zone" value="30%" type="text" disabled />
            <SettingRow label="Event Cooldown" description="Minimum time between duplicate events" value="30 seconds" type="text" disabled />
          </div>
        </CardContent>
      </Card>

      {/* About */}
      <Card>
        <CardHeader className="flex flex-row items-center gap-3">
          <Info className="w-5 h-5 text-slate-400" />
          <CardTitle>About</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm text-slate-600">
            <p><span className="font-medium text-slate-900">Project:</span> Smart Workplace Safety Intelligence Platform</p>
            <p><span className="font-medium text-slate-900">Version:</span> 1.0.0 — Phase 1 (40%)</p>
            <p><span className="font-medium text-slate-900">Engine:</span> Ultralytics YOLOv8n</p>
            <p><span className="font-medium text-slate-900">Backend:</span> FastAPI + SQLite</p>
            <p><span className="font-medium text-slate-900">Frontend:</span> React + TypeScript + Tailwind CSS</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function SettingRow({ label, description, value, type, disabled }: {
  label: string;
  description: string;
  value: string;
  type: string;
  disabled?: boolean;
}) {
  return (
    <div className="flex items-center justify-between py-1">
      <div>
        <p className="text-sm font-medium text-slate-900">{label}</p>
        <p className="text-xs text-slate-500">{description}</p>
      </div>
      <input
        type={type}
        value={value}
        disabled={disabled}
        readOnly
        className="w-32 text-right px-3 py-1.5 rounded-lg border border-slate-200 bg-slate-50 text-sm text-slate-700 disabled:opacity-70"
      />
    </div>
  );
}
