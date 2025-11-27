import React from 'react';
import { CycleTimeMetrics } from '../../types/cycleTime';

interface StageBreakdownProps {
  metrics: CycleTimeMetrics;
}

const StageBreakdown: React.FC<StageBreakdownProps> = ({ metrics }) => {
  const { stages, total, stage_breakdown_avg } = metrics;

  const formatTime = (hours: number): string => {
    if (hours === 0) return '0h';
    if (hours < 1) return `${Math.round(hours * 60)}m`;
    if (hours < 24) return `${hours.toFixed(1)}h`;
    const days = hours / 24;
    return `${days.toFixed(1)}d`;
  };

  const stages_data = [
    {
      name: 'Coding',
      stats: stages.coding,
      percentage: stage_breakdown_avg.coding_percentage,
      color: 'bg-blue-500',
      icon: '💻',
      description: 'Time from first commit to MR creation',
    },
    {
      name: 'Review',
      stats: stages.review,
      percentage: stage_breakdown_avg.review_percentage,
      color: 'bg-green-500',
      icon: '👀',
      description: 'Time from MR creation to merge',
    },
    {
      name: 'Deployment',
      stats: stages.deployment,
      percentage: stage_breakdown_avg.deployment_percentage,
      color: 'bg-purple-500',
      icon: '🚀',
      description: 'Time from merge to deployment',
    },
  ];

  if (metrics.count === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
        No cycle time data available for this period.
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Cycle Time Stage Breakdown</h3>
        <p className="mt-1 text-sm text-gray-500">
          Average time spent in each stage of the development process
        </p>
        <div className="mt-2 text-sm text-gray-600">
          Based on {metrics.count} merged MR{metrics.count !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Overall Cycle Time Summary */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <div className="text-sm text-gray-600 mb-1">Total Average Cycle Time</div>
        <div className="text-3xl font-bold text-gray-900">{formatTime(total.mean)}</div>
        <div className="mt-2 grid grid-cols-3 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Median: </span>
            <span className="font-medium text-gray-900">{formatTime(total.median)}</span>
          </div>
          <div>
            <span className="text-gray-600">75th: </span>
            <span className="font-medium text-gray-900">{formatTime(total.p75)}</span>
          </div>
          <div>
            <span className="text-gray-600">90th: </span>
            <span className="font-medium text-gray-900">{formatTime(total.p90)}</span>
          </div>
        </div>
      </div>

      {/* Visual Stage Breakdown Bar */}
      <div className="mb-6">
        <div className="text-sm font-medium text-gray-700 mb-2">Stage Distribution</div>
        <div className="flex h-8 rounded-lg overflow-hidden">
          {stages_data.map((stage, index) => (
            <div
              key={index}
              className={`${stage.color} flex items-center justify-center text-white text-xs font-medium`}
              style={{ width: `${stage.percentage}%` }}
              title={`${stage.name}: ${stage.percentage.toFixed(1)}%`}
            >
              {stage.percentage > 10 && (
                <span>
                  {stage.icon} {stage.percentage.toFixed(0)}%
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Detailed Stage Statistics */}
      <div className="space-y-4">
        {stages_data.map((stage, index) => (
          <div key={index} className="border-l-4 pl-4" style={{ borderColor: stage.color.replace('bg-', '#') }}>
            <div className="flex items-center justify-between mb-2">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-lg">{stage.icon}</span>
                  <h4 className="font-semibold text-gray-900">{stage.name}</h4>
                  <span className="text-sm text-gray-500">({stage.percentage.toFixed(1)}%)</span>
                </div>
                <p className="text-xs text-gray-500 mt-1">{stage.description}</p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-gray-900">
                  {formatTime(stage.stats.mean)}
                </div>
                <div className="text-xs text-gray-500">average</div>
              </div>
            </div>
            <div className="grid grid-cols-4 gap-2 text-sm mt-2">
              <div className="bg-gray-50 p-2 rounded">
                <div className="text-gray-600 text-xs">Median</div>
                <div className="font-medium text-gray-900">{formatTime(stage.stats.median)}</div>
              </div>
              <div className="bg-gray-50 p-2 rounded">
                <div className="text-gray-600 text-xs">75th %ile</div>
                <div className="font-medium text-gray-900">{formatTime(stage.stats.p75)}</div>
              </div>
              <div className="bg-gray-50 p-2 rounded">
                <div className="text-gray-600 text-xs">90th %ile</div>
                <div className="font-medium text-gray-900">{formatTime(stage.stats.p90)}</div>
              </div>
              <div className="bg-gray-50 p-2 rounded">
                <div className="text-gray-600 text-xs">Range</div>
                <div className="font-medium text-gray-900">
                  {formatTime(stage.stats.min)} - {formatTime(stage.stats.max)}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Insights */}
      <div className="mt-6 p-4 bg-blue-50 rounded-md">
        <p className="text-sm text-blue-800">
          <strong>💡 Interpretation:</strong>{' '}
          {stage_breakdown_avg.review_percentage > 50
            ? 'Review time is the dominant stage. Consider increasing reviewer availability or breaking down MRs.'
            : stage_breakdown_avg.coding_percentage > 50
            ? 'Coding time is the longest stage. Consider smaller, more frequent commits.'
            : stage_breakdown_avg.deployment_percentage > 30
            ? 'Deployment time is high. Consider improving CI/CD pipeline efficiency.'
            : 'Cycle time is well-balanced across stages.'}
        </p>
      </div>
    </div>
  );
};

export default StageBreakdown;
