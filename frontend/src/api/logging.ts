import axios from 'axios';
import { config } from '../config';

const BASE_URL = config.LOGGING_API_URL;

export interface LogEntry {
  timestamp: string;
  ip_address: string;
  event_type: string;
  user_ID: number;
  user_agent: string;
  geo?: [number, number];  // [latitude, longitude]
  severity?: 'low' | 'medium' | 'high';
  additional_data?: Record<string, any>;
}

// Note: These endpoints are internal service endpoints and don't require auth
export const sendLog = async (logData: LogEntry) => {
  try {
    const response = await axios.post(`${BASE_URL}/logs`, logData, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  } catch (error: any) {
    console.error('Failed to send log:', error);
    throw error;
  }
};

export const processLogs = async () => {
  try {
    const response = await axios.post(`${BASE_URL}/process_logs`, null, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  } catch (error: any) {
    console.error('Failed to process logs:', error);
    throw error;
  }
};

export const searchLogs = async (query: {
  startDate?: string;
  endDate?: string;
  eventType?: string;
  userId?: number;
  severity?: string;
  limit?: number;
  offset?: number;
}) => {
  try {
    const response = await axios.get(`${BASE_URL}/logs/search`, {
      params: query,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  } catch (error: any) {
    console.error('Failed to search logs:', error);
    throw error;
  }
};

export const getLogStats = async (startDate?: string, endDate?: string) => {
  try {
    const response = await axios.get(`${BASE_URL}/logs/stats`, {
      params: { startDate, endDate },
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  } catch (error: any) {
    console.error('Failed to get log stats:', error);
    throw error;
  }
};