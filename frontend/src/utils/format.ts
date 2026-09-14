import { formatDistanceToNow, format } from 'date-fns';

export function formatTimestamp(ts: string) {
  if (!ts) return '';
  return format(new Date(ts), 'MMM d, yyyy HH:mm:ss');
}

export function formatRelativeTime(ts: string) {
  if (!ts) return '';
  return formatDistanceToNow(new Date(ts), { addSuffix: true });
}

export function formatFPS(fps: number) {
  return Math.round(fps);
}

export function formatConfidence(conf: number) {
  return `${Math.round(conf * 100)}%`;
}

export function formatLatency(ms: number) {
  return `${Math.round(ms)} ms`;
}

export function getSeverityColor(severity: string) {
  switch (severity.toLowerCase()) {
    case 'critical': return 'critical';
    case 'warning': return 'warning';
    case 'info': return 'info';
    default: return 'inactive';
  }
}

export function getStatusColor(status: string) {
  switch (status.toLowerCase()) {
    case 'resolved': return 'safe';
    case 'active': return 'critical';
    case 'investigating': return 'warning';
    default: return 'inactive';
  }
}
