import { apiClient } from './api';
import { CycleTimeData, CycleTimeQueryParams } from '../types/cycleTime';

export class CycleTimeService {
  async getCycleTime(
    projectId: number,
    params: CycleTimeQueryParams
  ): Promise<CycleTimeData> {
    return await apiClient.get<CycleTimeData>(
      `/projects/${projectId}/cycle-time`,
      { params }
    );
  }
}

export const cycleTimeService = new CycleTimeService();
