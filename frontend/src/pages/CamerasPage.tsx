import React, { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import { EmptyState } from '../components/ui/EmptyState';
import {
  Camera as CameraIcon,
  Upload,
  Video,
  Webcam,
  Trash2,
  Plus,
  Film,
  CheckCircle2,
} from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { api } from '../services/api';
import { Camera } from '../types';

export default function CamerasPage() {
  const { data: cameras, refetch } = useApi(api.getCameras);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsUploading(true);
    setUploadSuccess(null);
    try {
      await api.uploadVideo(file);
      setUploadSuccess(file.name);
      await refetch();
    } catch (err) {
      console.error('Upload failed:', err);
    } finally {
      setIsUploading(false);
    }
  };

  const handleAddWebcam = async () => {
    try {
      await api.createCamera({
        name: 'Default Webcam',
        source_type: 'webcam',
        source_uri: '0',
        status: 'inactive',
      });
      await refetch();
    } catch (err) {
      console.error('Failed to add webcam:', err);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await api.deleteCamera(id);
      await refetch();
    } catch (err) {
      console.error('Failed to delete camera:', err);
    }
  };

  const getSourceIcon = (type: string) => {
    switch (type) {
      case 'webcam': return <Webcam className="w-5 h-5" />;
      case 'file': return <Film className="w-5 h-5" />;
      default: return <Video className="w-5 h-5" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Cameras & Sources</h1>
          <p className="text-slate-500 text-sm mt-0.5">
            Manage video inputs for safety monitoring
          </p>
        </div>
        <div className="flex items-center gap-3">
          <input
            ref={fileInputRef}
            type="file"
            accept=".mp4,.avi,.mov,.mkv,.webm"
            onChange={handleFileUpload}
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 transition-colors"
          >
            <Upload className="w-4 h-4" />
            {isUploading ? 'Uploading...' : 'Upload Video'}
          </button>
          <button
            onClick={handleAddWebcam}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium bg-indigo-600 text-white hover:bg-indigo-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add Webcam
          </button>
        </div>
      </div>

      {/* Upload Success Banner */}
      {uploadSuccess && (
        <div className="flex items-center gap-2 px-4 py-3 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm">
          <CheckCircle2 className="w-4 h-4" />
          <span className="font-medium">{uploadSuccess}</span> uploaded successfully
          <button onClick={() => setUploadSuccess(null)} className="ml-auto text-emerald-400 hover:text-emerald-600">✕</button>
        </div>
      )}

      {/* Camera Grid */}
      {cameras && cameras.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cameras.map((camera: Camera) => (
            <Card key={camera.id} className="overflow-hidden">
              {/* Camera Visual Header */}
              <div className="h-32 bg-gradient-to-br from-slate-100 to-slate-200 flex items-center justify-center">
                <div className="p-4 rounded-full bg-white/80 text-slate-400">
                  {getSourceIcon(camera.source_type)}
                </div>
              </div>
              <CardContent className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-semibold text-slate-900 text-sm">{camera.name}</h3>
                    <p className="text-xs text-slate-500 mt-0.5 truncate max-w-[200px]">
                      {camera.source_uri}
                    </p>
                  </div>
                  <StatusBadge
                    status={camera.status === 'active' ? 'safe' : 'inactive'}
                    label={camera.status}
                  />
                </div>
                <div className="flex items-center justify-between pt-3 border-t border-slate-100">
                  <div className="flex items-center gap-2">
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-600">
                      {camera.source_type}
                    </span>
                  </div>
                  <button
                    onClick={() => handleDelete(camera.id)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="p-0">
            <EmptyState
              icon={CameraIcon}
              title="No Video Sources"
              description="Upload a video file or connect a webcam to begin safety monitoring."
            />
          </CardContent>
        </Card>
      )}

      {/* RTSP Notice */}
      <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
        <p className="text-sm text-slate-500">
          <span className="font-medium text-slate-700">RTSP / IP Camera Support</span> — 
          Direct CCTV stream integration via RTSP protocol is planned for Phase 2. 
          The architecture supports it — only the connection UI and stream management need to be added.
        </p>
      </div>
    </div>
  );
}
