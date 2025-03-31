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
