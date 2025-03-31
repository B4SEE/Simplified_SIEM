import React, { useState } from 'react';
import { Box, CssBaseline, Toolbar, Typography, Button } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import PersonIcon from '@mui/icons-material/Person';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../sidebar/Sidebar';
import {
  ContentBox,
  StyledAppBar,
  StyledIconButton,
} from './StyledDasboardLayout';

const DashboardLayout: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />

      {/* AppBar */}
      <StyledAppBar position='fixed'>
        <Toolbar>
          <StyledIconButton
            color='inherit'
            aria-label='open drawer'
            edge='start'
            onClick={handleDrawerToggle}
          >
            <MenuIcon />
          </StyledIconButton>

          <Typography variant='h6' noWrap sx={{ flexGrow: 1 }}>
            Logging Dashboard
          </Typography>

          <Button
            color='inherit'
            startIcon={<PersonIcon />}
            onClick={() => navigate('/login')}
          >
            Log in
          </Button>
        </Toolbar>
      </StyledAppBar>

      {/* Sidebar */}
      <Sidebar
        mobileOpen={mobileOpen}
        handleDrawerToggle={handleDrawerToggle}
      />

      {/* Page Content */}
      <ContentBox component='main'>
        <Toolbar />
        {children}
      </ContentBox>
    </Box>
  );
};

export default DashboardLayout;
