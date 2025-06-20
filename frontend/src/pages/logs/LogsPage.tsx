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
  CircularProgress,
  Typography,
  Pagination,
  Box,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import { getRecentLogs } from '../../services/logsService';
import type { LogEntry } from '../../services/logsService';
import type { GetRecentLogsResult } from '../../services/logsService';

const LOGS_PER_PAGE = 10;

const LogsPage: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterAlerts, setFilterAlerts] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalLogs, setTotalLogs] = useState(0);
  const [eventTypeFilter, setEventTypeFilter] = useState<string>('all');
  const [uniqueEventTypes, setUniqueEventTypes] = useState<string[]>([]);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const severity = filterAlerts ? 'high' : undefined;
      const offset = (page - 1) * LOGS_PER_PAGE;
      const { logs, total }: GetRecentLogsResult = await getRecentLogs(
        LOGS_PER_PAGE,
        offset,
        eventTypeFilter,
        severity
      );
      setLogs(logs);
      setTotalLogs(total);
      setTotalPages(Math.max(1, Math.ceil(total / LOGS_PER_PAGE)));
      setError(null);

      // Fetch all event types for filter dropdown (optional: cache this)
      if (page === 1 && !filterAlerts && eventTypeFilter === 'all') {
        // Fetch a larger sample to get event types
        const allLogsResult = await getRecentLogs(100, 0);
        setUniqueEventTypes(Array.from(new Set(allLogsResult.logs.map(l => l.event_type))));
      }
    } catch (err) {
      console.error('Failed to fetch logs:', err);
      setError('Failed to load logs. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
    // Only refetch on page/filter change, not interval (optional)
    // const interval = setInterval(fetchLogs, 5000);
    // return () => clearInterval(interval);
  }, [page, filterAlerts, eventTypeFilter]);

  if (loading && logs.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="400px">
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  return (
    <TableContainer component={Paper} sx={{ padding: 2 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <FormControlLabel
          control={
            <Switch
              checked={filterAlerts}
              onChange={() => { setPage(1); setFilterAlerts(!filterAlerts); }}
            />
          }
          label='Show Only High Severity'
        />
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Event Type</InputLabel>
          <Select
            value={eventTypeFilter}
            onChange={(e) => { setPage(1); setEventTypeFilter(e.target.value); }}
            label="Event Type"
          >
            <MenuItem value="all">All Events</MenuItem>
            {uniqueEventTypes.map(type => (
              <MenuItem key={type} value={type}>{type}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

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
                  color: log.severity === 'high' ? 'red' :
                         log.severity === 'medium' ? 'orange' : 'green'
                }}
              >
                {log.severity?.toUpperCase() || 'LOW'}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <Box display="flex" justifyContent="center" mt={2}>
        <Pagination
          count={totalPages}
          page={page}
          onChange={(_, value) => setPage(value)}
          color="primary"
        />
      </Box>
    </TableContainer>
  );
};

export default LogsPage;
