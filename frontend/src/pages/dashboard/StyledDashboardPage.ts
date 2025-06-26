import { styled } from '@mui/system';
import { Box, colors, Typography } from '@mui/material';

interface StatBoxProps {
  color: string;
}

export const DashboardContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
}));

export const Title = styled(Typography)(({ theme }) => ({
  marginBottom: theme.spacing(2),
}));

export const StatBoxContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexWrap: 'wrap',
  gap: theme.spacing(3),
}));

export const StatBox = styled(Box)<StatBoxProps>(({ theme, color }) => ({
  backgroundColor: color,
  color: '#000',
  padding: theme.spacing(2),
  width: '100%',
  [theme.breakpoints.up('sm')]: {
    width: '48%',
  },
  [theme.breakpoints.up('md')]: {
    width: '23%',
  },
}));

export const LastLoginText = styled(Typography)(({ theme }) => ({
  marginTop: theme.spacing(2),
}));
