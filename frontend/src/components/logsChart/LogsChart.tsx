import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import colors from '../../theme/colors';

interface LogsChartProps {
  data: { date: string; logs: number; failed: number }[];
}

const LogsChart: React.FC<LogsChartProps> = ({ data }) => {
  return (
    <ResponsiveContainer width='100%' height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray='3 3' />
        <XAxis dataKey='date' />
        <YAxis />
        <Tooltip />
        <Line
          type='monotone'
          dataKey='logs'
          stroke={colors.successfulLogins}
          strokeWidth={2}
        />
        <Line
          type='monotone'
          dataKey='failed'
          stroke={colors.failedLogins}
          strokeWidth={2}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default LogsChart;
