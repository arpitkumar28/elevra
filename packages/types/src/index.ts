export interface AppRoute {
  slug: string;
  title: string;
  description: string;
}
export interface UserSummary {
  id: string;
  name: string;
  email: string;
}
export interface ExamSummary {
  id: string;
  slug: string;
  name: string;
  category: string;
  verified: boolean;
}
export interface OpportunitySummary {
  id: string;
  slug: string;
  title: string;
  type: string;
  verified: boolean;
}
