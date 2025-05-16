import axios from 'axios';

const BASE_URL = 'http://localhost:5001/api/alarms';

export const sendLog = async (logData: {
    timestamp: string;
    event_type: string;
    user_ID: number;
    ip_address: string;
    user_agent: string;
    geo: [number, number];
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