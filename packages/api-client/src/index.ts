// Lightweight API client shared by browser apps. Service clients can be generated from OpenAPI later.
import {
  OpportunitySchema,
  StudentProfileSchema,
  type Opportunity,
  type StudentProfile,
} from "@elevra/shared";

export type ApiClientOptions = {
  baseUrl: string;
  accessToken?: string;
};

export class ElevraApiClient {
  private readonly baseUrl: string;
  private readonly accessToken?: string;

  constructor(options: ApiClientOptions) {
    this.baseUrl = options.baseUrl.replace(/\/$/, "");
    this.accessToken = options.accessToken;
  }

  async getCurrentStudent(): Promise<StudentProfile> {
    const response = await this.request("/api/v1/auth/me");
    return StudentProfileSchema.parse(await response.json());
  }

  async listOpportunities(params?: { query?: string; country?: string }): Promise<Opportunity[]> {
    const searchParams = new URLSearchParams();
    if (params?.query) searchParams.set("query", params.query);
    if (params?.country) searchParams.set("country", params.country);

    const response = await this.request(`/api/v1/opportunities?${searchParams.toString()}`);
    const payload = (await response.json()) as { data: unknown[] };
    return payload.data.map((item) => OpportunitySchema.parse(item));
  }

  private async request(path: string, init?: RequestInit): Promise<Response> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      ...init,
      headers: {
        "content-type": "application/json",
        ...(this.accessToken ? { authorization: `Bearer ${this.accessToken}` } : {}),
        ...init?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`Elevra API request failed: ${response.status}`);
    }

    return response;
  }
}
