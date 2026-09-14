import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import { EmptyState } from '../components/ui/EmptyState';
import { ZoneEditor } from '../components/zones/ZoneEditor';
import { useApi } from '../hooks/useApi';
import { api } from '../services/api';
import { SafetyZone } from '../types';
import {
  Shield,
  Plus,
  Trash2,
  Eye,
  EyeOff,
  MapPin,
} from 'lucide-react';

export default function ZonesPage() {
  const { data: zones, refetch } = useApi(api.getZones);
  const [isCreating, setIsCreating] = useState(false);
  const [newZone, setNewZone] = useState({
    name: '',
    zone_type: 'walkway',
    detection_threshold: 0.3,
    persistence_frames: 10,
    color: '#3b82f6',
  });
  const [drawnPoints, setDrawnPoints] = useState<number[][] | null>(null);

  const handleSaveZone = async () => {
    if (!drawnPoints || !newZone.name.trim()) return;

    try {
      await api.createZone({
        name: newZone.name,
        zone_type: newZone.zone_type,
        points: drawnPoints.map(([x, y]) => ({ x, y })),
        is_active: true,
        detection_threshold: newZone.detection_threshold,
        persistence_frames: newZone.persistence_frames,
        color: newZone.color,
      });
      setIsCreating(false);
      setDrawnPoints(null);
      setNewZone({ name: '', zone_type: 'walkway', detection_threshold: 0.3, persistence_frames: 10, color: '#3b82f6' });
      await refetch();
    } catch (err) {
      console.error('Failed to create zone:', err);
    }
  };

  const handleDeleteZone = async (id: number) => {
    try {
      await api.deleteZone(id);
      await refetch();
    } catch (err) {
      console.error('Failed to delete zone:', err);
    }
  };

  const handleToggleZone = async (zone: SafetyZone) => {
    try {
      await api.updateZone(zone.id, { ...zone, is_active: !zone.is_active });
      await refetch();
    } catch (err) {
      console.error('Failed to toggle zone:', err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Safety Zones</h1>
          <p className="text-slate-500 text-sm mt-0.5">
            Define walkway and work areas for obstacle detection
          </p>
        </div>
        <button
          onClick={() => setIsCreating(!isCreating)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium bg-indigo-600 text-white hover:bg-indigo-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          {isCreating ? 'Cancel' : 'Create Zone'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Zone Editor */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>
                {isCreating ? 'Draw Zone on Canvas' : 'Zone Editor'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isCreating ? (
                <div className="space-y-4">
                  <ZoneEditor
                    onSave={(points) => setDrawnPoints(points)}
                  />
                  <p className="text-sm text-slate-500">
                    Click and drag on the canvas to draw a rectangular zone. The coordinates will be normalized (0-1).
                  </p>

                  {/* Zone Configuration */}
                  <div className="grid grid-cols-2 gap-4 p-4 bg-slate-50 rounded-lg border border-slate-200">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">
                        Zone Name
                      </label>
                      <input
                        type="text"
                        value={newZone.name}
                        onChange={(e) => setNewZone({ ...newZone, name: e.target.value })}
                        placeholder="e.g., Main Walkway"
                        className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">
                        Zone Type
                      </label>
                      <select
                        value={newZone.zone_type}
                        onChange={(e) => setNewZone({ ...newZone, zone_type: e.target.value })}
                        className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none bg-white"
                      >
                        <option value="walkway">Walkway / Movement Zone</option>
                        <option value="work_area">Work Area</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">
                        Detection Threshold
                      </label>
                      <input
                        type="range"
                        min="0.1"
                        max="0.9"
                        step="0.05"
                        value={newZone.detection_threshold}
                        onChange={(e) => setNewZone({ ...newZone, detection_threshold: parseFloat(e.target.value) })}
                        className="w-full"
                      />
                      <span className="text-xs text-slate-500">{(newZone.detection_threshold * 100).toFixed(0)}% overlap required</span>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">
                        Persistence (frames)
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="100"
                        value={newZone.persistence_frames}
                        onChange={(e) => setNewZone({ ...newZone, persistence_frames: parseInt(e.target.value) || 10 })}
                        className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
                      />
                    </div>
                  </div>

                  <div className="flex justify-end gap-3">
                    <button
                      onClick={() => { setIsCreating(false); setDrawnPoints(null); }}
                      className="px-4 py-2 rounded-lg text-sm font-medium border border-slate-200 text-slate-700 hover:bg-slate-50"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSaveZone}
                      disabled={!drawnPoints || !newZone.name.trim()}
                      className="px-4 py-2 rounded-lg text-sm font-medium bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Save Zone
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-12 text-slate-400">
                  <MapPin className="w-10 h-10 mb-3" />
                  <p className="text-sm">Click "Create Zone" to define a new safety area</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Zone List */}
        <div>
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Configured Zones</CardTitle>
            </CardHeader>
            <CardContent>
              {zones && zones.length > 0 ? (
                <div className="space-y-3">
                  {zones.map((zone: SafetyZone) => (
                    <div
                      key={zone.id}
                      className="p-3 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 transition-colors"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <div
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: zone.color }}
                          />
                          <span className="text-sm font-medium text-slate-900">{zone.name}</span>
                        </div>
                        <StatusBadge
                          status={zone.is_active ? 'safe' : 'inactive'}
                          label={zone.is_active ? 'Active' : 'Disabled'}
                        />
                      </div>
                      <div className="flex items-center gap-2 text-xs text-slate-500 mb-2">
                        <span className="px-1.5 py-0.5 rounded bg-slate-100">{zone.zone_type}</span>
                        <span>Threshold: {(zone.detection_threshold * 100).toFixed(0)}%</span>
                      </div>
                      <div className="flex items-center gap-1 pt-2 border-t border-slate-100">
                        <button
                          onClick={() => handleToggleZone(zone)}
                          className="p-1.5 rounded text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
                          title={zone.is_active ? 'Disable' : 'Enable'}
                        >
                          {zone.is_active ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                        </button>
                        <button
                          onClick={() => handleDeleteZone(zone.id)}
                          className="p-1.5 rounded text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors"
                          title="Delete zone"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-400">
                  <Shield className="w-8 h-8 mx-auto mb-2" />
                  <p className="text-sm">No zones configured yet</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
