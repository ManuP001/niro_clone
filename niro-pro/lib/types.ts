export type TopicKey =
  | "career" | "romantic_relationships" | "marriage_partnership"
  | "money" | "health_energy" | "family_home" | "spirituality"
  | "self_psychology" | "friends_social" | "learning_education"
  | "travel_relocation" | "legal_contracts" | "daily_guidance" | "general";

export interface Practitioner {
  id: string;
  full_name: string;
  primary_tradition: string;
  languages: string[];
  years_of_practice: number;
  credential_education?: string;
  city: string;
  philosophy: string;
  short_bio: string;
  primary_topic: TopicKey;
  secondary_topics: TopicKey[];
  typical_availability?: string;
  max_sessions_per_week: number;
  status: "pending" | "approved";
  conversion_rate: number;
  total_revenue_inr: number;
  average_rating: number;
  total_sessions: number;
  photo_url: string | null;
}

export interface Package {
  id: string;
  name: string;
  who_its_for: string;
  topic: TopicKey;
  outcomes: [string, string, string];
  duration_days: 15 | 30 | 60 | 90;
  sessions_included: 1 | 2 | 3 | 4;
  price_inr: number;
  is_intro_template: boolean;
}

export interface Lead {
  id: string;
  client_name: string;
  life_area: TopicKey;
  question: string;
  niro_ai_context: string;
  chart: {
    ascendant: string;
    moon_sign: string;
    current_mahadasha: string;
    mahadasha_end: string;
  } | null;
  top_transits: string[];
  focus_factors: { rule: string; summary: string }[];
  flat_fee_inr: number;
  expires_in_seconds: number;
  status: "pending" | "accepted" | "declined" | "expired";
}

export interface Session {
  id: string;
  lead_id: string;
  client_name: string;
  life_area: TopicKey;
  question: string;
  niro_ai_context: string;
  chart: Lead["chart"];
  top_transits: string[];
  focus_factors: Lead["focus_factors"];
  status: "scheduled" | "in_progress" | "completed";
}

export interface EarningsRow {
  date: string;
  client: string;
  package: string;
  gross_inr: number;
  fee_inr: number;
  net_inr: number;
}

export interface Notification {
  id: string;
  type: "follow_up_prompt";
  message: string;
  client_name: string;
  suggested_package: string;
  created_at: string;
  whatsapp_template: string;
}

export interface IdentityForm {
  full_name: string;
  primary_tradition: string;
  languages: string[];
  years_of_practice: number;
  credential_education?: string;
  city: string;
}

export interface StoryForm {
  philosophy: string;
  short_bio: string;
}

export interface SpecializationsForm {
  primary_topic: TopicKey;
  secondary_topics: TopicKey[];
  typical_availability?: string;
  max_sessions_per_week: number;
}
