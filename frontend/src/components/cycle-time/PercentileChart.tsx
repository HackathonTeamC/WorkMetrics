import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { CycleTimeDistributionItem } from '../../types/cycleTime';

interface PercentileChartProps {
  distribution: CycleTimeDistributionItem[];
}

const PercentileChart: React.FC<PercentileChartProps> = ({ distribution }) => {
  if (distribution.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
        No distribution data available for this period.
      </div>
    );
  }

  // Take top 20 slowest MRs for visualization
  const topMRs = distribution.slice(0, 20);

  const chartData = topMRs.map((item) => ({
    mr: `!${item.mr_id}`,
    title: item.title.length > 30 ? item.title.substring(0, 30) + '...' : item.title,
    Coding: item.coding_time,
    Review: item.review_time,
    Deployment: item.deployment_time,
    total: item.total_time,
  }));

  // Calculate percentiles for coloring
  const totalTimes = distribution.map((d) => d.total_time);
  const sortedTimes = [...totalTimes].sort((a, b) => a - b);
  const p50 = sortedTimes[Math.floor(sortedTimes.length * 0.5)];
  const p75 = sortedTimes[Math.floor(sortedTimes.length * 0.75)];
  const p90 = sortedTimes[Math.floor(sortedTimes.length * 0.9)];

  const getBarColor = (total: number): string => {
    if (total >= p90) return '#ef4444'; // Red - slowest 10%
    if (total >= p75) return '#f59e0b'; // Orange - slower 25%
    if (total >= p50) return '#3b82f6'; // Blue - median
    return '#10b981'; // Green - fastest 50%
  };

  const formatTime = (hours: number): string => {
    if (hours < 1) return `${Math.round(hours * 60)}m`;
    if (hours < 24) return `${hours.toFixed(1)}h`;
    const days = hours / 24;
    return `${days.toFixed(1)}d`;
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-900 mb-2">{data.mr}</p>
          <p className="text-xs text-gray-600 mb-2">{data.title}</p>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between gap-4">
              <span className="text-blue-600">Coding:</span>
              <span className="font-medium">{formatTime(data.Coding)}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-green-600">Review:</span>
              <span className="font-medium">{formatTime(data.Review)}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-purple-600">Deployment:</span>
              <span className="font-medium">{formatTime(data.Deployment)}</span>
            </div>
            <div className="flex justify-between gap-4 pt-2 border-t border-gray-200">
              <span className="font-semibold">Total:</span>
              <span className="font-semibold">{formatTime(data.total)}</span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Cycle Time Distribution</h3>
        <p className="mt-1 text-sm text-gray-500">
          Top 20 merge requests with longest cycle times (stacked by stage)
        </p>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 80 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="mr"
            angle={-45}
            textAnchor="end"
            height={100}
            interval={0}
            tick={{ fontSize: 12 }}
          />
          <YAxis
            label={{ value: 'Hours', angle: -90, position: 'insideLeft' }}
            tickFormatter={(value) => formatTime(value)}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Bar dataKey="Coding" stackId="a" fill="#3b82f6" />
          <Bar dataKey="Review" stackId="a" fill="#10b981" />
          <Bar dataKey="Deployment" stackId="a" fill="#8b5cf6" />
        </BarChart>
      </ResponsiveContainer>

      {/* Percentile Legend */}
      <div className="mt-6 grid grid-cols-2 gap-4">
        <div>
          <h4 className="font-medium text-gray-700 mb-2">Percentile Thresholds</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">50th percentile (median):</span>
              <span className="font-medium text-gray-900">{formatTime(p50)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">75th percentile:</span>
              <span className="font-medium text-gray-900">{formatTime(p75)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">90th percentile:</span>
              <span className="font-medium text-gray-900">{formatTime(p90)}</span>
            </div>
          </div>
        </div>
        <div>
          <h4 className="font-medium text-gray-700 mb-2">Stage Colors</h4>
          <div className="space-y-2 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-blue-500 rounded"></div>
              <span className="text-gray-600">Coding Stage</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-green-500 rounded"></div>
              <span className="text-gray-600">Review Stage</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-purple-500 rounded"></div>
              <span className="text-gray-600">Deployment Stage</span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 p-4 bg-yellow-50 rounded-md">
        <p className="text-sm text-yellow-800">
          <strong>⚠️ Bottleneck Analysis:</strong> MRs shown here represent the longest cycle
          times. Look for patterns in which stage dominates to identify process bottlenecks.
          Consistently high review times may indicate reviewer availability issues, while high
          deployment times may suggest CI/CD improvements are needed.
        </p>
      </div>

      {/* Summary Statistics */}
      <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
        <div className="p-3 bg-gray-50 rounded">
          <div className="text-gray-600">Total MRs Analyzed</div>
          <div className="text-2xl font-bold text-gray-900">{distribution.length}</div>
        </div>
        <div className="p-3 bg-gray-50 rounded">
          <div className="text-gray-600">Fastest Cycle Time</div>
          <div className="text-2xl font-bold text-green-600">
            {formatTime(Math.min(...totalTimes))}
          </div>
        </div>
        <div className="p-3 bg-gray-50 rounded">
          <div className="text-gray-600">Slowest Cycle Time</div>
          <div className="text-2xl font-bold text-red-600">
            {formatTime(Math.max(...totalTimes))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PercentileChart;
