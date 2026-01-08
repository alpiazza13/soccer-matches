export interface Competition {
  id: number;
  external_id: number;
  name: string;
  code: string;
  type: string;
  emblem: string | null;
}

export interface Team {
  id: number;
  external_id: number;
  name: string;
  short_name: string;
  tla: string;
  crest: string | null;
}

export interface Match {
  id: number;
  external_id: number;
  utc_date: string;
  status: string;
  matchday: number;
  stage: string;
  group: string | null;
  last_updated: string;
  score: any; // score is json column
  home_team: Team;
  away_team: Team;
  competition_id: number;
  is_done: boolean; 
}

export interface UserMatch {
  id: number;
  user_id: number;
  match_id: number;
  is_done: boolean;
  notes: string | null;
  match?: Match;
}