import React, { useState } from 'react';
import { Box, CssBaseline, Toolbar, Typography } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
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
          <Typography variant='h6' noWrap>
            Logging Dashboard
          </Typography>
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
