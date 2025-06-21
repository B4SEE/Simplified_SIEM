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

const AdvancedLogsPage: React.FC = () => {
  const { userId, isAdmin } = useAuth();
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    severity: '',
    userId: '',
    eventType: '',
  });
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Fetch logs when page or filters change
  React.useEffect(() => {
    const fetchLogs = async () => {
      setLoading(true);
      setError(null);
      try {
        const params = {
          ...filters,
          userId: filters.userId ? Number(filters.userId) : undefined,
          limit: 20,
          offset: (page - 1) * 20,
        };
        const response = await searchLogs(params);
        setLogs(response.logs);
        setTotalPages(Math.ceil(response.total / 20));
      } catch (err) {
        setError('Failed to fetch logs.');
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, filters]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const handleSeverityChange = (event: any) => {
    setFilters(prev => ({ ...prev, severity: event.target.value }));
  };

  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        ...filters,
        userId: filters.userId ? Number(filters.userId) : undefined,
        limit: 20,
        offset: (page - 1) * 20,
      };
      const response = await searchLogs(params);
      setLogs(response.logs);
      setTotalPages(Math.ceil(response.total / 20));
    } catch (err) {
      setError('Failed to fetch logs.');
    } finally {
      setLoading(false);
    }
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
          name="userId"
          value={filters.userId}
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
        <TableContainer component={Paper}>
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
          <Box display="flex" justifyContent="center" mt={2}>
            <Pagination
              count={totalPages}
              page={page}
              onChange={(_, value) => setPage(value)}
              color="primary"
            />
          </Box>
        </TableContainer>
      )}
    </Box>
  );
};

export default AdvancedLogsPage;
