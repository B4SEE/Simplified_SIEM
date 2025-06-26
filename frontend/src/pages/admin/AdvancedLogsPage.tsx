import React, { useState } from 'react';
import {
  Box,
  Typography,
  CircularProgress,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField,
  MenuItem,
  Select,
  InputLabel,
  FormControl,
  Pagination,
} from '@mui/material';
import { searchLogs } from '../../services/logsService';
import type { LogEntry } from '../../services/logsService';
import { useAuth } from '../../contexts/AuthContext';

const severities = ['low', 'medium', 'high'];
const LOGS_PER_PAGE = 10;

const AdvancedLogsPage: React.FC = () => {
  const { userId, isAdmin, token } = useAuth();
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    severity: '',
    filterUserId: '',
    eventType: '',
  });
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Fetch logs when page or filters change
  React.useEffect(() => {
    const fetchLogs = async () => {
      if (!token || userId === null) {
	  setError('Authentication required.');
	  setLoading(false);
	  return;
      }
      
      setLoading(true);
      setError(null);
      try {
        const params = {
          ...filters,
          userId: filters.filterUserId ? Number(filters.filterUserId) : undefined,
          limit: LOGS_PER_PAGE,
          offset: (page - 1) * LOGS_PER_PAGE,
        };
        const response = await searchLogs(params, token!, userId, isAdmin ? 'admin' : 'user');
        setLogs(response.logs);
        setTotalPages(Math.ceil(response.total / LOGS_PER_PAGE));
      } catch (err) {
        setError('Failed to fetch logs.');
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, filters, token, userId, isAdmin]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const handleSeverityChange = (event: any) => {
    setFilters(prev => ({ ...prev, severity: event.target.value }));
  };

  const handleSearch = async () => {
    if (!token || userId === null) {
	setError('Authentication required.');
	return;
    }

    setLoading(true);
    setError(null);
    try {
      const params = {
        ...filters,
        userId: filters.filterUserId ? Number(filters.filterUserId) : undefined,
        limit: LOGS_PER_PAGE,
        offset: (page - 1) * LOGS_PER_PAGE,
      };
      const response = await searchLogs(params, token!, userId, isAdmin ? 'admin' : 'user');
      setLogs(response.logs);
      setTotalPages(Math.ceil(response.total / LOGS_PER_PAGE));
    } catch (err) {
      setError('Failed to fetch logs.');
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  return (
    <Box p={3}>
      <Box display="flex" alignItems="center" gap={2} mb={1}>
        <Typography variant="h4" gutterBottom>
          Advanced Logs
        </Typography>
      </Box>
      <Box display="flex" gap={2} flexWrap="wrap" mb={2}>
        <TextField
          label="Start Date"
          name="startDate"
          type="date"
          InputLabelProps={{ shrink: true }}
          value={filters.startDate}
          onChange={handleChange}
        />
        <TextField
          label="End Date"
          name="endDate"
          type="date"
          InputLabelProps={{ shrink: true }}
          value={filters.endDate}
          onChange={handleChange}
        />
        <FormControl>
          <InputLabel>Severity</InputLabel>
          <Select
            label="Severity"
            name="severity"
            value={filters.severity}
            onChange={handleSeverityChange}
            style={{ minWidth: 120 }}
          >
            <MenuItem value="">All</MenuItem>
            {severities.map(sev => (
              <MenuItem key={sev} value={sev}>{sev.toUpperCase()}</MenuItem>
            ))}
          </Select>
        </FormControl>
        <TextField
          label="User ID"
          name="filterUserId"
          value={filters.filterUserId}
          onChange={handleChange}
        />
        <TextField
          label="Event Type"
          name="eventType"
          value={filters.eventType}
          onChange={handleChange}
        />
        <Button variant="contained" onClick={handleSearch} disabled={loading}>
          Search
        </Button>
      </Box>
      {loading ? (
        <CircularProgress />
      ) : error ? (
        <Typography color="error">{error}</Typography>
      ) : (
        <>
          <TableContainer component={Paper} elevation={3}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>User ID</TableCell>
                  <TableCell>Event Type</TableCell>
                  <TableCell>Severity</TableCell>
                  <TableCell>IP Address</TableCell>
                  <TableCell>User Roles</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {logs.map(log => (
                  <TableRow key={log.id}>
                    <TableCell>{log.timestamp}</TableCell>
                    <TableCell>
                      {log.user_ID === null || log.user_ID === undefined ? '-' : log.user_ID}
                      {userId !== null && log.user_ID === userId && (
  <span style={{
    display: 'inline-block',
    background: '#e3f2fd',
    color: '#1976d2',
    fontWeight: 600,
    borderRadius: '12px',
    padding: '2px 10px',
    marginLeft: 8,
    fontSize: '0.85em',
    boxShadow: '0 1px 3px rgba(25, 118, 210, 0.08)'
  }}>
    that's you!
  </span>
)}
                    </TableCell>
                    <TableCell>{log.event_type}</TableCell>
                    <TableCell>{log.severity}</TableCell>
                    <TableCell>{log.ip_address}</TableCell>
                    <TableCell>{Array.isArray(log.roles) && log.roles.length > 0 ? log.roles.join(', ') : '-'}</TableCell>
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
        </>
      )}
    </Box>
  );
};

export default AdvancedLogsPage;
