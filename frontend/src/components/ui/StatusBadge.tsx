import React from 'react';
import clsx from 'clsx';

interface StatusBadgeProps {
  status: string;
  label?: string;
  className?: string;
}

const styleMap: Record<string, string> = {
  safe: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  compliant: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  low: 'bg-blue-100 text-blue-800 border-blue-200',
  info: 'bg-blue-100 text-blue-800 border-blue-200',
  warning: 'bg-amber-100 text-amber-800 border-amber-200',
  medium: 'bg-amber-100 text-amber-800 border-amber-200',
  helmet_missing: 'bg-amber-100 text-amber-800 border-amber-200',
  vest_missing: 'bg-amber-100 text-amber-800 border-amber-200',
  high: 'bg-red-100 text-red-800 border-red-200',
  critical: 'bg-red-100 text-red-800 border-red-200',
  violation: 'bg-red-100 text-red-800 border-red-200',
  active: 'bg-blue-100 text-blue-800 border-blue-200',
  resolved: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  acknowledged: 'bg-slate-100 text-slate-800 border-slate-200',
  inactive: 'bg-slate-100 text-slate-600 border-slate-200',
};

const dotMap: Record<string, string> = {
  safe: 'bg-emerald-500',
  compliant: 'bg-emerald-500',
  low: 'bg-blue-500',
  info: 'bg-blue-500',
  warning: 'bg-amber-500',
  medium: 'bg-amber-500',
  helmet_missing: 'bg-amber-500',
  vest_missing: 'bg-amber-500',
  high: 'bg-red-500',
  critical: 'bg-red-500',
  violation: 'bg-red-500',
  active: 'bg-blue-500',
  resolved: 'bg-emerald-500',
  acknowledged: 'bg-slate-400',
  inactive: 'bg-slate-400',
};

export function StatusBadge({ status, label, className }: StatusBadgeProps) {
  const normalizedStatus = status?.toLowerCase() || 'inactive';
  const style = styleMap[normalizedStatus] || styleMap.inactive;
  const dot = dotMap[normalizedStatus] || dotMap.inactive;

  return (
    <span className={clsx(
      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border',
      style,
      className
    )}>
      <span className={clsx('w-1.5 h-1.5 rounded-full mr-1.5', dot)} />
      {label || status?.charAt(0).toUpperCase() + status?.slice(1).replace('_', ' ') || 'Unknown'}
    </span>
  );
}
