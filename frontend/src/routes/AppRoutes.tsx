import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from '../pages/login/Login';
import Dashboard from '../pages/dashboard/Dashboard';
import Logs from '../pages/logs/Logs';
import Alerts from '../pages/alerts/Alerts';
import DashboardLayout from '../components/dashboardLayout/DashboardLayout';

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path='/login' element={<Login />} />

      <Route
        path='/dashboard'
        element={
          <DashboardLayout>
            <Dashboard />
          </DashboardLayout>
        }
      />
      <Route
        path='/logs'
        element={
          <DashboardLayout>
            <Logs />
          </DashboardLayout>
        }
      />
      <Route
        path='/alerts'
        element={
          <DashboardLayout>
            <Alerts />
          </DashboardLayout>
        }
      />

      <Route path='*' element={<Navigate to='/dashboard' replace />} />
    </Routes>
  );
};

export default AppRoutes;
