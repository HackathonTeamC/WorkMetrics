import { useEffect, useState } from 'react';
import { FourKeysMetrics, MetricsQueryParams } from '../types/metrics';
import { fourKeysService } from '../services/fourKeysService';

interface UseMetricsResult {
  metrics: FourKeysMetrics | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useMetrics(
  projectId: number | null,
  params: MetricsQueryParams
): UseMetricsResult {
  const [metrics, setMetrics] = useState<FourKeysMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = async () => {
    if (!projectId) {
      setMetrics(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await fourKeysService.getFourKeysMetrics(projectId, params);
      setMetrics(data);
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || err.message || 'Failed to fetch metrics';
      setError(errorMessage);
      console.error('Error fetching metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, [projectId, params.start_date, params.end_date]);

  return {
    metrics,
    loading,
    error,
    refetch: fetchMetrics,
  };
}
