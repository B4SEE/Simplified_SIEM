import React, { useState } from 'react';
import { TextField, Typography, Container } from '@mui/material';
import { LoginBox, StyledButton, StyledForm } from './StyledLoginPage';

const LoginPage: React.FC = () => {
  const [credentials, setCredentials] = useState({
    username: '',
    password: '',
  });
  const [error, setError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCredentials({ ...credentials, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!credentials.username || !credentials.password) {
      setError('Please enter both username and password.');
      return;
    }
    console.log('Logging in:', credentials);
  };

  return (
    <Container component='main' maxWidth='xs'>
      <LoginBox elevation={3}>
        <Typography variant='h5' gutterBottom>
          Admin Login
        </Typography>
        <StyledForm onSubmit={handleSubmit}>
          <TextField
            label='Username'
            variant='outlined'
            fullWidth
            margin='normal'
            name='username'
            value={credentials.username}
            onChange={handleChange}
          />
          <TextField
            label='Password'
            type='password'
            variant='outlined'
            fullWidth
            margin='normal'
            name='password'
            value={credentials.password}
            onChange={handleChange}
          />
          {error && (
            <Typography color='error' variant='body2'>
              {error}
            </Typography>
          )}
          <StyledButton type='submit' variant='contained' fullWidth>
            Login
          </StyledButton>
        </StyledForm>
      </LoginBox>
    </Container>
  );
};

export default LoginPage;
