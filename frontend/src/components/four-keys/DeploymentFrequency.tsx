import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface DeploymentFrequencyProps {
  frequency: number;
  deploymentCount: number;
  periodDays: number;
}

const DeploymentFrequency: React.FC<DeploymentFrequencyProps> = ({
  frequency,
  deploymentCount,
  periodDays,
}) => {
  const data = [
    {
      name: 'Deployments',
      'Per Day': parseFloat(frequency.toFixed(2)),
      'Total': deploymentCount,
    },
  ];

  const getRating = (freq: number): { level: string; color: string } => {
    if (freq >= 1) return { level: 'Elite', color: 'text-green-600' };
    if (freq >= 0.14) return { level: 'High', color: 'text-blue-600' };
    if (freq >= 0.033) return { level: 'Medium', color: 'text-yellow-600' };
    return { level: 'Low', color: 'text-red-600' };
  };

  const rating = getRating(frequency);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Deployment Frequency</h3>
      
      <div className="mb-6">
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold text-gray-900">
            {frequency.toFixed(2)}
          </span>
          <span className="text-sm text-gray-500">deployments/day</span>
        </div>
        <div className="mt-2 flex items-center gap-2">
          <span className={`text-sm font-medium ${rating.color}`}>{rating.level}</span>
          <span className="text-sm text-gray-500">
            • {deploymentCount} deployments in {periodDays} days
          </span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="Per Day" fill="#3b82f6" />
          <Bar dataKey="Total" fill="#10b981" />
        </BarChart>
      </ResponsiveContainer>

      <div className="mt-4 text-sm text-gray-600">
        <p className="font-medium">How often code gets deployed to production</p>
        <p className="mt-1">Elite: Multiple per day | High: Weekly | Medium: Monthly | Low: Less than monthly</p>
      </div>
    </div>
  );
};

export default DeploymentFrequency;
