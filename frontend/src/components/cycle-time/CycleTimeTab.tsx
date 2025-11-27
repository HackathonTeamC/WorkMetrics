import React, { useState, useEffect } from 'react';
import { format, subDays } from 'date-fns';
import { cycleTimeService } from '../../services/cycleTimeService';
import { CycleTimeData } from '../../types/cycleTime';
import { TimeRange } from '../../types/api';
import TimeRangeSelector from '../common/TimeRangeSelector';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';
import StageBreakdown from './StageBreakdown';
import PercentileChart from './PercentileChart';

interface CycleTimeTabProps {
  projectId: number;
}

const CycleTimeTab: React.FC<CycleTimeTabProps> = ({ projectId }) => {
  const [timeRange, setTimeRange] = useState<TimeRange>({
    start: format(subDays(new Date(), 30), 'yyyy-MM-dd'),
    end: format(new Date(), 'yyyy-MM-dd'),
  });

  const [data, setData] = useState<CycleTimeData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    if (!projectId) return;

    setLoading(true);
    setError(null);

    try {
      const result = await cycleTimeService.getCycleTime(projectId, {
        start_date: timeRange.start,
        end_date: timeRange.end,
      });
      setData(result);
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.message || err.message || 'Failed to fetch cycle time data';
      setError(errorMessage);
      console.error('Error fetching cycle time:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [projectId, timeRange.start, timeRange.end]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Cycle Time Analysis</h2>
        <p className="text-gray-600">
          Analyze cycle time broken down by development stages (coding, review, deployment) to
          identify process bottlenecks and optimization opportunities
        </p>
      </div>

      <TimeRangeSelector value={timeRange} onChange={setTimeRange} />

      {loading && <LoadingSpinner message="Analyzing cycle times..." />}

      {error && <ErrorMessage message={error} onRetry={fetchData} />}

      {!loading && !error && data && (
        <>
          {data.metrics.count === 0 ? (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
              <p className="text-yellow-800">
                No merged merge requests found for the selected time period. Cycle time analysis
                requires merged MRs with deployment data. Make sure to refresh project data to
                sync merge requests from GitLab.
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              <StageBreakdown metrics={data.metrics} />
              <PercentileChart distribution={data.distribution} />

              {/* Additional Insights */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  How to Use This Analysis
                </h3>
                <div className="space-y-3 text-sm text-gray-700">
                  <div className="flex gap-3">
                    <span className="text-blue-600 font-bold">1.</span>
                    <div>
                      <strong>Identify Bottlenecks:</strong> Look at which stage takes the most
                      time on average. If review time dominates, consider increasing reviewer
                      availability or improving MR quality.
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-blue-600 font-bold">2.</span>
                    <div>
                      <strong>Monitor Percentiles:</strong> The 75th and 90th percentiles show how
                      long the slower MRs take. Large gaps between median and p90 indicate
                      inconsistency.
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-blue-600 font-bold">3.</span>
                    <div>
                      <strong>Track Trends:</strong> Compare cycle times across different periods
                      to see if process improvements are working.
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-blue-600 font-bold">4.</span>
                    <div>
                      <strong>Investigate Outliers:</strong> Use the distribution chart to find
                      specific MRs with unusually long cycle times and understand what caused the
                      delay.
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default CycleTimeTab;
