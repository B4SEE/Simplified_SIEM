import { styled } from '@mui/material/styles';
import { TableContainer, TableCell, Button, IconButton } from '@mui/material';

interface SeverityCellProps {
  severity: string;
}

export const StyledTableContainer = styled(TableContainer)<{
  component?: React.ElementType;
}>(({ theme }) => ({
  padding: theme.spacing(2),
}));

export const StyledSeverityCell = styled(TableCell)<SeverityCellProps>(
  ({ severity }) => ({
    color: severity === 'High' ? 'red' : 'orange',
  })
);

export const StyledButton = styled(Button)(({ theme }) => ({
  minWidth: '170px',
  textTransform: 'none',
  display: 'none',
  [theme.breakpoints.up('md')]: {
    display: 'inline-flex',
  },
}));

export const StyledIconButton = styled(IconButton)(({ theme }) => ({
  display: 'flex',
  [theme.breakpoints.up('md')]: {
    display: 'none',
  },
}));
