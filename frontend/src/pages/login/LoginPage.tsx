import React, { useState } from 'react';
import { TextField, Typography, Container } from '@mui/material';
import { LoginBox, StyledButton, StyledForm } from './StyledLoginPage';
import { Link } from 'react-router-dom';
import { login } from '../../api/auth';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { setAuthToken } = useAuth();

  const [credentials, setCredentials] = useState({
    username: '',
    password: '',
  });
  const [error, setError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCredentials({ ...credentials, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!credentials.username || !credentials.password) {
      setError('Please enter both username and password.');
      return;
    }

    try {
      const data = await login(credentials);
      console.log('Login successful:', data);

      setAuthToken(data.token);
      localStorage.setItem('user_id', data.user_id);

      navigate('/dashboard');
    } catch (err: any) {
      const msg =
        err.response?.data?.message || 'Login failed. Please try again.';
      setError(msg);
    }
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
        <Typography
          variant='body2'
          align='center'
          style={{ marginTop: '1rem' }}
        >
          Don’t have an account? <Link to='/register'>Register</Link>
        </Typography>
      </LoginBox>
    </Container>
  );
};

export default LoginPage;
