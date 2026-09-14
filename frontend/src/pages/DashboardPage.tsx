import React from 'react';
import { useApi } from '../hooks/useApi';
import { useWebSocket } from '../hooks/useWebSocket';
import { api } from '../services/api';
import { MetricCard } from '../components/ui/MetricCard';
import { Users, HardHat, AlertTriangle, Activity, Shield, Cpu } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { RecentEventsTable } from '../components/dashboard/RecentEventsTable';
import { SystemHealthCard } from '../components/dashboard/SystemHealthCard';
import { StatusBadge } from '../components/ui/StatusBadge';

export default function DashboardPage() {
  const { data: systemStatus } = useApi(api.getSystemStatus);
  const { data: events } = useApi(() => api.getEvents({ limit: '10' }));
  const { data: eventStats } = useApi(api.getEventStats);
  const { lastFrame, isConnected } = useWebSocket();

  // Derive real-time metrics from WebSocket frame
  const ppeList = Array.isArray(lastFrame?.ppe_statuses) ? lastFrame.ppe_statuses : [];
  const obstacleList = Array.isArray(lastFrame?.obstacle_warnings) ? lastFrame.obstacle_warnings : [];
  const workerCount = lastFrame?.worker_count ?? ppeList.length;
  const compliantCount = ppeList.filter(
    (w) => w.compliance_status === 'compliant'
  ).length;
  const hazardCount = obstacleList.length;
  const currentFps = lastFrame?.fps ?? 0;
  const ppeCompliance = workerCount > 0
    ? `${Math.round((compliantCount / workerCount) * 100)}%`
    : '—';

  // Overall safety status
  const hasViolations = ppeList.some(
    (w) => w.compliance_status !== 'compliant'
  );
  const overallStatus = !isConnected || !lastFrame
    ? 'inactive'
    : hazardCount > 0 || hasViolations
    ? (hazardCount > 0 ? 'critical' : 'warning')
    : 'safe';

  const statusLabel = overallStatus === 'safe' ? 'All Clear' :
    overallStatus === 'warning' ? 'PPE Issues' :
    overallStatus === 'critical' ? 'Hazards Active' : 'Offline';

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
          <p className="text-slate-500 text-sm mt-0.5">
            Real-time safety intelligence overview
          </p>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge
            status={overallStatus as any}
            label={statusLabel}
            className="text-sm px-3 py-1"
          />
          <div className={`flex items-center gap-1.5 text-sm ${isConnected ? 'text-emerald-600' : 'text-slate-400'}`}>
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-slate-400'}`} />
            {isConnected ? 'Live' : 'Offline'}
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Workers Detected"
          value={workerCount}
          icon={Users}
          iconClassName="text-blue-600 bg-blue-50"
          subtitle={isConnected ? 'Real-time' : 'No stream'}
        />
        <MetricCard
          title="PPE Compliance"
          value={ppeCompliance}
          icon={HardHat}
          iconClassName="text-emerald-600 bg-emerald-50"
          subtitle={workerCount > 0 ? `${compliantCount}/${workerCount} workers` : 'No workers'}
        />
        <MetricCard
          title="Active Hazards"
          value={hazardCount}
          icon={AlertTriangle}
          iconClassName={hazardCount > 0 ? 'text-red-600 bg-red-50' : 'text-amber-600 bg-amber-50'}
          subtitle={hazardCount > 0 ? 'Obstacles detected' : 'No hazards'}
        />
        <MetricCard
          title="System FPS"
          value={currentFps > 0 ? currentFps.toFixed(1) : '—'}
          icon={Activity}
          iconClassName="text-indigo-600 bg-indigo-50"
          subtitle={lastFrame ? `${lastFrame.latency_ms.toFixed(0)}ms latency` : 'Idle'}
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Events */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Recent Safety Events</CardTitle>
              {eventStats && (
                <span className="text-sm text-slate-500">
                  {eventStats.total ?? 0} total events
                </span>
              )}
            </CardHeader>
            <CardContent className="p-0">
              <RecentEventsTable events={events || []} />
            </CardContent>
          </Card>
        </div>

        {/* System Health */}
        <div className="lg:col-span-1">
          <SystemHealthCard status={systemStatus} />
        </div>
      </div>

      {/* Event Summary Cards */}
      {eventStats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="p-5">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-red-50">
                <AlertTriangle className="w-5 h-5 text-red-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">
                  {eventStats.by_type?.ppe_violation ?? 0}
                </p>
                <p className="text-sm text-slate-500">PPE Violations</p>
              </div>
            </div>
          </Card>
          <Card className="p-5">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-amber-50">
                <Shield className="w-5 h-5 text-amber-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">
                  {eventStats.by_type?.obstacle_detected ?? 0}
                </p>
                <p className="text-sm text-slate-500">Obstacle Events</p>
              </div>
            </div>
          </Card>
          <Card className="p-5">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-indigo-50">
                <Cpu className="w-5 h-5 text-indigo-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">
                  {systemStatus?.model_loaded ? 'Online' : 'Offline'}
                </p>
                <p className="text-sm text-slate-500">Detection Engine</p>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
