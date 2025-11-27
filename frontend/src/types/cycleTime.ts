export interface StageStats {
  name: string;
  mean: number;
  median: number;
  p75: number;
  p90: number;
  min: number;
  max: number;
}

export interface StageBreakdown {
  coding_percentage: number;
  review_percentage: number;
  deployment_percentage: number;
}

export interface CycleTimeMetrics {
  count: number;
  stages: {
    coding: StageStats;
    review: StageStats;
    deployment: StageStats;
  };
  total: StageStats;
  stage_breakdown_avg: StageBreakdown;
}

export interface CycleTimeDistributionItem {
  mr_id: number;
  title: string;
  merged_at: string | null;
  coding_time: number;
  review_time: number;
  deployment_time: number;
  total_time: number;
}

export interface CycleTimeData {
  period_start: string;
  period_end: string;
  metrics: CycleTimeMetrics;
  distribution: CycleTimeDistributionItem[];
}

export interface CycleTimeQueryParams {
  start_date: string; // YYYY-MM-DD
  end_date: string; // YYYY-MM-DD
}
