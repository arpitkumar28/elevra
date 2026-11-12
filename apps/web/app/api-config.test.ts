import { describe, expect, it } from "vitest";
import {
  LOCAL_API_BASE_URL,
  PRODUCTION_API_BASE_URL,
  resolveApiBaseUrl,
} from "./api-config";

describe("API base URL configuration", () => {
  it("uses an explicitly configured API URL for each deployment environment", () => {
    expect(resolveApiBaseUrl("https://api.custom.example/api/v1", "production")).toBe(
      "https://api.custom.example/api/v1",
    );
  });

  it("uses the live Render API for production when no override is configured", () => {
    expect(resolveApiBaseUrl(undefined, "production")).toBe(PRODUCTION_API_BASE_URL);
    expect(resolveApiBaseUrl("   ", "production")).toBe(PRODUCTION_API_BASE_URL);
  });

  it("rejects stale localhost and non-HTTPS overrides in production", () => {
    expect(resolveApiBaseUrl("http://localhost:8000/api/v1", "production")).toBe(
      PRODUCTION_API_BASE_URL,
    );
    expect(resolveApiBaseUrl("https://127.0.0.1:8000/api/v1", "production")).toBe(
      PRODUCTION_API_BASE_URL,
    );
    expect(resolveApiBaseUrl("http://api.example.test/api/v1", "production")).toBe(
      PRODUCTION_API_BASE_URL,
    );
    expect(resolveApiBaseUrl("not-a-url", "production")).toBe(PRODUCTION_API_BASE_URL);
  });

  it("keeps local development and tests pointed at the local FastAPI server", () => {
    expect(resolveApiBaseUrl(undefined, "development")).toBe(LOCAL_API_BASE_URL);
    expect(resolveApiBaseUrl(undefined, "test")).toBe(LOCAL_API_BASE_URL);
  });
});
