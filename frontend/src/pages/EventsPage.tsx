import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { EmptyState } from '../components/ui/EmptyState';
import { AlertTriangle } from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { api } from '../services/api';
import { RecentEventsTable } from '../components/dashboard/RecentEventsTable';

export default function EventsPage() {
  const { data: events, loading } = useApi(() => api.getEvents());

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Safety Events</h1>
        <p className="text-slate-500 mt-1">Review and manage recorded incidents and hazards.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Event Log</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {loading ? (
            <div className="p-8 text-center text-slate-500">Loading events...</div>
          ) : events && events.length > 0 ? (
            <RecentEventsTable events={events} />
          ) : (
            <EmptyState 
              icon={AlertTriangle}
              title="No Events Found"
              description="There are currently no safety events recorded in the system."
            />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
