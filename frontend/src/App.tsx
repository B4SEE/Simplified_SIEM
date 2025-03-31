import React from 'react';
import DashboardLayout from './components/dashboardLayout/DashboardLayout';
import { Container, Paper, Typography } from '@mui/material';

const App: React.FC = () => {
  return (
    <DashboardLayout>
      <Container>
        <Paper sx={{ p: 3 }}>
          <Typography variant='h4'>Welcome to the Logging Dashboard</Typography>
          <Typography variant='body1'>
            Monitor and analyze authentication logs in real time.
          </Typography>
        </Paper>
      </Container>
    </DashboardLayout>
  );
};

export default App;
