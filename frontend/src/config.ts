export const config = {
  AUTH_API_URL: process.env.REACT_APP_AUTH_API_URL || 'http://localhost:5001/api/auth',
  LOGGING_API_URL: process.env.REACT_APP_LOGGING_API_URL || 'http://localhost:5000/api',
  ALARMS_API_URL: process.env.REACT_APP_ALARMS_API_URL || 'http://localhost:5001/api/alarms'
}; 