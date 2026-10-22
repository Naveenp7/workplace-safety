import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, MonitorPlay, AlertTriangle, Camera, Shield, Users, Settings, ShieldCheck } from 'lucide-react';
import clsx from 'clsx';
import { useApi } from '../../hooks/useApi';
import { api } from '../../services/api';

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/monitoring', label: 'Live Monitoring', icon: MonitorPlay },
  { to: '/events', label: 'Events', icon: AlertTriangle },
  { to: '/cameras', label: 'Cameras', icon: Camera },
  { to: '/zones', label: 'Safety Zones', icon: Shield },
  { to: '/faces', label: 'Face Recognition', icon: Users },
  { to: '/settings', label: 'Settings', icon: Settings },
];

export default function Sidebar() {
  const { data: status } = useApi(api.getSystemStatus);

  return (
    <div className="w-64 bg-white border-r border-slate-200 flex flex-col h-full flex-shrink-0">
      <div className="h-16 flex items-center px-6 border-b border-slate-100">
        <ShieldCheck className="w-8 h-8 text-indigo-600 mr-2" />
        <span className="text-xl font-bold text-slate-900">SafetyAI</span>
      </div>
      
      <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              clsx(
                'flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-indigo-50 text-indigo-700'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              )
            }
          >
            <item.icon className="w-5 h-5 mr-3 flex-shrink-0" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-slate-100">
        <div className="flex items-center px-3 py-2 bg-slate-50 rounded-lg">
          <div className={clsx("w-2 h-2 rounded-full mr-3", status?.detection_running ? "bg-emerald-500" : "bg-amber-500")} />
          <span className="text-sm font-medium text-slate-700">
            {status?.detection_running ? 'System Active' : 'System Idle'}
          </span>
        </div>
      </div>
    </div>
  );
}
