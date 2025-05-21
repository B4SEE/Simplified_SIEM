import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import DashboardLayout from '../components/dashboardLayout/DashboardLayout';
import AlertsPage from '../pages/alerts/AlertsPage';
import DashboardPage from '../pages/dashboard/DashboardPage';
import LoginPage from '../pages/login/LoginPage';
import LogsPage from '../pages/logs/LogsPage';
import RegistrationPage from '../pages/registration/RegistrationPage';
import UserPage from '../pages/user/UserPage';
import PrivateRoute from './PrivateRoute';

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path='/login' element={<LoginPage />} />
      <Route path='/register' element={<RegistrationPage />} />

      <Route
        path='/dashboard'
        element={
          <PrivateRoute>
            <DashboardLayout>
              <DashboardPage />
            </DashboardLayout>
          </PrivateRoute>
        }
      />
      <Route
        path='/logs'
        element={
          <PrivateRoute>
            <DashboardLayout>
              <LogsPage />
            </DashboardLayout>
          </PrivateRoute>
        }
      />
      <Route
        path='/alerts'
        element={
          <PrivateRoute>
            <DashboardLayout>
              <AlertsPage />
            </DashboardLayout>
          </PrivateRoute>
        }
      />
      <Route
        path='/profile'
        element={
          <PrivateRoute>
            <DashboardLayout>
              <UserPage />
            </DashboardLayout>
          </PrivateRoute>
        }
      />

      <Route path='*' element={<Navigate to='/dashboard' replace />} />
    </Routes>
  );
};

export default AppRoutes;
