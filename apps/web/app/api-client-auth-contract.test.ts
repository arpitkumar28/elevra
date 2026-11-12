import { describe, expect, it, vi } from "vitest";
import { ApiError, createApiClient } from "@elevra/api-client";

describe("shared API client auth response compatibility", () => {
  it("normalizes the FastAPI CurrentUser roles response for admin decisions", async () => {
    const fetcher = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        id: "admin-id",
        email: "admin@example.com",
        full_name: "Elevra Admin",
        roles: ["admin"],
        permissions: ["analytics:read"],
      }),
    });
    const client = createApiClient({
      baseUrl: "https://api.example.test/api/v1",
      fetch: fetcher as unknown as typeof fetch,
    });

    await expect(client.getMe("access-token")).resolves.toEqual({
      id: "admin-id",
      email: "admin@example.com",
      name: "Elevra Admin",
      role: "admin",
    });
    expect(fetcher).toHaveBeenCalledWith(
      "https://api.example.test/api/v1/auth/me",
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: "Bearer access-token" }),
      }),
    );
  });

  it("posts registration details to the live FastAPI contract with cookie credentials", async () => {
    const tokens = {
      access_token: "access-token",
      refresh_token: "refresh-token",
      token_type: "bearer" as const,
      expires_in: 900,
    };
    const fetcher = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(tokens), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    const client = createApiClient({
      baseUrl: "https://elevra-api-jrxa.onrender.com/api/v1",
      fetch: fetcher as unknown as typeof fetch,
    });

    await expect(
      client.register("Arpit Kumar", "arpit@example.com", "StrongPassword123"),
    ).resolves.toEqual(tokens);
    expect(fetcher).toHaveBeenCalledWith(
      "https://elevra-api-jrxa.onrender.com/api/v1/auth/register",
      expect.objectContaining({
        method: "POST",
        credentials: "include",
        body: JSON.stringify({
          name: "Arpit Kumar",
          email: "arpit@example.com",
          password: "StrongPassword123",
        }),
        headers: expect.objectContaining({ "Content-Type": "application/json" }),
      }),
    );
  });

  it("preserves the super-admin role and defaults an empty role list to student", async () => {
    const fetcher = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          id: "super-id",
          email: "root@example.com",
          full_name: "Root",
          roles: ["super_admin"],
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          id: "student-id",
          email: "student@example.com",
          full_name: "Student",
          roles: [],
        }),
      });
    const client = createApiClient({
      baseUrl: "https://api.example.test/api/v1",
      fetch: fetcher as unknown as typeof fetch,
    });

    await expect(client.getMe("super-token")).resolves.toMatchObject({ role: "super_admin" });
    await expect(client.getMe("student-token")).resolves.toMatchObject({ role: "student" });
  });

  it("rejects an incomplete identity instead of making a role decision", async () => {
    const fetcher = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ role: "admin" }),
    });
    const client = createApiClient({
      baseUrl: "https://api.example.test/api/v1",
      fetch: fetcher as unknown as typeof fetch,
    });

    await expect(client.getMe("access-token")).rejects.toBeInstanceOf(ApiError);
  });
});
