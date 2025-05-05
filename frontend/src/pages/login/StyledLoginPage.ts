import { styled } from '@mui/material/styles';
import { Paper, Button } from '@mui/material';

export const LoginBox = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(4),
  marginTop: theme.spacing(4),
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
}));

export const StyledForm = styled('form')({
  width: '100%',
  marginTop: 8,
});

export const StyledButton = styled(Button)(({ theme }) => ({
  marginTop: theme.spacing(2),
}));
