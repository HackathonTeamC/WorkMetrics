import React, { useState } from 'react';
import { format, subDays } from 'date-fns';
import { useMetrics } from '../../hooks/useMetrics';
import TimeRangeSelector from '../common/TimeRangeSelector';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';
import DeploymentFrequency from './DeploymentFrequency';
import LeadTimeChart from './LeadTimeChart';
import ChangeFailureRate from './ChangeFailureRate';
import TimeToRestore from './TimeToRestore';
import { TimeRange } from '../../types/api';

interface FourKeysTabProps {
  projectId: number;
}

const FourKeysTab: React.FC<FourKeysTabProps> = ({ projectId }) => {
  const [timeRange, setTimeRange] = useState<TimeRange>({
    start: format(subDays(new Date(), 30), 'yyyy-MM-dd'),
    end: format(new Date(), 'yyyy-MM-dd'),
  });

  const { metrics, loading, error, refetch } = useMetrics(projectId, {
    start_date: timeRange.start,
    end_date: timeRange.end,
  });

  const calculatePeriodDays = (): number => {
    const start = new Date(timeRange.start);
    const end = new Date(timeRange.end);
    return Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Four Keys Metrics</h2>
        <p className="text-gray-600">
          DevOps performance metrics based on the DORA (DevOps Research and Assessment) framework
        </p>
      </div>

      <TimeRangeSelector value={timeRange} onChange={setTimeRange} />

      {loading && <LoadingSpinner message="Loading metrics..." />}

      {error && <ErrorMessage message={error} onRetry={refetch} />}

      {!loading && !error && metrics && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <DeploymentFrequency
            frequency={metrics.deployment_frequency}
            deploymentCount={metrics.deployment_count}
            periodDays={calculatePeriodDays()}
          />

          <LeadTimeChart
            meanHours={metrics.lead_time_hours}
            medianHours={metrics.lead_time_median_hours}
          />

          <ChangeFailureRate
            failureRate={metrics.change_failure_rate}
            failedCount={metrics.failed_deployment_count}
            totalCount={metrics.deployment_count}
          />

          <TimeToRestore
            meanHours={metrics.time_to_restore_hours}
            medianHours={metrics.time_to_restore_median_hours}
          />
        </div>
      )}

      {!loading && !error && metrics && metrics.deployment_count === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <p className="text-yellow-800">
            No deployments found for the selected time period. Try expanding the date range or
            refresh project data.
          </p>
        </div>
      )}
    </div>
  );
};

export default FourKeysTab;
