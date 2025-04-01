import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Paper,
  Button,
} from '@mui/material';
import { mockAlertsData } from '../../mock-data/mockAlertsData';
import {
  StyledButton,
  StyledIconButton,
  StyledSeverityCell,
  StyledTableContainer,
} from './StyledAlertsPage';
import { CheckCircle, Undo } from '@mui/icons-material';

const AlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState(mockAlertsData);

  const toggleResolved = (id: number) => {
    setAlerts((prevAlerts) =>
      prevAlerts.map((alert) =>
        alert.id === id ? { ...alert, resolved: !alert.resolved } : alert
      )
    );
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
                  onClick={() => toggleResolved(alert.id)}
                  color={alert.resolved ? 'warning' : 'success'}
                >
                  {alert.resolved ? <Undo /> : <CheckCircle />}
                </StyledIconButton>
                <StyledButton
                  variant='contained'
                  color={alert.resolved ? 'warning' : 'success'}
                  onClick={() => toggleResolved(alert.id)}
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
