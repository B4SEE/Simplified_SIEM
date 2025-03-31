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
import {
  SidebarContainer,
  StyledDrawerMobile,
  StyledDrawerDesktop,
} from './StyledSidebar';

const Sidebar: React.FC<{
  mobileOpen: boolean;
  handleDrawerToggle: () => void;
}> = ({ mobileOpen, handleDrawerToggle }) => {
  const drawer = (
    <SidebarContainer>
      <Toolbar />
      <List>
        <ListItemButton>
          <ListItemIcon>
            <DashboardIcon />
          </ListItemIcon>
          <ListItemText primary='Dashboard' />
        </ListItemButton>
        <ListItemButton>
          <ListItemIcon>
            <SecurityIcon />
          </ListItemIcon>
          <ListItemText primary='Security Logs' />
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
