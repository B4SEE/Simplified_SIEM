import React, { useEffect, useState } from 'react';
import {
  Table, TableBody, TableCell, TableHead, TableRow, Paper
} from '@mui/material';
import {
  StyledButton,
  StyledIconButton,
  StyledSeverityCell,
  StyledTableContainer,
} from './StyledAlertsPage';
import { CheckCircle, Undo } from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import { getAlarms, getAlarmById } from '../../api/alarms';
import { toggleAlarmStatus, deleteAlarm } from '../../api/alarms';


interface Alarm {
  id: number;
  timestamp: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  resolved: boolean;
}

const AlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<Alarm[]>([]);
  const { token, userId} = useAuth();

  useEffect(() => {
    const fetchAlarms = async () => {
      if (!token || !userId) return;

      try {
        const response = await getAlarms(token, userId);
        console.log('Raw alarms data:', JSON.stringify(response.data, null, 2));

        if (response.data.status === 'success') {
          const formatted = response.data.alarms.map((alarm: any) => {
            // Log the raw alarm data
            console.log('Raw alarm data:', {
              id: alarm.id,
              is_active: alarm.is_active,
              description: alarm.description,
              created_at: alarm.created_at,
              severity: alarm.severity
            });
            
            return {
              id: alarm.id,
              timestamp: alarm.created_at,
              description: alarm.description,
              severity: alarm.severity,
              resolved: !alarm.is_active,
            };
          });
          
          console.log('Final formatted alarms:', formatted);
          setAlerts(formatted);
        } else {
          console.error('❌ Failed to fetch alarms: Invalid response format');
        }
      } catch (error) {
        console.error('❌ Failed to fetch alarms:', error);
      }
    };

    fetchAlarms();
  }, [token, userId]);

  const toggleResolved = async (id: number, currentStatus: boolean) => {
    try {
      if (!token || !userId) {
        console.error('❌ Missing token or userId');
        return;
      }

      // Find the current alarm to verify its state
      const currentAlarm = alerts.find(a => a.id === id);
      if (!currentAlarm) {
        console.error('❌ Alarm not found:', id);
        return;
      }

      // Get the current state from the server first
      const currentResponse = await getAlarmById(id, token, userId);
      console.log('Current server state:', currentResponse.data);

      if (currentResponse.data.status !== 'success') {
        throw new Error('Failed to get current alarm state');
      }

      const currentServerState = currentResponse.data.alarm;
      console.log('Current alarm states:', {
        id,
        frontendState: {
          resolved: currentAlarm.resolved,
          is_active: !currentAlarm.resolved
        },
        serverState: {
          is_active: currentServerState.is_active
        }
      });

      // Toggling the current server state
      const newIsActive = !currentServerState.is_active;
      
      console.log('Starting toggle for alarm:', { 
        id, 
        currentServerState: currentServerState.is_active,
        newIsActive,
        currentState: currentServerState.is_active ? 'active' : 'inactive'
      });

      const response = await toggleAlarmStatus(id, token, newIsActive, userId);
      console.log('Full toggle response:', response.data);

      if (response.data.status === 'success' && response.data.alarm) {
        const serverIsActive = response.data.alarm.is_active;
        console.log('✅ New server state:', { 
          serverIsActive,
          shouldBeResolved: !serverIsActive 
        });

        // Update UI with the server response
        setAlerts((prevAlerts) => {
          const updatedAlerts = prevAlerts.map((alert) =>
            alert.id === id 
              ? { 
                  ...alert, 
                  resolved: !serverIsActive,
                  timestamp: response.data.alarm.created_at
                } 
              : alert
          );
          console.log('Updated alerts state:', updatedAlerts);
          return updatedAlerts;
        });

        // Fetch fresh data to ensure UI is in sync
        const freshResponse = await getAlarms(token, userId);
        if (freshResponse.data.status === 'success') {
          const formatted = freshResponse.data.alarms.map((alarm: any) => ({
            id: alarm.id,
            timestamp: alarm.created_at,
            description: alarm.description,
            severity: alarm.severity,
            resolved: !alarm.is_active,
          }));
          console.log('Setting fresh alerts data:', formatted);
          setAlerts(formatted);
        }
      } else {
        console.error('❌ Invalid response format:', response.data);
        throw new Error(response.data.message || 'Invalid response format');
      }
    } catch (error) {
      console.error('❌ Failed to toggle alarm:', error);
    }
  };
  

  return (
    <StyledTableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Timestamp</TableCell>
            <TableCell>Description</TableCell>
            <TableCell>Severity</TableCell>
            <TableCell>Resolved</TableCell>
            <TableCell>Action</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {alerts.map((alert) => (
            <TableRow key={alert.id}>
              <TableCell>{alert.timestamp}</TableCell>
              <TableCell>{alert.description}</TableCell>
              <StyledSeverityCell severity={alert.severity}>
                {alert.severity}
              </StyledSeverityCell>
              <TableCell>{alert.resolved ? '✅ Yes' : '❌ No'}</TableCell>
              <TableCell>
              <StyledIconButton
              onClick={() => toggleResolved(alert.id, alert.resolved)}
              color={alert.resolved ? 'warning' : 'success'}
              >
                {alert.resolved ? <Undo /> : <CheckCircle />}
              </StyledIconButton>
              <StyledButton
              variant="contained"
              color={alert.resolved ? 'warning' : 'success'}
              onClick={() => toggleResolved(alert.id, alert.resolved)}
              >
                {alert.resolved ? 'MARK UNRESOLVED' : 'RESOLVE'}
              </StyledButton>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </StyledTableContainer>
  );
};

export default AlertsPage;
