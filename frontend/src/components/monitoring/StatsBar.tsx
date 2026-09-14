import React from 'react';
import { DetectionFrame } from '../../types';
import { formatFPS, formatLatency } from '../../utils/format';
import { Activity, Clock, Users, Box, Wifi, WifiOff } from 'lucide-react';
import clsx from 'clsx';

interface StatsBarProps {
  frame: DetectionFrame | null;
  isConnected: boolean;
}

export function StatsBar({ frame, isConnected }: StatsBarProps) {
  const detectionsCount = frame?.detections ? frame.detections.length : 0;
  const workerCount = frame?.worker_count ?? (frame?.ppe_statuses ? frame.ppe_statuses.length : 0);
  const fps = frame?.fps ?? 0;
  const latency = frame?.latency_ms ?? 0;

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm px-6 py-3 flex items-center justify-between">
      <div className="flex items-center space-x-8">
        <div className="flex items-center">
          {isConnected ? (
            <Wifi className="w-4 h-4 text-emerald-500 mr-2" />
          ) : (
            <WifiOff className="w-4 h-4 text-slate-400 mr-2" />
          )}
          <span className="text-sm font-medium text-slate-600">
            {isConnected ? 'Connected' : 'Connecting / Idle'}
          </span>
        </div>
        
        {frame && (
          <>
            <div className="flex items-center">
              <Activity className="w-4 h-4 text-slate-400 mr-2" />
              <span className="text-sm text-slate-600 mr-1">FPS:</span>
              <span className={clsx(
                "text-sm font-bold",
                fps > 20 ? "text-emerald-600" : fps > 10 ? "text-amber-600" : "text-slate-700"
              )}>
                {fps > 0 ? formatFPS(fps) : '—'}
              </span>
            </div>
            
            <div className="flex items-center">
              <Clock className="w-4 h-4 text-slate-400 mr-2" />
              <span className="text-sm text-slate-600 mr-1">Latency:</span>
              <span className="text-sm font-bold text-slate-900">
                {latency > 0 ? formatLatency(latency) : '—'}
              </span>
            </div>

            <div className="flex items-center">
              <Users className="w-4 h-4 text-slate-400 mr-2" />
              <span className="text-sm text-slate-600 mr-1">Workers:</span>
              <span className="text-sm font-bold text-slate-900">{workerCount}</span>
            </div>
            
            <div className="flex items-center">
              <Box className="w-4 h-4 text-slate-400 mr-2" />
              <span className="text-sm text-slate-600 mr-1">Objects:</span>
              <span className="text-sm font-bold text-slate-900">{detectionsCount}</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
