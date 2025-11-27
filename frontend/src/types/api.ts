export interface HealthResponse {
  status: string;
  database: string;
  service: string;
}

export interface ErrorResponse {
  error: string;
  message: string;
  detail?: string;
}

export interface ApiResponse<T> {
  data?: T;
  error?: ErrorResponse;
}

export interface TimeRange {
  start: string; // ISO date string
  end: string; // ISO date string
}

export interface PaginationParams {
  page?: number;
  per_page?: number;
}

export interface Project {
  id: number;
  gitlab_id: number;
  name: string;
  url: string;
  last_synced_at?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateProjectRequest {
  gitlab_id: number;
  name: string;
  url: string;
}
