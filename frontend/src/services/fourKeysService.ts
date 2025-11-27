import { apiClient } from './api';
import { FourKeysMetrics, MetricsQueryParams } from '../types/metrics';

export class FourKeysService {
  async getFourKeysMetrics(
    projectId: number,
    params: MetricsQueryParams
  ): Promise<FourKeysMetrics> {
    return await apiClient.get<FourKeysMetrics>(
      `/projects/${projectId}/four-keys`,
      { params }
    );
  }
}

export const fourKeysService = new FourKeysService();
