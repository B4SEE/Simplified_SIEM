import React, { useEffect, useState } from 'react';
import { TextField, Typography, Container } from '@mui/material';
import { LoginBox, StyledButton, StyledForm } from '../login/StyledLoginPage';
import { useAuth } from '../../contexts/AuthContext';
import { getProfile } from '../../api/auth';

const UserPage: React.FC = () => {
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

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Saving updated user info:', formData);
  };

  return (
    <Container component='main' maxWidth='xs'>
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
