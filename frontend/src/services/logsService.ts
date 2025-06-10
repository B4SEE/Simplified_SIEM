import { searchLogs } from '../api/logging';

export interface LogEntry {
  id: number;
  timestamp: string;
  user_ID: number;
  event_type: string;
  ip_address: string;
  severity: string;
  geo?: [number, number];
  user_agent?: string;
  additional_data?: Record<string, any>;
}

export interface LogStats {
  totalLogs: number;
  successfulLogins: number;
  failedLogins: number;
  alertsCount: number;
  lastLogin: string;
}

export interface LogsGraphData {
  date: string;
  logs: number;
  failed: number;
}

export interface LogSearchResponse {
  logs: LogEntry[];
  total: number;
  offset: number;
  limit: number;
}

export const fetchLogStats = async (startDate?: string, endDate?: string): Promise<LogStats> => {
  try {
    const response = await searchLogs({
      startDate,
      endDate,
      limit: 1000
    });

    const logs: LogEntry[] = response.data.logs || [];
    const successfulLogins = logs.filter((log: LogEntry) => log.event_type === 'login_success').length;
    const failedLogins = logs.filter((log: LogEntry) => log.event_type === 'login_failed').length;
    const alertsCount = logs.filter((log: LogEntry) => log.severity === 'high').length;
    const lastLogin = logs
      .filter((log: LogEntry) => log.event_type === 'login_success')
      .sort((a: LogEntry, b: LogEntry) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())[0]?.timestamp;

    return {
      totalLogs: logs.length,
      successfulLogins,
      failedLogins,
      alertsCount,
      lastLogin: lastLogin || 'No recent logins'
    };
  } catch (error) {
    console.error('Failed to get log stats:', error);
    throw error;
  }
};

export const getLogsGraphData = async (days: number = 7): Promise<LogsGraphData[]> => {
  try {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);

    const response = await searchLogs({
      startDate: startDate.toISOString(),
      endDate: endDate.toISOString(),
      limit: 1000
    });

    const logs = response.data.logs || [];
    const graphData: LogsGraphData[] = [];

    for (let i = 0; i < days; i++) {
      const date = new Date(startDate);
      date.setDate(date.getDate() + i);
      const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

      const dayLogs = logs.filter((log: LogEntry) => {
        const logDate = new Date(log.timestamp);
        return logDate.getDate() === date.getDate() &&
               logDate.getMonth() === date.getMonth() &&
               logDate.getFullYear() === date.getFullYear();
      });

      graphData.push({
        date: dateStr,
        logs: dayLogs.length,
        failed: dayLogs.filter((log: LogEntry) => log.event_type === 'login_failed').length
      });
    }

    return graphData;
  } catch (error) {
    console.error('Failed to get logs graph data:', error);
    throw error;
  }
};

export const getRecentLogs = async (limit: number = 10): Promise<LogEntry[]> => {
  try {
    const response = await searchLogs({ limit });
    return response.data.logs || [];
  } catch (error) {
    console.error('Failed to get recent logs:', error);
    throw error;
  }
}; 