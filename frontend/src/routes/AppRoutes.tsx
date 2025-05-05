import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import DashboardLayout from '../components/dashboardLayout/DashboardLayout';
import AlertsPage from '../pages/alerts/AlertsPage';
import DashboardPage from '../pages/dashboard/DashboardPage';
import LoginPage from '../pages/login/LoginPage';
import LogsPage from '../pages/logs/LogsPage';
import RegistrationPage from '../pages/registration/RegistrationPage';
import UserPage from '../pages/user/UserPage';

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path='/login' element={<LoginPage />} />
      <Route path='/register' element={<RegistrationPage />} />

      <Route
        path='/dashboard'
        element={
          <DashboardLayout>
            <DashboardPage />
          </DashboardLayout>
        }
      />
      <Route
        path='/logs'
        element={
          <DashboardLayout>
            <LogsPage />
          </DashboardLayout>
        }
      />
      <Route
        path='/alerts'
        element={
          <DashboardLayout>
            <AlertsPage />
          </DashboardLayout>
        }
      />
      <Route
        path='/user'
        element={
          <DashboardLayout>
            <UserPage />
          </DashboardLayout>
        }
      />

      <Route path='*' element={<Navigate to='/dashboard' replace />} />
    </Routes>
  );
};

export default AppRoutes;
