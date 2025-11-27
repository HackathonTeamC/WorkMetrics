import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { ReviewLoad } from '../../types/team';

interface ReviewLoadChartProps {
  reviewLoad: ReviewLoad[];
}

const ReviewLoadChart: React.FC<ReviewLoadChartProps> = ({ reviewLoad }) => {
  if (reviewLoad.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
        No review load data available for this period.
      </div>
    );
  }

  // Sort by review count descending and take top 10
  const topReviewers = [...reviewLoad]
    .sort((a, b) => b.review_count - a.review_count)
    .slice(0, 10);

  const chartData = topReviewers.map((reviewer) => ({
    name: reviewer.username,
    'Review Count': reviewer.review_count,
    'Comments': reviewer.comment_count,
    'Load %': reviewer.review_load_percentage,
  }));

  // Calculate load balance (ideal is equal distribution)
  const idealPercentage = 100 / reviewLoad.length;
  const maxDeviation = Math.max(
    ...reviewLoad.map((r) => Math.abs(r.review_load_percentage - idealPercentage))
  );
  const isBalanced = maxDeviation < 10; // Within 10% of ideal

  // Color bars based on load
  const getBarColor = (percentage: number): string => {
    if (percentage > 30) return '#ef4444'; // Red - overloaded
    if (percentage > 20) return '#f59e0b'; // Orange - heavy
    if (percentage > 10) return '#3b82f6'; // Blue - normal
    return '#10b981'; // Green - light
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Review Load Distribution</h3>
        <p className="mt-1 text-sm text-gray-500">
          Distribution of code review workload across team members
        </p>
        <div className="mt-2 flex items-center gap-4">
          <span
            className={`text-sm font-medium ${
              isBalanced ? 'text-green-600' : 'text-yellow-600'
            }`}
          >
            {isBalanced ? '✓ Well Balanced' : '⚠ Imbalanced Load'}
          </span>
          <span className="text-sm text-gray-500">
            Total reviews: {reviewLoad.reduce((sum, r) => sum + r.review_count, 0)}
          </span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 60 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="name"
            angle={-45}
            textAnchor="end"
            height={80}
            interval={0}
          />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="Review Count" fill="#3b82f6">
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getBarColor(entry['Load %'])} />
            ))}
          </Bar>
          <Bar dataKey="Comments" fill="#10b981" />
        </BarChart>
      </ResponsiveContainer>

      <div className="mt-6 grid grid-cols-2 gap-4 text-sm">
        <div>
          <h4 className="font-medium text-gray-700 mb-2">Top Reviewers</h4>
          <ul className="space-y-1">
            {topReviewers.slice(0, 5).map((reviewer) => (
              <li key={reviewer.team_member_id} className="flex justify-between">
                <span className="text-gray-600">{reviewer.name}</span>
                <span className="font-medium text-gray-900">
                  {reviewer.review_count} ({reviewer.review_load_percentage.toFixed(1)}%)
                </span>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h4 className="font-medium text-gray-700 mb-2">Load Indicators</h4>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-red-500 rounded"></div>
              <span className="text-gray-600">Overloaded (&gt;30%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-yellow-500 rounded"></div>
              <span className="text-gray-600">Heavy (20-30%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-blue-500 rounded"></div>
              <span className="text-gray-600">Normal (10-20%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-green-500 rounded"></div>
              <span className="text-gray-600">Light (&lt;10%)</span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-4 p-4 bg-blue-50 rounded-md">
        <p className="text-sm text-blue-800">
          <strong>💡 Tip:</strong> Ideally, review load should be distributed evenly across team
          members. Significant imbalances may indicate bottlenecks or opportunities to spread
          knowledge more broadly.
        </p>
      </div>
    </div>
  );
};

export default ReviewLoadChart;
