export const mockLogsData = [
  {
    id: 1,
    timestamp: '2025-03-30 10:00:00',
    user: 'admin',
    event: 'Login Attempt',
    status: 'Success',
    alert: true,
  },
  {
    id: 2,
    timestamp: '2025-03-30 10:15:00',
    user: 'user123',
    event: 'Login Attempt',
    status: 'Failure',
    alert: false,
  },
  {
    id: 3,
    timestamp: '2025-03-30 10:30:00',
    user: 'admin',
    event: 'Password Change',
    status: 'Success',
    alert: false,
  },
  {
    id: 4,
    timestamp: '2025-03-30 10:45:00',
    user: 'guest',
    event: 'Login Attempt',
    status: 'Failure',
    alert: true,
  },
];

export const mockLogsGraphData = [
  { date: 'Mar 24', logs: 200, failed: 50 },
  { date: 'Mar 25', logs: 180, failed: 40 },
  { date: 'Mar 26', logs: 220, failed: 60 },
  { date: 'Mar 27', logs: 250, failed: 70 },
  { date: 'Mar 28', logs: 230, failed: 55 },
  { date: 'Mar 29', logs: 270, failed: 80 },
  { date: 'Mar 30', logs: 300, failed: 90 },
];
