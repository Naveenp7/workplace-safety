import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { ErrorBoundary } from './components/ui/ErrorBoundary';
import DashboardPage from './pages/DashboardPage';
import MonitoringPage from './pages/MonitoringPage';
import EventsPage from './pages/EventsPage';
import CamerasPage from './pages/CamerasPage';
import ZonesPage from './pages/ZonesPage';
import SettingsPage from './pages/SettingsPage';

function App() {
  return (
    <ErrorBoundary fallbackTitle="Application Error">
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/monitoring" element={<MonitoringPage />} />
          <Route path="/events" element={<EventsPage />} />
          <Route path="/cameras" element={<CamerasPage />} />
          <Route path="/zones" element={<ZonesPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </ErrorBoundary>
  );
}

export default App;
