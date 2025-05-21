import axios from 'axios';

const BASE_URL = 'http://localhost:5001/api/alarms';

export const getAlarms = async (token: string) => {
  return axios.get(BASE_URL, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
};

export const getAlarmById = async (alarmId: number, token: string) => {
  return axios.get(`${BASE_URL}/${alarmId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
};

export const createAlarm = async (
  token: string,
  alarmData: {
    name: string;
    description: string;
    event_type: string;
    threshold: number;
    time_window: number;
    is_active: boolean;
    severity: 'low' | 'medium' | 'high';
    criteria: Record<string, any>; // may be adjusted
  }
) => {
  return axios.post(BASE_URL, alarmData, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });
};

export const updateAlarm = async (
  alarmId: number,
  token: string,
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
  return axios.put(`${BASE_URL}/${alarmId}`, updatedFields, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });
};

// Enable or disable alarm
export const toggleAlarmStatus = async (
  alarmId: number,
  token: string,
  is_active: boolean
) => {
  return axios.put(
    `${BASE_URL}/${alarmId}/status`,
    { is_active },
    {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }
  );
};

export const deleteAlarm = async (alarmId: number, token: string) => {
  return axios.delete(`${BASE_URL}/${alarmId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
};
