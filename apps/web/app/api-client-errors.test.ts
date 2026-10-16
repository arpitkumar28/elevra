import { describe, expect, it, vi } from "vitest";
import { createApiClient } from "@elevra/api-client";

describe("API request failures", () => {
  it("points network-style fetch failures to connection, URL, or CORS configuration", async () => {
    const fetcher = vi.fn<typeof fetch>().mockRejectedValue(new TypeError("Failed to fetch"));
    const api = createApiClient({
      baseUrl: "https://elevra-api.example/api/v1",
      fetch: fetcher,
    });

    await expect(api.refreshSession()).rejects.toMatchObject({
      message:
        "Unable to reach Elevra. Check your connection, API URL, and the backend CORS allowlist.",
      status: 0,
    });
  });

  it("preserves HTTP authorization errors instead of reporting a connection failure", async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue(
      new Response(JSON.stringify({ detail: "Authentication failed" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      }),
    );
    const api = createApiClient({ baseUrl: "https://elevra-api.example", fetch: fetcher });

    await expect(api.refreshSession()).rejects.toMatchObject({
      message: "Authentication failed",
      status: 401,
    });
  });

  it("sends refresh as a credentialed POST to the normalized API path", async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue(
      new Response(
        JSON.stringify({
          access_token: "access",
          refresh_token: "refresh",
          token_type: "bearer",
          expires_in: 900,
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    const api = createApiClient({
      baseUrl: "https://elevra-api.example/api/v1/",
      fetch: fetcher,
    });

    await api.refreshSession();

    expect(fetcher).toHaveBeenCalledWith(
      "https://elevra-api.example/api/v1/auth/refresh",
      expect.objectContaining({ method: "POST", credentials: "include" }),
    );
  });
});
