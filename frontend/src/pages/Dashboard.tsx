import React from 'react';
import LoadingSpinner from '../components/common/LoadingSpinner';

const Dashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
        <p className="mt-2 text-gray-600">
          View your GitLab project metrics and team performance
        </p>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-600">
          Phase 2 foundational setup complete. User stories will be implemented in Phase 3+.
        </p>
      </div>
    </div>
  );
};

export default Dashboard;
