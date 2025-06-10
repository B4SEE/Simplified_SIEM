import axios from 'axios';
import { config } from '../config';

const BASE_URL = config.AUTH_API_URL;

// Create axios instance with default config
const api = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor to handle CORS
api.interceptors.request.use(
  config => {
    config.withCredentials = true;
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle errors
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      console.error('Response error:', error.response.data);
    } else if (error.request) {
      console.error('Request error:', error.request);
    } else {
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// Public endpoints - no auth required
export const checkAuthStatus = async () => {
  return api.get('/status');
};

export const login = async (credentials: {
  username: string;
  password: string;
}) => {
  const response = await api.post('/login', credentials);
  return response.data;
};

export const register = async (data: {
  username: string;
  email: string;
  password: string;
  confirm_password: string;
  first_name?: string;
  last_name?: string;
}) => {
  try {
    const response = await api.post('/register', data);
    return response.data;
  } catch (error: any) {
    const message =
      error.response?.data?.message || error.message || 'Registration failed.';
    throw new Error(message);
  }
};

// Protected endpoints - require auth
export const getProfile = async (token: string, userId: number) => {
  return api.get('/profile', {
    headers: {
      Authorization: `Bearer ${token}`,
      'X-User-Id': String(userId),
    },
  });
};

export const updateProfile = async (
  token: string,
  userId: number,
  profileData: {
    username: string;
    email: string;
    first_name: string;
    last_name: string;
  }
) => {
  return api.put('/profile', profileData, {
    headers: {
      Authorization: `Bearer ${token}`,
      'X-User-Id': String(userId),
    },
  });
};

export const changePassword = async (
  token: string,
  userId: number,
  data: {
    current_password: string;
    new_password: string;
    confirm_password: string;
  }
) => {
  return api.put('/password', data, {
    headers: {
      Authorization: `Bearer ${token}`,
      'X-User-Id': String(userId),
    },
  });
};

export const verifyEmail = async (token: string, userId: number) => {
  return api.get('/verify-email', {
    headers: {
      Authorization: `Bearer ${token}`,
      'X-User-Id': String(userId),
    },
  });
};
