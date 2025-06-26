import React, { useEffect, useState } from 'react';
import {
  Table, TableBody, TableCell, TableHead, TableRow, Paper,
  CircularProgress, Typography, Box, Alert, Snackbar
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

interface SnackbarState {
  open: boolean;
  message: string;
  severity: 'success' | 'error' | 'info' | 'warning';
}

const AlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<Alarm[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [snackbar, setSnackbar] = useState<SnackbarState>({
    open: false,
    message: '',
    severity: 'info'
  });
  const { token, userId } = useAuth();

  const showSnackbar = (message: string, severity: SnackbarState['severity']) => {
    setSnackbar({
      open: true,
      message,
      severity
    });
  };

  const handleSnackbarClose = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  const fetchAlarms = async () => {
    if (!token || !userId) {
      setError('Authentication required');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const response = await getAlarms(token, userId);
      console.log('Raw alarms data:', JSON.stringify(response.data, null, 2));

      if (response.data.status === 'success') {
        const formatted = response.data.alarms.map((alarm: any) => ({
          id: alarm.id,
          timestamp: alarm.created_at,
          description: alarm.description,
          severity: alarm.severity,
          resolved: !alarm.is_active,
        }));
        
        console.log('Final formatted alarms:', formatted);
        setAlerts(formatted);
        setError(null);
      } else {
        throw new Error('Invalid response format');
      }
    } catch (error) {
      console.error('❌ Failed to fetch alarms:', error);
      setError('Failed to load alarms. Please try again later.');
      showSnackbar('Failed to load alarms', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlarms();
    const interval = setInterval(fetchAlarms, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [token, userId]);

  const toggleResolved = async (id: number, currentStatus: boolean) => {
    try {
      if (!token || !userId) {
        showSnackbar('Authentication required', 'error');
        return;
      }

      // Find the current alarm to verify its state
      const currentAlarm = alerts.find(a => a.id === id);
      if (!currentAlarm) {
        showSnackbar('Alarm not found', 'error');
        return;
      }

      // Get the current state from the server first
      const currentResponse = await getAlarmById(id, token, userId);
      console.log('Current server state:', currentResponse.data);

      if (currentResponse.data.status !== 'success') {
        throw new Error('Failed to get current alarm state');
      }

      const currentServerState = currentResponse.data.alarm;
      const newIsActive = !currentServerState.is_active;
      
      console.log('Starting toggle for alarm:', { 
        id, 
        currentServerState: currentServerState.is_active,
        newIsActive
      });

      // Optimistically update UI
      setAlerts(prevAlerts => 
        prevAlerts.map(alert =>
          alert.id === id ? { ...alert, resolved: !alert.resolved } : alert
        )
      );

      const response = await toggleAlarmStatus(id, token, newIsActive, userId);
      console.log('Full toggle response:', response.data);

      if (response.data.status === 'success' && response.data.alarm) {
        const serverIsActive = response.data.alarm.is_active;
        showSnackbar(
          `Alarm ${serverIsActive ? 'activated' : 'resolved'} successfully`,
          'success'
        );
        await fetchAlarms(); // Refresh data
      } else {
        throw new Error(response.data.message || 'Invalid response format');
      }
    } catch (error) {
      console.error('❌ Failed to toggle alarm:', error);
      showSnackbar('Failed to update alarm status', 'error');
      await fetchAlarms(); // Refresh to revert optimistic update
    }
  };

  if (loading && alerts.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error && alerts.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="400px">
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  return (
    <>
      <StyledTableContainer component={Paper}>
        {loading && (
          <Box display="flex" justifyContent="center" p={1}>
            <CircularProgress size={20} />
          </Box>
        )}
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
                <TableCell>{new Date(alert.timestamp).toLocaleString()}</TableCell>
                <TableCell>{alert.description}</TableCell>
                <StyledSeverityCell severity={alert.severity}>
                  {alert.severity.toUpperCase()}
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

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={handleSnackbarClose}
          severity={snackbar.severity}
          variant="filled"
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </>
  );
};

export default AlertsPage;
