import React from 'react';
import {
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import SecurityIcon from '@mui/icons-material/Security';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import {
  SidebarContainer,
  StyledDrawerMobile,
  StyledDrawerDesktop,
} from './StyledSidebar';
import { NavLink } from 'react-router-dom';

const Sidebar: React.FC<{
  mobileOpen: boolean;
  handleDrawerToggle: () => void;
}> = ({ mobileOpen, handleDrawerToggle }) => {
  const drawer = (
    <SidebarContainer>
      <Toolbar />
      <List>
        <ListItemButton component={NavLink} to='/dashboard'>
          <ListItemIcon>
            <DashboardIcon />
          </ListItemIcon>
          <ListItemText primary='Dashboard' />
        </ListItemButton>

        <ListItemButton component={NavLink} to='/logs'>
          <ListItemIcon>
            <SecurityIcon />
          </ListItemIcon>
          <ListItemText primary='Logs' />
        </ListItemButton>

        <ListItemButton component={NavLink} to='/alerts'>
          <ListItemIcon>
            <WarningAmberIcon />
          </ListItemIcon>
          <ListItemText primary='Alerts' />
        </ListItemButton>
      </List>
    </SidebarContainer>
  );

  return (
    <>
      {/* Mobile Sidebar */}
      <StyledDrawerMobile
        variant='temporary'
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{ keepMounted: true }}
      >
        {drawer}
      </StyledDrawerMobile>

      {/* Desktop Sidebar */}
      <StyledDrawerDesktop variant='permanent' open>
        {drawer}
      </StyledDrawerDesktop>
    </>
  );
};

export default Sidebar;
