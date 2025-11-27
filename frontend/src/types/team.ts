export interface TeamMemberActivity {
  team_member_id: number;
  username: string;
  name: string;
  commit_count: number;
  lines_added: number;
  lines_deleted: number;
  mrs_created: number;
  mrs_merged: number;
  mrs_closed: number;
  reviews_given: number;
  review_comments: number;
  avg_review_time_hours: number | null;
}

export interface ReviewLoad {
  team_member_id: number;
  username: string;
  name: string;
  review_count: number;
  comment_count: number;
  review_load_percentage: number;
}

export interface TeamActivityData {
  period_start: string;
  period_end: string;
  team_members: TeamMemberActivity[];
  review_load: ReviewLoad[];
}

export interface TeamActivityQueryParams {
  start_date: string; // YYYY-MM-DD
  end_date: string; // YYYY-MM-DD
}
