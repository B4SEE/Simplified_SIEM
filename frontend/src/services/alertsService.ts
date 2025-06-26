import { getAlarms } from '../api/alarms';

export interface Alert {
  id: number;
  alert_type: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  timestamp: string;
  user_ID?: number;
  ip_address?: string;
  count?: number;
  distance_km?: number;
  velocity_kmh?: number;
  from_geo?: [number, number];
  to_geo?: [number, number];
  from_ip?: string;
  to_ip?: string;
  user_agents?: string[];
  users?: number[];
  ips?: string[];
  resolved: boolean;
}

export const getActiveAlerts = async (token: string, userId: string | number): Promise<Alert[]> => {
  try {
    const response = await getAlarms(token, userId);
    const alarms = response.data.alarms || [];

    // Transform alarms into alerts format
    return alarms.map((alarm: any) => ({
      id: alarm.id,
      alert_type: alarm.alert_type || alarm.name,
      description: alarm.description || getAlertDescription(alarm),
      severity: alarm.severity.toLowerCase(),
      timestamp: alarm.created_at || alarm.timestamp,
      user_ID: alarm.user_ID,
      ip_address: alarm.ip_address,
      count: alarm.count || alarm.event_count,
      distance_km: alarm.distance_km,
      velocity_kmh: alarm.velocity_kmh,
      from_geo: alarm.from_geo,
      to_geo: alarm.to_geo,
      from_ip: alarm.from_ip,
      to_ip: alarm.to_ip,
      user_agents: alarm.user_agents,
      users: alarm.users,
      ips: alarm.ips,
      resolved: alarm.resolved || false
    }));
  } catch (error) {
    console.error('Failed to get active alerts:', error);
    throw error;
  }
};

function getAlertDescription(alarm: any): string {
  switch (alarm.alert_type) {
    case 'impossible_travel':
      return `Impossible travel detected for user ${alarm.user_ID} - ${alarm.velocity_kmh.toFixed(2)} km/h`;
    case 'multiple_user_agents':
      return `Multiple user agents (${alarm.count}) detected for user ${alarm.user_ID}`;
    case 'potential_account_sharing':
      return `Potential account sharing detected from IP ${alarm.ip_address} (${alarm.user_count} users)`;
    case 'distributed_access':
      return `Distributed access detected for user ${alarm.user_ID} from ${alarm.ip_count} IPs`;
    case 'unusual_login_location':
      return `Unusual login location detected for user ${alarm.user_ID} - ${alarm.distance_km.toFixed(2)} km away`;
    case 'excessive_login_failed':
      return `Excessive failed login attempts from IP ${alarm.ip_address} (${alarm.count} attempts)`;
    case 'excessive_password_reset':
      return `Excessive password reset attempts (${alarm.count} attempts)`;
    case 'suspicious_ip_activity':
      return `Suspicious activity from IP ${alarm.ip_address} (${alarm.event_count} events)`;
    default:
      return alarm.description || `Alert: ${alarm.alert_type}`;
  }
} 