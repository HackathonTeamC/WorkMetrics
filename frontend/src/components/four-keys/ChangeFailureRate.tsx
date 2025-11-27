import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface ChangeFailureRateProps {
  failureRate: number | null;
  failedCount: number;
  totalCount: number;
}

const ChangeFailureRate: React.FC<ChangeFailureRateProps> = ({
  failureRate,
  failedCount,
  totalCount,
}) => {
  const successCount = totalCount - failedCount;
  
  const data = [
    { name: 'Successful', value: successCount, color: '#10b981' },
    { name: 'Failed', value: failedCount, color: '#ef4444' },
  ];

  const getRating = (rate: number | null): { level: string; color: string } => {
    if (rate === null) return { level: 'No Data', color: 'text-gray-400' };
    if (rate <= 15) return { level: 'Elite', color: 'text-green-600' };
    if (rate <= 30) return { level: 'High', color: 'text-blue-600' };
    if (rate <= 45) return { level: 'Medium', color: 'text-yellow-600' };
    return { level: 'Low', color: 'text-red-600' };
  };

  const rating = getRating(failureRate);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Change Failure Rate</h3>
      
      <div className="mb-6">
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold text-gray-900">
            {failureRate !== null ? `${failureRate.toFixed(1)}%` : 'N/A'}
          </span>
          <span className="text-sm text-gray-500">failure rate</span>
        </div>
        <div className="mt-2 flex items-center gap-2">
          <span className={`text-sm font-medium ${rating.color}`}>{rating.level}</span>
          <span className="text-sm text-gray-500">
            • {failedCount} failed / {totalCount} total
          </span>
        </div>
      </div>

      {totalCount > 0 && (
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      )}

      <div className="mt-4 text-sm text-gray-600">
        <p className="font-medium">Percentage of deployments causing failures</p>
        <p className="mt-1">Elite: 0-15% | High: 16-30% | Medium: 31-45% | Low: &gt;45%</p>
      </div>
    </div>
  );
};

export default ChangeFailureRate;
