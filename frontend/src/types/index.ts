export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface CandidateProfile {
  id: string;
  user_id: string;
  headline?: string;
  summary?: string;
  total_experience_years: number;
  current_role?: string;
  skills: string[];
  location?: string;
  education: Array<{ degree: string; institution: string; year?: string }>;
  experience: Array<{ role: string; company: string; duration?: string; description?: string }>;
  projects: Array<{ title: string; description?: string; technologies?: string[] }>;
  created_at: string;
  updated_at: string;
}

export interface JobSkill {
  id: string;
  skill_name: string;
  is_required: boolean;
  importance_weight: number;
}

export interface Job {
  id: string;
  title: string;
  company: string;
  description: string;
  location: string;
  remote_policy: 'REMOTE' | 'HYBRID' | 'ONSITE';
  job_type: string;
  min_salary?: number;
  max_salary?: number;
  currency: string;
  experience_level: 'ENTRY' | 'MID' | 'SENIOR' | 'LEAD';
  skills: JobSkill[];
  created_at: string;
}

export interface ScoreBreakdown {
  skill_overlap_score: number;
  semantic_score: number;
  role_score: number;
  location_score: number;
  preference_score: number;
}

export interface Recommendation {
  id: string;
  job: Job;
  match_score: number;
  score_breakdown: ScoreBreakdown;
  matching_skills: string[];
  missing_skills: string[];
  generated_at: string;
}

export interface SavedJob {
  id: string;
  user_id: string;
  job_id: string;
  status: 'SAVED' | 'APPLIED' | 'INTERVIEWING' | 'OFFERED' | 'REJECTED';
  notes?: string;
  job: Job;
  created_at: string;
}

export interface UserPreferences {
  id: string;
  user_id: string;
  desired_roles: string[];
  preferred_locations: string[];
  remote_only: boolean;
  min_salary?: number;
  max_salary?: number;
  preferred_industries: string[];
}

export interface ToolCallExecution {
  tool: string;
  args: Record<string, any>;
  result: any;
}

export interface ChatMessage {
  id?: string;
  role: 'user' | 'assistant' | 'tool' | 'system';
  content: string;
  tool_calls?: ToolCallExecution[];
  created_at?: string;
}
