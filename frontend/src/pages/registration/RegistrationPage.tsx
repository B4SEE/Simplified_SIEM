import React, { useState } from 'react';
import { TextField, Typography, Container } from '@mui/material';
import { LoginBox, StyledButton, StyledForm } from '../login/StyledLoginPage';
import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import { register } from '../../api/auth';



const RegistrationPage: React.FC = () => {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    username: '',
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const isEmpty = Object.values(formData).some((field) => !field.trim());
    if (isEmpty) {
      setError('Please fill out all fields.');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    const payload = {
      username: formData.username,
      email: formData.email,
      password: formData.password,
      confirm_password: formData.confirmPassword,
      first_name: formData.firstName,
      last_name: formData.lastName,
    };
    try {
      const data = await register(payload);
  
      console.log('Registration success:', data);
      navigate('/login');
    } catch (err: any) {
      setError(err.message || 'Something went wrong.');
    }
  
    // try {
    //   const res = await fetch('http://localhost:5001/api/auth/register', {
    //     // mode: 'no-cors',
    //     method: 'POST',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify(payload),
    //   });

    //   const data = await res.json();

    //   if (!res.ok) {
    //     throw new Error(data.message || 'Registration failed.');
    //   }

    //   console.log('Registration success:', data);


    //   navigate('/login');
    // } catch (err: any) {
    //   setError(err.message || 'Something went wrong.');
    // }
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
          <TextField
            label='Confirm Password'
            type='password'
            name='confirmPassword'
            value={formData.confirmPassword}
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