import React, { useState, useEffect } from 'react';
import { format, subDays } from 'date-fns';
import { teamActivityService } from '../../services/teamActivityService';
import { TeamActivityData } from '../../types/team';
import { TimeRange } from '../../types/api';
import TimeRangeSelector from '../common/TimeRangeSelector';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';
import MemberActivityTable from './MemberActivityTable';
import ReviewLoadChart from './ReviewLoadChart';

interface TeamActivityTabProps {
  projectId: number;
}

const TeamActivityTab: React.FC<TeamActivityTabProps> = ({ projectId }) => {
  const [timeRange, setTimeRange] = useState<TimeRange>({
    start: format(subDays(new Date(), 30), 'yyyy-MM-dd'),
    end: format(new Date(), 'yyyy-MM-dd'),
  });

  const [data, setData] = useState<TeamActivityData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    if (!projectId) return;

    setLoading(true);
    setError(null);

    try {
      const result = await teamActivityService.getTeamActivity(projectId, {
        start_date: timeRange.start,
        end_date: timeRange.end,
      });
      setData(result);
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.message || err.message || 'Failed to fetch team activity data';
      setError(errorMessage);
      console.error('Error fetching team activity:', err);
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
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Team Activity</h2>
        <p className="text-gray-600">
          Track individual team member contributions, merge request activity, and code review
          workload distribution
        </p>
      </div>

      <TimeRangeSelector value={timeRange} onChange={setTimeRange} />

      {loading && <LoadingSpinner message="Loading team activity data..." />}

      {error && <ErrorMessage message={error} onRetry={fetchData} />}

      {!loading && !error && data && (
        <>
          {data.team_members.length === 0 && data.review_load.length === 0 ? (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
              <p className="text-yellow-800">
                No team activity data found for the selected time period. Make sure to refresh
                project data to sync merge requests and team member information from GitLab.
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              <MemberActivityTable members={data.team_members} />
              <ReviewLoadChart reviewLoad={data.review_load} />
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default TeamActivityTab;
