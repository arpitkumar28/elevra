import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError } from "@elevra/api-client";
import { AuthProvider, useAuth } from "./auth-provider";

const api = vi.hoisted(() => ({
  login: vi.fn(),
  register: vi.fn(),
  refreshSession: vi.fn(),
  logout: vi.fn(),
  getMe: vi.fn(),
}));

vi.mock("@elevra/api-client", () => ({
  ApiError: class ApiError extends Error {
    status: number;
    constructor(message: string, status = 0) {
      super(message);
      this.status = status;
    }
  },
  createApiClient: () => api,
}));

function Probe() {
  const auth = useAuth();
  return (
    <div>
      <p>
        {auth.status}:{auth.user?.email || "signed-out"}
      </p>
      <button
        onClick={() =>
          void auth.signIn("student@example.com", "SecurePass123").catch(() => undefined)
        }
      >
        Sign in
      </button>
      <button onClick={() => void auth.signOut()}>Sign out</button>
    </div>
  );
}

describe("student auth session", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.refreshSession.mockResolvedValue({
      access_token: "access-cookie-restored",
      refresh_token: "ignored-refresh",
      expires_in: 900,
    });
    api.getMe.mockResolvedValue({
      id: "user-1",
      email: "student@example.com",
      name: "Student",
      role: "student",
    });
    api.login.mockResolvedValue({
      access_token: "access-login",
      refresh_token: "ignored-refresh",
      expires_in: 900,
    });
    api.logout.mockResolvedValue({ message: "logged out" });
  });

  it("restores a session through the refresh endpoint and keeps the refresh token out of app state", async () => {
    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    );
    expect(await screen.findByText("authenticated:student@example.com")).toBeDefined();
    expect(api.refreshSession).toHaveBeenCalledOnce();
    expect(api.getMe).toHaveBeenCalledWith("access-cookie-restored");
    expect(window.localStorage.length).toBe(0);
    expect(window.sessionStorage.length).toBe(0);
  });

  it("signs in, signs out through the API, and clears the in-memory session", async () => {
    api.refreshSession.mockRejectedValue(new ApiError("No session", 401));
    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    );
    await screen.findByText("unauthenticated:signed-out");

    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));
    await screen.findByText("authenticated:student@example.com");
    expect(api.login).toHaveBeenCalledWith("student@example.com", "SecurePass123");
    expect(api.getMe).toHaveBeenCalledWith("access-login");

    fireEvent.click(screen.getByRole("button", { name: "Sign out" }));
    await waitFor(() => expect(api.logout).toHaveBeenCalledWith("access-login"));
    await screen.findByText("unauthenticated:signed-out");
  });
});
