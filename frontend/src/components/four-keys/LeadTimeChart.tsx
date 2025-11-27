import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface LeadTimeChartProps {
  meanHours: number | null;
  medianHours: number | null;
}

const LeadTimeChart: React.FC<LeadTimeChartProps> = ({ meanHours, medianHours }) => {
  const data = [
    {
      metric: 'Lead Time',
      Mean: meanHours ? parseFloat(meanHours.toFixed(2)) : 0,
      Median: medianHours ? parseFloat(medianHours.toFixed(2)) : 0,
    },
  ];

  const getRating = (hours: number | null): { level: string; color: string } => {
    if (hours === null) return { level: 'No Data', color: 'text-gray-400' };
    if (hours <= 24) return { level: 'Elite', color: 'text-green-600' };
    if (hours <= 168) return { level: 'High', color: 'text-blue-600' };
    if (hours <= 720) return { level: 'Medium', color: 'text-yellow-600' };
    return { level: 'Low', color: 'text-red-600' };
  };

  const rating = getRating(meanHours);

  const formatHours = (hours: number | null): string => {
    if (hours === null) return 'N/A';
    if (hours < 24) return `${hours.toFixed(1)}h`;
    return `${(hours / 24).toFixed(1)}d`;
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Lead Time for Changes</h3>
      
      <div className="mb-6">
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold text-gray-900">
            {formatHours(meanHours)}
          </span>
          <span className="text-sm text-gray-500">average</span>
        </div>
        <div className="mt-2 flex items-center gap-2">
          <span className={`text-sm font-medium ${rating.color}`}>{rating.level}</span>
          <span className="text-sm text-gray-500">
            • Median: {formatHours(medianHours)}
          </span>
        </div>
      </div>

      {meanHours !== null && (
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="metric" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="Mean" stroke="#3b82f6" strokeWidth={2} />
            <Line type="monotone" dataKey="Median" stroke="#10b981" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      )}

      <div className="mt-4 text-sm text-gray-600">
        <p className="font-medium">Time from commit to production deployment</p>
        <p className="mt-1">Elite: &lt;1 day | High: &lt;1 week | Medium: &lt;1 month | Low: &gt;1 month</p>
      </div>
    </div>
  );
};

export default LeadTimeChart;
