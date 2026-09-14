import React, { useState, useRef, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { VideoCanvas } from '../components/monitoring/VideoCanvas';
import { SafetyStatusPanel } from '../components/monitoring/SafetyStatusPanel';
import { StatsBar } from '../components/monitoring/StatsBar';
import { api } from '../services/api';
import { useApi } from '../hooks/useApi';
import { SafetyEvent } from '../types';
import { StatusBadge } from '../components/ui/StatusBadge';
import {
  Play,
  Square,
  Upload,
  Camera,
  Video,
  AlertTriangle,
  Clock,
  Loader2,
} from 'lucide-react';

export default function MonitoringPage() {
  const { lastFrame, isConnected, connectionStatus } = useWebSocket();
  const { data: status, refetch: refetchStatus } = useApi(api.getDetectionStatus);
  const { data: recentEvents } = useApi(() => api.getEvents({ limit: '5' }));
  const [isProcessing, setIsProcessing] = useState(false);
  const [sourceMode, setSourceMode] = useState<'webcam' | 'upload'>('webcam');
  const [uploadedFile, setUploadedFile] = useState<{ camera_id: number; path: string; name: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Poll status while detecting
  useEffect(() => {
    if (!status?.is_running) return;
    const interval = setInterval(refetchStatus, 3000);
    return () => clearInterval(interval);
  }, [status?.is_running, refetchStatus]);

  const handleStartDetection = async () => {
    setIsProcessing(true);
    setError(null);
    try {
      if (sourceMode === 'webcam') {
        await api.startDetection('webcam', '0');
      } else if (uploadedFile) {
        await api.startDetection('file', uploadedFile.path, uploadedFile.camera_id);
      }
      await refetchStatus();
    } catch (e: any) {
      setError(e.message || 'Failed to start detection');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleStopDetection = async () => {
    setIsProcessing(true);
    try {
      await api.stopDetection();
      await refetchStatus();
    } catch (e: any) {
      setError(e.message || 'Failed to stop detection');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsProcessing(true);
    setError(null);
    try {
      const result = await api.uploadVideo(file);
      setUploadedFile({
        camera_id: result.camera_id,
        path: result.path,
        name: file.name,
      });
      setSourceMode('upload');
    } catch (e: any) {
      setError(e.message || 'Failed to upload video');
    } finally {
      setIsProcessing(false);
    }
  };

  const isRunning = status?.is_running ?? false;

  return (
    <div className="flex flex-col h-full gap-4">
      {/* Header */}
      <div className="flex items-center justify-between flex-shrink-0">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Live Monitoring</h1>
          <p className="text-slate-500 text-sm mt-0.5">
            Real-time AI-powered safety analysis
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* Source Selector */}
          <div className="flex items-center bg-slate-100 rounded-lg p-1">
            <button
              onClick={() => setSourceMode('webcam')}
              disabled={isRunning}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                sourceMode === 'webcam'
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              <Camera className="w-4 h-4" />
              Webcam
            </button>
            <button
              onClick={() => setSourceMode('upload')}
              disabled={isRunning}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                sourceMode === 'upload'
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              <Video className="w-4 h-4" />
              Video File
            </button>
          </div>

          {/* Upload Button */}
          {sourceMode === 'upload' && !isRunning && (
            <>
              <input
                ref={fileInputRef}
                type="file"
                accept=".mp4,.avi,.mov,.mkv,.webm"
                onChange={handleFileUpload}
                className="hidden"
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={isProcessing}
                className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 transition-colors"
              >
                <Upload className="w-4 h-4" />
                {uploadedFile ? uploadedFile.name : 'Upload Video'}
              </button>
            </>
          )}

          {/* Start/Stop Button */}
          <button
            onClick={isRunning ? handleStopDetection : handleStartDetection}
            disabled={isProcessing || (sourceMode === 'upload' && !uploadedFile)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
              isRunning
                ? 'bg-red-600 hover:bg-red-700'
                : 'bg-indigo-600 hover:bg-indigo-700'
            }`}
          >
            {isProcessing ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : isRunning ? (
              <Square className="w-4 h-4" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            {isProcessing
              ? 'Processing...'
              : isRunning
              ? 'Stop Detection'
              : 'Start Detection'}
          </button>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          {error}
          <button onClick={() => setError(null)} className="ml-auto text-red-400 hover:text-red-600">✕</button>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 min-h-0 flex gap-4">
        {/* Video + Stats */}
        <div className="flex-1 flex flex-col min-w-0 gap-4">
          {/* Video Canvas */}
          <div className="flex-1 rounded-xl overflow-hidden border border-slate-200 bg-slate-900 relative min-h-[400px]">
            <VideoCanvas frame={lastFrame} />
            {/* Connection indicator */}
            <div className="absolute top-3 right-3">
              <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                isConnected
                  ? 'bg-emerald-500/20 text-emerald-300'
                  : 'bg-slate-500/20 text-slate-400'
              }`}>
                <span className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-emerald-400' : 'bg-slate-500'}`} />
                {connectionStatus === 'connected' ? 'Live' : connectionStatus === 'connecting' ? 'Connecting...' : 'Disconnected'}
              </div>
            </div>
          </div>

          {/* Stats Bar */}
          <StatsBar frame={lastFrame} isConnected={isConnected} />
        </div>

        {/* Right Panel: Safety Status + Recent Events */}
        <div className="w-80 flex-shrink-0 flex flex-col gap-4">
          <SafetyStatusPanel frame={lastFrame} />

          {/* Recent Events Mini List */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex-1 min-h-0 flex flex-col">
            <div className="px-4 py-3 border-b border-slate-100">
              <h3 className="text-sm font-semibold text-slate-900">Recent Events</h3>
            </div>
            <div className="flex-1 overflow-y-auto">
              {recentEvents && recentEvents.length > 0 ? (
                <div className="divide-y divide-slate-100">
                  {recentEvents.map((event: SafetyEvent) => (
                    <div key={event.id} className="px-4 py-2.5 flex items-start gap-3">
                      <div className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${
                        event.severity === 'critical' ? 'bg-red-500' :
                        event.severity === 'high' ? 'bg-red-400' :
                        event.severity === 'medium' ? 'bg-amber-500' : 'bg-blue-400'
                      }`} />
                      <div className="min-w-0 flex-1">
                        <p className="text-sm text-slate-700 truncate">
                          {event.event_type === 'ppe_violation' ? 'PPE Violation' : 'Obstacle Detected'}
                          {event.object_class && ` — ${event.object_class}`}
                        </p>
                        <div className="flex items-center gap-1.5 mt-0.5 text-xs text-slate-400">
                          <Clock className="w-3 h-3" />
                          {new Date(event.timestamp).toLocaleTimeString()}
                        </div>
                      </div>
                      <StatusBadge status={event.severity} />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex items-center justify-center h-full text-sm text-slate-400 p-4">
                  No events recorded yet
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
