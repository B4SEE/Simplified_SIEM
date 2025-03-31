import { styled } from '@mui/material/styles';
import { Drawer, Box } from '@mui/material';
import { SIDEBAR_WIDTH } from '../../consts/sidebarConsts';

export const StyledDrawerMobile = styled(Drawer)(({ theme }) => ({
  display: 'block',
  [theme.breakpoints.up('sm')]: {
    display: 'none',
  },
  '& .MuiDrawer-paper': {
    width: SIDEBAR_WIDTH,
  },
}));

export const StyledDrawerDesktop = styled(Drawer)(({ theme }) => ({
  display: 'none',
  [theme.breakpoints.up('sm')]: {
    display: 'block',
  },
  '& .MuiDrawer-paper': {
    width: SIDEBAR_WIDTH,
  },
}));

export const SidebarContainer = styled(Box)({
  width: SIDEBAR_WIDTH,
});
