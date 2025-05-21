import React, { useEffect, useState } from 'react';
import {
  TextField,
  Typography,
  Container,
  Snackbar,
  Alert,
} from '@mui/material';
import { LoginBox, StyledButton, StyledForm } from '../login/StyledLoginPage';
import { useAuth } from '../../contexts/AuthContext';
import { getProfile, updateProfile } from '../../api/auth';

const UserPage: React.FC = () => {
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const { token, userId } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    firstName: '',
    lastName: '',
    email: '',
    password: '',
  });

  useEffect(() => {
    const fetchUserProfile = async () => {
      if (!token || !userId) return;

      try {
        const response = await getProfile(token, userId);
        const profile = response.data.profile;

        setFormData({
          username: profile.username || '',
          firstName: profile.first_name || '',
          lastName: profile.last_name || '',
          email: profile.email || '',
          password: '',
        });
      } catch (error) {
        console.error('❌ Error fetching profile:', error);
      }
    };

    fetchUserProfile();
  }, [token, userId]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token || !userId) return;

    try {
      const response = await updateProfile(token, userId, {
        username: formData.username,
        email: formData.email,
        first_name: formData.firstName,
        last_name: formData.lastName,
      });

      setSuccessMessage(
        response.data.message || 'Profile updated successfully'
      );
    } catch (error: any) {
      const msg = error.response?.data?.message || 'Failed to update profile.';
      setErrorMessage(msg);
      console.error('❌ Failed to update profile:', error);
    }
  };

  return (
    <Container component='main' maxWidth='xs'>
      <Snackbar
        open={!!successMessage}
        autoHideDuration={3000}
        onClose={() => setSuccessMessage('')}
      >
        <Alert
          onClose={() => setSuccessMessage('')}
          severity='success'
          sx={{ width: '100%' }}
        >
          {successMessage}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!errorMessage}
        autoHideDuration={3000}
        onClose={() => setErrorMessage('')}
      >
        <Alert
          onClose={() => setErrorMessage('')}
          severity='error'
          sx={{ width: '100%' }}
        >
          {errorMessage}
        </Alert>
      </Snackbar>

      <LoginBox elevation={3}>
        <Typography variant='h5' gutterBottom>
          Account Settings
        </Typography>
        <StyledForm onSubmit={handleSave}>
          <TextField
            label='Username'
            name='username'
            value={formData.username}
            onChange={handleChange}
            fullWidth
            margin='normal'
          />
          <TextField
            label='First Name'
            name='firstName'
            value={formData.firstName}
            onChange={handleChange}
            fullWidth
            margin='normal'
          />
          <TextField
            label='Last Name'
            name='lastName'
            value={formData.lastName}
            onChange={handleChange}
            fullWidth
            margin='normal'
          />
          <TextField
            label='Email'
            name='email'
            value={formData.email}
            onChange={handleChange}
            fullWidth
            margin='normal'
          />
          <TextField
            label='Password'
            type='password'
            name='password'
            value={formData.password}
            onChange={handleChange}
            fullWidth
            margin='normal'
          />
          <StyledButton type='submit' variant='contained' fullWidth>
            Save Changes
          </StyledButton>
        </StyledForm>
      </LoginBox>
    </Container>
  );
};
export default UserPage;
