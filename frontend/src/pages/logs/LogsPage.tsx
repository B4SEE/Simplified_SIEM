import React, { useEffect, useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Box,
  Typography,
  Switch,
  FormControlLabel,
  Pagination,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import { getLogs, LogEntry } from '../../services/logsService';
import { useAuth } from '../../contexts/AuthContext';
import { SelectChangeEvent } from '@mui/material/Select';

const LOGS_PER_PAGE = 10;

const LogsPage: React.FC = () => {
  const { token, userId, roles } = useAuth();
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterAlerts, setFilterAlerts] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalLogs, setTotalLogs] = useState(0);
  const [eventTypeFilter, setEventTypeFilter] = useState<string>('all');
  const [uniqueEventTypes, setUniqueEventTypes] = useState<string[]>([]);

  // Determine user role for API calls
  const userRole = roles.includes('admin') ? 'admin' : 'user';

  const fetchLogs = async () => {
    if (!token) return;
    
    try {
      setLoading(true);
      const offset = (page - 1) * LOGS_PER_PAGE;
      const severity = filterAlerts ? 'high' : undefined;

      const response = await getLogs(
        token,
        userId ?? undefined,
        userRole,
        LOGS_PER_PAGE,
        offset,
        eventTypeFilter,
        severity
      );
      
      setLogs(response.logs);
      setTotalLogs(response.total);
      setTotalPages(Math.max(1, Math.ceil(response.total / LOGS_PER_PAGE)));

      // Fetch unique event types for dropdown if not already loaded
      if (uniqueEventTypes.length === 0) {
        const allLogsResponse = await getLogs(
          token,
          userId ?? undefined,
          userRole,
          1000,
          0
        );
        setUniqueEventTypes(
          Array.from(new Set(allLogsResponse.logs.map((log: LogEntry) => log.event_type))) as string[]
        );
      }
      
      setError(null);
    } catch (err) {
      console.error('Failed to fetch logs:', err);
      setError('Failed to load logs. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchLogs();
    }
  }, [page, token, eventTypeFilter, filterAlerts, userId, userRole]);

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  const handleEventTypeChange = (e: SelectChangeEvent<string>) => {
    setPage(1);
    setEventTypeFilter(e.target.value as string);
  };

  const handleSeverityChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPage(1);
    setFilterAlerts(e.target.checked);
  };

  if (loading && logs.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Typography color="error" align="center">
          {error}
        </Typography>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h4">System Logs</Typography>
        <Box display="flex" alignItems="center">
          <FormControlLabel
            control={
              <Switch
                checked={filterAlerts}
                onChange={handleSeverityChange}
                name="filterAlerts"
                color="primary"
              />
            }
            label="Show Only High Severity"
          />
          <FormControl variant="outlined" style={{ minWidth: 150, marginLeft: 16 }}>
            <InputLabel>Event Type</InputLabel>
            <Select
              value={eventTypeFilter}
              onChange={handleEventTypeChange}
              label="Event Type"
            >
              <MenuItem value="all">All Events</MenuItem>
              {uniqueEventTypes.map((type) => (
                <MenuItem key={type} value={type}>
                  {type}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
      </Box>
      <TableContainer component={Paper} elevation={3}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Timestamp</TableCell>
              <TableCell>User ID</TableCell>
              <TableCell>Event Type</TableCell>
              <TableCell>IP Address</TableCell>
              <TableCell>Severity</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {logs.map((log) => (
              <TableRow key={log.id}>
                <TableCell>{new Date(log.timestamp).toLocaleString()}</TableCell>
                <TableCell>{log.user_ID}</TableCell>
                <TableCell>{log.event_type}</TableCell>
                <TableCell>{log.ip_address}</TableCell>
                <TableCell
                  style={{
                    color: log.severity === 'high' ? 'red' : log.severity === 'medium' ? 'orange' : 'green',
                    fontWeight: 'bold',
                  }}
                >
                  {log.severity?.toUpperCase() || 'LOW'}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Box display="flex" justifyContent="center" mt={2}>
        <Pagination
          count={totalPages}
          page={page}
          onChange={handlePageChange}
          color="primary"
        />
      </Box>
    </Box>
  );
};

export default LogsPage;
