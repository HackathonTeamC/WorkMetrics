import React from 'react';
import { TeamMemberActivity } from '../../types/team';

interface MemberActivityTableProps {
  members: TeamMemberActivity[];
}

const MemberActivityTable: React.FC<MemberActivityTableProps> = ({ members }) => {
  if (members.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
        No team member activity data available for this period.
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Team Member Activity</h3>
        <p className="mt-1 text-sm text-gray-500">
          Individual contributor metrics and code contributions
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Member
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Commits
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Lines +/-
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                MRs Created
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                MRs Merged
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Reviews Given
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Avg Review Time
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {members.map((member) => (
              <tr key={member.team_member_id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{member.name}</div>
                      <div className="text-sm text-gray-500">@{member.username}</div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                  {member.commit_count}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                  <span className="text-green-600">+{member.lines_added}</span>
                  {' / '}
                  <span className="text-red-600">-{member.lines_deleted}</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                  {member.mrs_created}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                  <span className="text-green-600 font-medium">{member.mrs_merged}</span>
                  {member.mrs_closed > 0 && (
                    <span className="text-gray-400"> / {member.mrs_closed} closed</span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                  {member.reviews_given}
                  {member.review_comments > 0 && (
                    <span className="text-gray-400 text-xs ml-1">
                      ({member.review_comments} comments)
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                  {member.avg_review_time_hours !== null
                    ? member.avg_review_time_hours < 24
                      ? `${member.avg_review_time_hours.toFixed(1)}h`
                      : `${(member.avg_review_time_hours / 24).toFixed(1)}d`
                    : 'N/A'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>Total team members: {members.length}</span>
          <span>
            Total commits:{' '}
            {members.reduce((sum, m) => sum + m.commit_count, 0)}
          </span>
        </div>
      </div>
    </div>
  );
};

export default MemberActivityTable;
