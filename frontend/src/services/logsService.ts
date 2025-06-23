import { searchLogs } from '../api/logging';
import { getAlarms } from '../api/alarms';
export { searchLogs };

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
  roles?: string[]; // Added for user roles display
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

export const fetchLogStats = async (
  token?: string,
  userId?: number,
  userRole: string = 'user',
  startDate?: string,
  endDate?: string
): Promise<LogStats> => {
  try {
    const response = await searchLogs(
      {
        startDate,
        endDate,
        limit: 1000,
      },
      token,
      userId,
      userRole
    );

    const logs: LogEntry[] = response.logs || [];
    const successfulLogins = logs.filter((log: LogEntry) => log.event_type === 'login_success').length;
    const failedLogins = logs.filter((log: LogEntry) => log.event_type === 'login_failed').length;
    
    // Get actual alarms count from alarms API
    let alertsCount = 0;
    if (token && userId) {
      try {
        const alarmsResponse = await getAlarms(token, userId);
        if (alarmsResponse.data.status === 'success') {
          // Count active (unresolved) alarms
          alertsCount = alarmsResponse.data.alarms.filter((alarm: any) => alarm.is_active).length;
        }
      } catch (alarmsError) {
        console.warn('Failed to fetch alarms for count:', alarmsError);
        // Fallback to counting high severity logs if alarms API fails
        alertsCount = logs.filter((log: LogEntry) => log.severity === 'high').length;
      }
    }
    
    const lastLogin = logs
      .filter((log: LogEntry) => log.event_type === 'login_success')
      .sort((a: LogEntry, b: LogEntry) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())[0]?.timestamp;

    // Format the last login timestamp to be user-friendly
    const formattedLastLogin = lastLogin 
      ? new Date(lastLogin).toLocaleString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: true
        })
      : 'No recent logins';

    return {
      totalLogs: logs.length,
      successfulLogins,
      failedLogins,
      alertsCount,
      lastLogin: formattedLastLogin
    };
  } catch (error) {
    console.error('Failed to get log stats:', error);
    throw error;
  }
};

export const getLogsGraphData = async (
  token?: string,
  userId?: number,
  userRole: string = 'user',
  days: number = 7
): Promise<LogsGraphData[]> => {
  try {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - (days - 1)); // Include today in the range

    console.log('Graph data date range:', { startDate: startDate.toISOString(), endDate: endDate.toISOString() });

    const response = await searchLogs(
      {
        startDate: startDate.toISOString(),
        endDate: endDate.toISOString(),
        limit: 1000,
      },
      token,
      userId,
      userRole
    );

    const logs = response.logs || [];
    console.log('Total logs fetched for graph:', logs.length);
    console.log('Sample log timestamps:', logs.slice(0, 3).map((log: LogEntry) => ({ timestamp: log.timestamp, event_type: log.event_type })));
    
    const graphData: LogsGraphData[] = [];

    for (let i = 0; i < days; i++) {
      const date = new Date(startDate);
      date.setDate(date.getDate() + i);
      
      // Set date range for the day (start of day to end of day) in UTC to match server timestamps
      const dayStart = new Date(date);
      dayStart.setUTCHours(0, 0, 0, 0);
      const dayEnd = new Date(date);
      dayEnd.setUTCHours(23, 59, 59, 999);
      
      const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

      const dayLogs = logs.filter((log: LogEntry) => {
        // Parse log timestamp and handle timezone
        const logDate = new Date(log.timestamp);
        // If timestamp doesn't have timezone info, treat as UTC
        const logDateUTC = log.timestamp.includes('Z') || log.timestamp.includes('+') || log.timestamp.includes('-') 
          ? logDate 
          : new Date(log.timestamp + 'Z');
        
        return logDateUTC >= dayStart && logDateUTC <= dayEnd;
      });

      console.log(`Day ${dateStr}: ${dayLogs.length} logs (${dayLogs.filter((log: LogEntry) => log.event_type === 'login_failed').length} failed)`);

      graphData.push({
        date: dateStr,
        logs: dayLogs.length,
        failed: dayLogs.filter((log: LogEntry) => log.event_type === 'login_failed').length
      });
    }

    console.log('Graph data generated:', graphData);
    return graphData;
  } catch (error) {
    console.error('Failed to get logs graph data:', error);
    throw error;
  }
};

export const getLogs = async (
  token?: string,
  userId?: number,
  userRole: string = 'user',
  limit: number = 10,
  offset: number = 0,
  eventType?: string,
  severity?: string
): Promise<LogSearchResponse> => {
  try {
    const query: any = { limit, offset };
    if (eventType && eventType !== 'all') {
      query.eventType = eventType;
    }
    if (severity) {
      query.severity = severity;
    }
    
    const response = await searchLogs(query, token, userId, userRole);
    return response || { logs: [], total: 0, offset: 0, limit: 0 };
  } catch (error) {
    console.error('Failed to get logs:', error);
    throw error;
  }
};

// Backward compatibility alias for pagination feature
export const getRecentLogs = getLogs;

// Type alias for backward compatibility
export interface GetRecentLogsResult extends LogSearchResponse {}