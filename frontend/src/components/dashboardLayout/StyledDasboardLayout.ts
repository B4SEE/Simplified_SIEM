import { styled } from '@mui/material/styles';
import { Box, AppBar, IconButton } from '@mui/material';
import { SIDEBAR_WIDTH } from '../../consts/sidebarConsts';

export const StyledAppBar = styled(AppBar)(({ theme }) => ({
  zIndex: theme.zIndex.drawer + 1,
}));

export const ContentBox = styled(Box)<{ component?: React.ElementType }>(
  ({ theme }) => ({
    flexGrow: 1,
    padding: theme.spacing(3),
    marginLeft: `${SIDEBAR_WIDTH}px`,
    transition: 'margin-left 0.3s',
    width: '100%',
    [theme.breakpoints.down('sm')]: {
      marginLeft: 0,
    },
  })
);

export const StyledIconButton = styled(IconButton)(({ theme }) => ({
  [theme.breakpoints.down('sm')]: {
    display: 'inline-flex',
  },
  [theme.breakpoints.up('sm')]: {
    display: 'none',
  },
}));
