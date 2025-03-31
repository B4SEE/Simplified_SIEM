import React, { useEffect, useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  FormControlLabel,
  Switch,
} from '@mui/material';
import { mockLogsData } from '../../mock-data/mockLogsData';

//temp
const generateRandomLog = () => {
  const users = ['admin', 'user123', 'guest', 'testUser'];
  const events = ['Login Attempt', 'Password Change', 'Logout'];
  const statuses = ['Success', 'Failure'];

  return {
    id: Date.now(),
    timestamp: new Date().toISOString().replace('T', ' ').split('.')[0],
    user: users[Math.floor(Math.random() * users.length)],
    event: events[Math.floor(Math.random() * events.length)],
    status: statuses[Math.floor(Math.random() * statuses.length)],
    alert: Math.random() > 0.7,
  };
};

const Logs: React.FC = () => {
  const [logs, setLogs] = useState(mockLogsData);
  const [filterAlerts, setFilterAlerts] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setLogs((prevLogs) => [generateRandomLog(), ...prevLogs]);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const filteredLogs = filterAlerts ? logs.filter((log) => log.alert) : logs;

  return (
    <TableContainer component={Paper} sx={{ padding: 2 }}>
      <FormControlLabel
        control={
          <Switch
            checked={filterAlerts}
            onChange={() => setFilterAlerts(!filterAlerts)}
          />
        }
        label='Show Only Alerts'
      />
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Timestamp</TableCell>
            <TableCell>User</TableCell>
            <TableCell>Event</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Alert</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {filteredLogs.map((log) => (
            <TableRow key={log.id}>
              <TableCell>{log.timestamp}</TableCell>
              <TableCell>{log.user}</TableCell>
              <TableCell>{log.event}</TableCell>
              <TableCell
                style={{ color: log.status === 'Success' ? 'green' : 'red' }}
              >
                {log.status}
              </TableCell>
              <TableCell>{log.alert ? '🚨 Yes' : 'No'}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default Logs;
