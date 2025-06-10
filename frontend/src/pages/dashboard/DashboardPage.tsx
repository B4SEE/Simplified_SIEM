import React, { useEffect, useState } from 'react';
import { Typography, CircularProgress } from '@mui/material';
import {
  DashboardContainer,
  Title,
  StatBoxContainer,
  StatBox,
  LastLoginText,
} from './StyledDashboardPage';
import colors from '../../theme/colors';
import LogsChart from '../../components/logsChart/LogsChart';
import { fetchLogStats } from '../../services/logsService';
import { getLogsGraphData } from '../../services/logsService';
import type { LogStats, LogsGraphData } from '../../services/logsService';

const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<LogStats | null>(null);
  const [graphData, setGraphData] = useState<LogsGraphData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [statsData, graphData] = await Promise.all([
          fetchLogStats(),
          getLogsGraphData(7)
        ]);
        setStats(statsData);
        setGraphData(graphData);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        setError('Failed to load dashboard data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading && !stats) {
    return (
      <DashboardContainer>
        <CircularProgress />
      </DashboardContainer>
    );
  }

  if (error) {
    return (
      <DashboardContainer>
        <Typography color="error">{error}</Typography>
      </DashboardContainer>
    );
  }

  return (
    <DashboardContainer>
      <Title variant='h4' gutterBottom>
        Dashboard
      </Title>

      <StatBoxContainer>
        <StatBox color={colors.totalLogs}>
          <Typography variant='h6'>Total Logs</Typography>
          <Typography variant='h4'>{stats?.totalLogs || 0}</Typography>
        </StatBox>

        <StatBox color={colors.successfulLogins}>
          <Typography variant='h6'>Successful Logins</Typography>
          <Typography variant='h4'>{stats?.successfulLogins || 0}</Typography>
        </StatBox>

        <StatBox color={colors.failedLogins}>
          <Typography variant='h6'>Failed Logins</Typography>
          <Typography variant='h4'>{stats?.failedLogins || 0}</Typography>
        </StatBox>

        <StatBox color={colors.activeAlerts}>
          <Typography variant='h6'>Active Alerts</Typography>
          <Typography variant='h4'>{stats?.alertsCount || 0}</Typography>
        </StatBox>
      </StatBoxContainer>

      <Typography variant='h6' sx={{ marginTop: 4 }}>
        Login Activity (Last 7 Days)
      </Typography>

      <LogsChart data={graphData} />

      <LastLoginText variant='h6'>
        Last Login: {stats?.lastLogin || 'No recent logins'}
      </LastLoginText>
    </DashboardContainer>
  );
};

export default DashboardPage;
