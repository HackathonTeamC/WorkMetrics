export interface FourKeysMetrics {
  period_start: string;
  period_end: string;
  deployment_frequency: number;
  deployment_count: number;
  lead_time_hours: number | null;
  lead_time_median_hours: number | null;
  change_failure_rate: number | null;
  failed_deployment_count: number;
  time_to_restore_hours: number | null;
  time_to_restore_median_hours: number | null;
}

export interface MetricsQueryParams {
  start_date: string; // YYYY-MM-DD
  end_date: string; // YYYY-MM-DD
}

export interface DeploymentFrequencyData {
  date: string;
  count: number;
}

export interface LeadTimeData {
  deployment: string;
  hours: number;
}

export interface ChangeFailureData {
  status: string;
  count: number;
  percentage: number;
}

export interface TimeToRestoreData {
  incident: string;
  hours: number;
}
