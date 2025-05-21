import axios from 'axios';

const BASE_URL = 'http://localhost:5001/api/auth';

export const checkAuthStatus = async () => {
  return axios.get(`${BASE_URL}/status`);
};

export const login = async (credentials: {
  username: string;
  password: string;
}) => {
  const response = await axios.post(`${BASE_URL}/login`, credentials);
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
    const response = await axios.post(`${BASE_URL}/register`, data);
    return response.data;
  } catch (error: any) {
    const message =
      error.response?.data?.message || error.message || 'Registration failed.';
    throw new Error(message);
  }
};

export const getProfile = async (token: string, userId: number) => {
  return axios.get(`${BASE_URL}/profile`, {
    headers: {
      Authorization: `Bearer ${token}`,
      'X-User-ID': String(userId),
    },
  });
};

export const updateProfile = async (
  token: string,
  profileData: {
    username: string;
    email: string;
    first_name: string;
    last_name: string;
  }
) => {
  return axios.put(`${BASE_URL}/profile`, profileData, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });
};

export const changePassword = async (
  token: string,
  data: {
    current_password: string;
    new_password: string;
    confirm_password: string;
  }
) => {
  return axios.put(`${BASE_URL}/password`, data, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });
};

export const verifyEmail = async (token: string) => {
  return axios.get(`${BASE_URL}/verify-email/`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
};
