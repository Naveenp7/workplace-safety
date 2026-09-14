import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { StatusBadge } from '../ui/StatusBadge';
import { formatRelativeTime } from '../../utils/format';
import { SafetyEvent } from '../../types';

export function RecentEventsTable({ events }: { events: SafetyEvent[] }) {
  if (!events || events.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500">
        No recent events
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm text-left">
        <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-200">
          <tr>
            <th className="px-4 py-3">Time</th>
            <th className="px-4 py-3">Type</th>
            <th className="px-4 py-3">Severity</th>
            <th className="px-4 py-3">Status</th>
          </tr>
        </thead>
        <tbody>
          {events.map((event) => (
            <tr key={event.id} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 font-medium text-slate-900">
                {formatRelativeTime(event.timestamp)}
              </td>
              <td className="px-4 py-3 text-slate-700 capitalize">
                {event.event_type.replace('_', ' ')}
              </td>
              <td className="px-4 py-3">
                <StatusBadge 
                  status={event.severity.toLowerCase() as any} 
                  label={event.severity} 
                />
              </td>
              <td className="px-4 py-3">
                <StatusBadge 
                  status={event.status === 'resolved' ? 'safe' : 'warning'} 
                  label={event.status} 
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
