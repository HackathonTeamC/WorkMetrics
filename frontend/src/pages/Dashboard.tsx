import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/api';
import { Project } from '../types/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import FourKeysTab from '../components/four-keys/FourKeysTab';

const Dashboard: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.get<Project[]>('/projects');
      setProjects(data);
      if (data.length > 0 && !selectedProject) {
        setSelectedProject(data[0]);
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner message="Loading projects..." />
      </div>
    );
  }

  if (error) {
    return <ErrorMessage message={error} onRetry={fetchProjects} />;
  }

  if (projects.length === 0) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">No Projects Found</h2>
        <p className="text-gray-600 mb-6">
          Get started by adding your first GitLab project
        </p>
        <a
          href="/projects"
          className="inline-block px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Add Project
        </a>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Project Selector */}
      <div className="bg-white rounded-lg shadow p-4">
        <label htmlFor="project-select" className="block text-sm font-medium text-gray-700 mb-2">
          Select Project
        </label>
        <select
          id="project-select"
          value={selectedProject?.id || ''}
          onChange={(e) => {
            const project = projects.find((p) => p.id === parseInt(e.target.value));
            if (project) setSelectedProject(project);
          }}
          className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          {projects.map((project) => (
            <option key={project.id} value={project.id}>
              {project.name} (ID: {project.gitlab_id})
            </option>
          ))}
        </select>
      </div>

      {/* Four Keys Metrics */}
      {selectedProject && <FourKeysTab projectId={selectedProject.id} />}
    </div>
  );
};

export default Dashboard;
