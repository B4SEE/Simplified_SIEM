import React, { useState } from 'react';
import { TextField, Typography, Container } from '@mui/material';
import { LoginBox, StyledButton, StyledForm } from '../login/StyledLoginPage';
import { Link } from 'react-router-dom';

const RegistrationPage: React.FC = () => {
  const [formData, setFormData] = useState({
    username: '',
    firstName: '',
    lastName: '',
    email: '',
    password: '',
  });
  const [error, setError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const isEmpty = Object.values(formData).some((field) => !field.trim());
    if (isEmpty) {
      setError('Please fill out all fields.');
      return;
    }
    console.log('Registering user:', formData);
  };

  return (
    <Container component='main' maxWidth='xs'>
      <LoginBox elevation={3}>
        <Typography variant='h5' gutterBottom>
          Register
        </Typography>
        <StyledForm onSubmit={handleSubmit}>
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
          {error && <Typography color='error'>{error}</Typography>}
          <StyledButton type='submit' variant='contained' fullWidth>
            Register
          </StyledButton>
        </StyledForm>
        <Typography
          variant='body2'
          align='center'
          style={{ marginTop: '1rem' }}
        >
          Already have an account? <Link to='/login'>Log in</Link>
        </Typography>
      </LoginBox>
    </Container>
  );
};

export default RegistrationPage;
