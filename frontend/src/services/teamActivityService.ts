import { apiClient } from './api';
import { TeamActivityData, TeamActivityQueryParams } from '../types/team';

export class TeamActivityService {
  async getTeamActivity(
    projectId: number,
    params: TeamActivityQueryParams
  ): Promise<TeamActivityData> {
    return await apiClient.get<TeamActivityData>(
      `/projects/${projectId}/team-activity`,
      { params }
    );
  }
}

export const teamActivityService = new TeamActivityService();
