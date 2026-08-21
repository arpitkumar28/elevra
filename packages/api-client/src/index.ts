export type Exam = {
  id: string;
  slug: string;
  name: string;
  category: string;
  conducting_body?: string;
  short_description?: string;
  description?: string;
  application_start?: string;
  application_deadline?: string;
  exam_date?: string;
  result_date?: string;
  official_website?: string;
  source_url?: string;
  source_name?: string;
  verified: boolean;
  verified_at?: string;
  status: string;
};
export type Opportunity = {
  id: string;
  slug: string;
  title: string;
  type: string;
  organization?: string;
  description?: string;
  eligibility?: string;
  location?: string;
  remote?: boolean;
  deadline?: string;
  application_url?: string;
  source_url?: string;
  verified: boolean;
  verified_at?: string;
  status: string;
};
export type Page<T> = {
  items: T[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
};

const timeout = 10000;
export type ApiClientOptions = { baseUrl: string; fetch?: typeof fetch };
export class ApiError extends Error {
  constructor(
    message: string,
    public status = 0,
  ) {
    super(message);
  }
}
export function createApiClient({ baseUrl, fetch: fetcher = fetch }: ApiClientOptions) {
  // The public deployment contract includes the API version, e.g.
  // https://api.example.com/api/v1. Accept the old host-only value while
  // applications transition without ever adding the version twice.
  const normalizedBaseUrl = baseUrl.replace(/\/$/, "").endsWith("/api/v1")
    ? baseUrl.replace(/\/$/, "")
    : `${baseUrl.replace(/\/$/, "")}/api/v1`;
  async function request<T>(path: string, init?: RequestInit): Promise<T> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeout);
    try {
      const response = await fetcher(`${normalizedBaseUrl}${path}`, {
        ...init,
        signal: controller.signal,
        headers: { "Content-Type": "application/json", ...init?.headers },
      });
      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new ApiError(
          body.detail || "Something went wrong. Please try again.",
          response.status,
        );
      }
      return response.status === 204 ? (undefined as T) : response.json();
    } catch (error) {
      if (error instanceof ApiError) throw error;
      throw new ApiError("Unable to reach Elevra. Check your connection and try again.");
    } finally {
      clearTimeout(timer);
    }
  }
  function query(params: Record<string, string | number | boolean | undefined>) {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => v !== undefined && v !== "" && q.set(k, String(v)));
    return q.toString() ? `?${q}` : "";
  }
  return {
    getHealth: () => fetcher(`${normalizedBaseUrl}/health`).then((r) => r.json()),
    listExams: (params: Record<string, string | number | boolean | undefined> = {}) =>
      request<Page<Exam>>(`/exams${query(params)}`),
    getExam: (slug: string) => request<Exam>(`/exams/${slug}`),
    listOpportunities: (params: Record<string, string | number | boolean | undefined> = {}) =>
      request<Page<Opportunity>>(`/opportunities${query(params)}`),
    getOpportunity: (slug: string) => request<Opportunity>(`/opportunities/${slug}`),
    createExam: (data: Partial<Exam>, token: string) =>
      request<Exam>("/exams", {
        method: "POST",
        body: JSON.stringify(data),
        headers: { Authorization: `Bearer ${token}` },
      }),
    updateExam: (id: string, data: Partial<Exam>, token: string) =>
      request<Exam>(`/exams/${id}`, {
        method: "PATCH",
        body: JSON.stringify(data),
        headers: { Authorization: `Bearer ${token}` },
      }),
    createOpportunity: (data: Partial<Opportunity>, token: string) =>
      request<Opportunity>("/opportunities", {
        method: "POST",
        body: JSON.stringify(data),
        headers: { Authorization: `Bearer ${token}` },
      }),
    updateOpportunity: (id: string, data: Partial<Opportunity>, token: string) =>
      request<Opportunity>(`/opportunities/${id}`, {
        method: "PATCH",
        body: JSON.stringify(data),
        headers: { Authorization: `Bearer ${token}` },
      }),
  };
}
