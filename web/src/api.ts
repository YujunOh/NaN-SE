// docs/orchestration/DASHBOARD_DESIGN.md의 API 계약과 일치하는 타입·fetch.

const BASE = import.meta.env.VITE_API_BASE ?? "";

export interface Stats {
  total_findings: number;
  total_cards: number;
  review: { accepted: number; rejected: number; pending: number };
  acceptance_rate: number | null;
  by_principle: { principle: string; count: number }[];
  by_severity: { severity: number; count: number }[];
  cards_over_time: { date: string; count: number }[];
}

export interface Finding {
  id: number;
  session_id: string;
  class_name: string;
  metric: string;
  value: number;
  threshold: number;
  principle: string;
  severity: number;
  source_file: string | null;
  source_line: number | null;
  created_at: string;
}

export interface CardSummary {
  id: string;
  principle: string;
  severity: number;
  violation_reason: string;
  user_accepted: boolean | null;
  source_file: string | null;
  source_line: number | null;
  generated_at: string;
  reviewed_at: string | null;
}

export interface CardDetail extends CardSummary {
  session_id: string;
  finding_id: number;
  code_hash: string;
  cost_example: string;
  before_code: string;
  after_code: string;
  learning_points: string[];
  revision_prompt: string;
  user_feedback: string | null;
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`${path}: ${res.status}`);
  return res.json() as Promise<T>;
}

export const api = {
  stats: () => get<Stats>("/api/stats"),
  findings: () => get<Finding[]>("/api/findings"),
  cards: (status = "all") => get<CardSummary[]>(`/api/cards?status=${status}`),
  card: (id: string) => get<CardDetail>(`/api/cards/${id}`),
};
