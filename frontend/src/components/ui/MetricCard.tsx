import React from 'react';
import { Card } from './Card';
import { LucideIcon } from 'lucide-react';
import clsx from 'clsx';

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  subtitle?: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  iconClassName?: string;
}

export function MetricCard({ title, value, icon: Icon, subtitle, trend, iconClassName }: MetricCardProps) {
  return (
    <Card className="p-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500 mb-1">{title}</p>
          <h3 className="text-3xl font-bold text-slate-900">{value}</h3>
          
          {(subtitle || trend) && (
            <div className="mt-2 flex items-center text-sm">
              {trend && (
                <span className={clsx(
                  "font-medium mr-2",
                  trend.isPositive ? "text-emerald-600" : "text-red-600"
                )}>
                  {trend.isPositive ? '+' : '-'}{Math.abs(trend.value)}%
                </span>
              )}
              {subtitle && <span className="text-slate-500">{subtitle}</span>}
            </div>
          )}
        </div>
        <div className={clsx("p-3 rounded-xl bg-slate-50", iconClassName)}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </Card>
  );
}
