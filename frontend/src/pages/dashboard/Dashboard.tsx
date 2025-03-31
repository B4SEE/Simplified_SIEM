import React from 'react';
import { Typography } from '@mui/material';
import { mockStatsData } from '../../mock-data/mockStatsData';
import {
  DashboardContainer,
  Title,
  StatBoxContainer,
  StatBox,
  LastLoginText,
} from './StyledDashboard';
import colors from '../../theme/colors';

const Dashboard: React.FC = () => {
  return (
    <DashboardContainer>
      <Title variant='h4' gutterBottom>
        Dashboard
      </Title>

      <StatBoxContainer>
        <StatBox color={colors.totalLogs}>
          <Typography variant='h6'>Total Logs</Typography>
          <Typography variant='h4'>{mockStatsData.totalLogs}</Typography>
        </StatBox>

        <StatBox color={colors.successfulLogins}>
          <Typography variant='h6'>Successful Logins</Typography>
          <Typography variant='h4'>{mockStatsData.successfulLogins}</Typography>
        </StatBox>

        <StatBox color={colors.failedLogins}>
          <Typography variant='h6'>Failed Logins</Typography>
          <Typography variant='h4'>{mockStatsData.failedLogins}</Typography>
        </StatBox>

        <StatBox color={colors.activeAlerts}>
          <Typography variant='h6'>Active Alerts</Typography>
          <Typography variant='h4'>{mockStatsData.alertsCount}</Typography>
        </StatBox>
      </StatBoxContainer>

      <LastLoginText variant='h6'>
        Last Login: {mockStatsData.lastLogin}
      </LastLoginText>
    </DashboardContainer>
  );
};

export default Dashboard;
