import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { SystemStatus } from '../../types';
import { Activity, HardDrive, Cpu, Server } from 'lucide-react';
import clsx from 'clsx';

export function SystemHealthCard({ status }: { status: SystemStatus | null }) {
  if (!status) return null;

  const items = [
    {
      label: 'Detection Engine',
      value: status.detection_running ? 'Running' : 'Idle',
      icon: Activity,
      ok: status.detection_running
    },
    {
      label: 'YOLO Model',
      value: status.model_loaded ? 'Loaded' : 'Unloaded',
      icon: Cpu,
      ok: status.model_loaded
    },
    {
      label: 'Hardware Accel',
      value: status.gpu_available ? 'GPU Active' : 'CPU Mode',
      icon: HardDrive,
      ok: status.gpu_available
    },
    {
      label: 'Active Cameras',
      value: status.active_cameras.toString(),
      icon: Server,
      ok: status.active_cameras > 0
    }
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>System Health</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-2 gap-4">
        {items.map((item, i) => (
          <div key={i} className="flex items-center p-3 rounded-lg bg-slate-50 border border-slate-100">
            <div className={clsx(
              "p-2 rounded-md mr-3",
              item.ok ? "bg-emerald-100 text-emerald-600" : "bg-slate-200 text-slate-500"
            )}>
              <item.icon className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs text-slate-500 font-medium mb-0.5">{item.label}</p>
              <p className="text-sm font-semibold text-slate-900">{item.value}</p>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
