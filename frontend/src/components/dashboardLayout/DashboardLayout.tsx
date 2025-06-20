import React, { useState } from 'react';
import {
  Box,
  CssBaseline,
  Toolbar,
  Button,
  Tooltip,
  IconButton,
} from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';
import MenuIcon from '@mui/icons-material/Menu';
import PersonIcon from '@mui/icons-material/Person';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../sidebar/Sidebar';
import {
  AppBarHeader,
  ContentBox,
  StyledAppBar,
  StyledIconButton,
} from './StyledDasboardLayout';
import { useAuth } from '../../contexts/AuthContext';

const DashboardLayout: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { isLoading, isLoggedIn, logout, isAdmin } = useAuth();

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

          <AppBarHeader variant='h5' noWrap>
            MoniLog
          </AppBarHeader>

          {/* ADMIN badge, only for admin users */}
          {isAdmin && (
            <Box
              sx={{
                background: 'linear-gradient(90deg, #8e24aa 0%, #ce93d8 100%)',
                color: 'white',
                fontWeight: 600,
                borderRadius: '16px',
                px: 2,
                py: 0.5,
                fontSize: '1rem',
                boxShadow: '0 1px 4px rgba(142, 36, 170, 0.12)',
                letterSpacing: 1,
                ml: 2
              }}
            >
              ADMIN
            </Box>
          )}

          {!isLoading &&
            (isLoggedIn ? (
              <>
                <Button
                  color='inherit'
                  startIcon={<PersonIcon />}
                  onClick={() => navigate('/profile')}
                >
                  Profile
                </Button>
                <Tooltip title='Log Out'>
                  <IconButton color='inherit' onClick={logout}>
                    <LogoutIcon />
                  </IconButton>
                </Tooltip>
              </>
            ) : (
              <Button
                color='inherit'
                startIcon={<PersonIcon />}
                onClick={() => navigate('/login')}
              >
                Log in
              </Button>
            ))}
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
