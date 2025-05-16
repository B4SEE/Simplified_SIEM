import React, { useState } from 'react';
import { TextField, Typography, Container } from '@mui/material';
import { LoginBox, StyledButton, StyledForm } from '../login/StyledLoginPage';

const UserPage: React.FC = () => {
  const [formData, setFormData] = useState({
    username: 'admin',
    firstName: 'John',
    lastName: 'Doe',
    email: 'admin@example.com',
    password: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Saving updated user info:', formData);
  };

  const handleLogout = () => {
    console.log('Logging out...');
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
          <StyledButton
            variant='outlined'
            onClick={handleLogout}
            fullWidth
            style={{ marginTop: '1rem' }}
          >
            Log Out
          </StyledButton>
        </StyledForm>
      </LoginBox>
    </Container>
  );
};
export default UserPage;
