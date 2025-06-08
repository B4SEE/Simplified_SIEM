import axios from 'axios';

const BASE_URL = 'http://localhost:5002/api';

// Note: These endpoints are internal service endpoints and don't require auth
export const sendLog = async (logData: {
    timestamp: string;
    event_type: string;
    user_id: number;
    ip_address: string;
    user_agent: string;
    geo: [number, number];  // [latitude, longitude]
    severity?: 'low' | 'medium' | 'high';
    additional_data?: Record<string, any>;
}) => {
  return axios.post(`${BASE_URL}/logs`, logData, {
    headers: {
      'Content-Type': 'application/json',
    },
  });
};

export const processLogs = async () => {
  return axios.post(`${BASE_URL}/process_logs`, null, {
    headers: {
      'Content-Type': 'application/json',
    },
  });
};