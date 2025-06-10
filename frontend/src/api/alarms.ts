import axios from 'axios';
import { config } from '../config';

const BASE_URL = config.ALARMS_API_URL;

// Create axios instance with default config
const api = axios.create({
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  }
});

export const getAlarms = async (token: string, userId: string | number) => {
  return api.get(`${BASE_URL}/`, {
    headers: {
      Authorization: `Bearer ${token}`,
      'X-User-Id': userId,
    },
  });
};

export const getAlarmById = async (alarmId: number, token: string, userId: string | number) => {
  return api.get(`${BASE_URL}/${alarmId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      'X-User-Id': userId
    },
  });
};

export const createAlarm = async (
  token: string,
  userId: string | number,
  alarmData: {
    name: string;
    description: string;
    event_type: string;
    threshold: number;
    time_window: number;
    is_active: boolean;
    severity: 'low' | 'medium' | 'high';
    criteria: Record<string, any>;
  }
) => {
  return api.post(`${BASE_URL}/`, alarmData, {
    headers: {
      Authorization: `Bearer ${token}`,
      'X-User-Id': userId,
    },
  });
};

export const updateAlarm = async (
  alarmId: number,
  token: string,
  userId: string | number,
  updatedFields: Partial<{
    name: string;
    description: string;
    event_type: string;
    threshold: number;
    time_window: number;
    is_active: boolean;
    severity: 'low' | 'medium' | 'high';
    criteria: Record<string, any>;
  }>
) => {
  return api.put(`${BASE_URL}/${alarmId}`, updatedFields, {
    headers: {
      Authorization: `Bearer ${token}`,
      'X-User-Id': userId,
    },
  });
};

// Enable or disable alarm
export const toggleAlarmStatus = async (
  alarmId: number,
  token: string,
  is_active: boolean,
  userId: string | number
) => {
  try {
    console.log('Sending toggle request:', {
      url: `${BASE_URL}/${alarmId}/status`,
      is_active,
      alarmId,
      userId
    });

    const response = await api.put(
      `${BASE_URL}/${alarmId}/status`,
      { is_active },
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'X-User-Id': userId,
        },
      }
    );

    console.log('✅ Toggle response:', response.data);
    return response;
  } catch (error: any) {
    console.error('❌ Toggle request failed:', {
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    });
    throw error;
  }
};

export const deleteAlarm = async (alarmId: number, token: string, userId: string | number) => {
  return api.delete(`${BASE_URL}/${alarmId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      'X-User-Id': userId,
    },
  });
};
