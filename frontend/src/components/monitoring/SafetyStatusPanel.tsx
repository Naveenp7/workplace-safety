import React from 'react';
import { DetectionFrame } from '../../types';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { HardHat, AlertTriangle, Users } from 'lucide-react';
import { StatusBadge } from '../ui/StatusBadge';

export function SafetyStatusPanel({ frame }: { frame: DetectionFrame | null }) {
  if (!frame) {
    return (
      <Card className="h-full">
        <CardHeader><CardTitle>Live Safety Status</CardTitle></CardHeader>
        <CardContent className="text-slate-500 text-sm">No active video stream.</CardContent>
      </Card>
    );
  }

  const ppeStatuses = Array.isArray(frame.ppe_statuses) ? frame.ppe_statuses : [];
  const obstacleWarnings = Array.isArray(frame.obstacle_warnings) ? frame.obstacle_warnings : [];
  const faceRecognitions = Array.isArray(frame.face_recognitions) ? frame.face_recognitions : [];

  const compliantWorkers = ppeStatuses.filter(w => w.compliance_status === 'compliant').length;
  const totalWorkers = frame.worker_count ?? ppeStatuses.length;
  const hasViolations = totalWorkers > 0 && compliantWorkers < totalWorkers;
  const hasObstacles = obstacleWarnings.length > 0;

  let overallStatus: 'safe' | 'warning' | 'critical' = 'safe';
  if (hasViolations) overallStatus = 'warning';
  if (hasObstacles) overallStatus = 'critical';

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Live Safety Status</CardTitle>
        <StatusBadge status={overallStatus} label={overallStatus.toUpperCase()} />
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto space-y-6">
        
        <div>
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-semibold text-slate-700 flex items-center">
              <HardHat className="w-4 h-4 mr-2 text-slate-400" />
              PPE Compliance
            </h4>
            <span className="text-sm font-medium">{compliantWorkers} / {totalWorkers}</span>
          </div>
          <div className="space-y-3 mt-4">
            {ppeStatuses.map((w, idx) => (
              <div key={w.worker_id ?? idx} className="p-3 bg-slate-50 rounded-lg border border-slate-100 flex justify-between items-center">
                <span className="text-sm font-medium">Worker #{w.worker_id ?? idx}</span>
                <StatusBadge 
                  status={w.compliance_status === 'compliant' ? 'safe' : (w.has_helmet ? 'warning' : 'violation')} 
                  label={
                    w.compliance_status === 'compliant' ? 'Compliant' :
                    w.compliance_status === 'vest_missing' ? 'Helmet OK (Vest Missing)' :
                    w.compliance_status === 'helmet_missing' ? 'Helmet Missing' : 'No Helmet / No Vest'
                  } 
                />
              </div>
            ))}
            {totalWorkers === 0 && <p className="text-sm text-slate-500">No workers detected.</p>}
          </div>
        </div>

        <div className="pt-4 border-t border-slate-100">
          <h4 className="text-sm font-semibold text-slate-700 flex items-center mb-4">
            <AlertTriangle className="w-4 h-4 mr-2 text-slate-400" />
            Hazards & Obstacles
          </h4>
          <div className="space-y-3">
            {obstacleWarnings.map((obs, idx) => (
              <div key={idx} className="p-3 bg-amber-50 rounded-lg border border-amber-100">
                <p className="text-sm font-medium text-amber-900">{obs.object_class}</p>
                <p className="text-xs text-amber-700 mt-1">In zone: {obs.zone_name || 'Safety Zone'}</p>
              </div>
            ))}
            {obstacleWarnings.length === 0 && (
              <p className="text-sm text-slate-500">No hazards detected.</p>
            )}
          </div>
        </div>

        {/* Face Recognition Section */}
        <div className="pt-4 border-t border-slate-100">
          <h4 className="text-sm font-semibold text-slate-700 flex items-center mb-4">
            <Users className="w-4 h-4 mr-2 text-violet-500" />
            Face Recognition
          </h4>
          <div className="space-y-3">
            {faceRecognitions.filter(f => f.name !== 'Unknown').map((face, idx) => (
              <div key={idx} className="p-3 bg-violet-50 rounded-lg border border-violet-100 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {(face.trained_thumbnail_b64 || face.face_crop_b64) && (
                    <img
                      src={`data:image/jpeg;base64,${face.trained_thumbnail_b64 || face.face_crop_b64}`}
                      alt={face.name}
                      className="w-10 h-10 rounded-full object-cover border-2 border-violet-400 shadow-sm shrink-0"
                    />
                  )}
                  <span className="text-sm font-medium text-violet-900">{face.name}</span>
                </div>
                <span className="text-xs font-semibold bg-violet-600 text-white px-2 py-0.5 rounded-full">
                  {Math.round(face.confidence * 100)}%
                </span>
              </div>
            ))}
            {faceRecognitions.filter(f => f.name === 'Unknown').length > 0 && (
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                <p className="text-sm text-slate-500">
                  {faceRecognitions.filter(f => f.name === 'Unknown').length} unknown face(s) detected
                </p>
              </div>
            )}
            {faceRecognitions.length === 0 && (
              <p className="text-sm text-slate-500">No faces recognized.</p>
            )}
          </div>
        </div>

      </CardContent>
    </Card>
  );
}
