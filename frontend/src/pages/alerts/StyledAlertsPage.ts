import { styled } from '@mui/material/styles';
import { TableContainer, TableCell, Button } from '@mui/material';

export const StyledTableContainer = styled(TableContainer)<{
  component?: React.ElementType;
}>(({ theme }) => ({
  padding: theme.spacing(2),
}));

export const StyledSeverityCell = styled(TableCell)<{ severity: string }>(
  ({ severity }) => ({
    color: severity === 'High' ? 'red' : 'orange',
  })
);

export const StyledButton = styled(Button)(() => ({
  minWidth: '170px',
  textTransform: 'none',
}));
