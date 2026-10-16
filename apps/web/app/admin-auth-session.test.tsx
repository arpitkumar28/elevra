import React, { useEffect } from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError } from "@elevra/api-client";
import { AdminAuth } from "../../admin/app/admin-auth";
import { useAuth } from "./auth-provider";

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

function ExpireSessionOnMount() {
  const { withSession } = useAuth();
  useEffect(() => {
    void withSession(async () => {
      throw new ApiError("Access token expired", 401);
    }).catch(() => undefined);
  }, [withSession]);
  return <p>Private admin content</p>;
}

describe("admin authentication session discovery", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.refreshSession.mockRejectedValue(new ApiError("refresh token required", 401));
    api.login.mockResolvedValue({
      access_token: "admin-access",
      refresh_token: "http-only-cookie-is-set-by-api",
      expires_in: 900,
    });
    api.getMe.mockResolvedValue({
      id: "admin-1",
      email: "admin@example.com",
      name: "Admin",
      role: "admin",
    });
    api.logout.mockResolvedValue({ message: "logged out" });
  });

  it("shows sign-in without a fatal error when the browser has no refresh cookie", async () => {
    render(
      <AdminAuth>
        <p>Private admin content</p>
      </AdminAuth>,
    );

    expect(await screen.findByRole("heading", { name: "Admin sign in" })).toBeDefined();
    expect(screen.queryByRole("alert")).toBeNull();
    expect(screen.queryByText("Session unavailable")).toBeNull();
  });

  it("establishes an admin session after valid credentials", async () => {
    render(
      <AdminAuth>
        <p>Private admin content</p>
      </AdminAuth>,
    );

    await screen.findByRole("heading", { name: "Admin sign in" });
    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "admin@example.com" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "ValidPassword123" } });
    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

    expect(await screen.findByText("Private admin content")).toBeDefined();
    expect(api.login).toHaveBeenCalledWith("admin@example.com", "ValidPassword123");
    expect(api.getMe).toHaveBeenCalledWith("admin-access");
  });

  it("shows the authentication response for invalid credentials", async () => {
    api.login.mockRejectedValueOnce(new ApiError("Authentication failed", 401));
    render(
      <AdminAuth>
        <p>Private admin content</p>
      </AdminAuth>,
    );

    await screen.findByRole("heading", { name: "Admin sign in" });
    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "admin@example.com" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "wrong-password" } });
    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

    expect((await screen.findByRole("alert")).textContent).toContain("Authentication failed");
    expect(screen.queryByText("Private admin content")).toBeNull();
  });

  it("does not expose admin content to a signed-in non-admin", async () => {
    api.getMe.mockResolvedValueOnce({
      id: "student-1",
      email: "student@example.com",
      name: "Student",
      role: "student",
    });
    render(
      <AdminAuth>
        <p>Private admin content</p>
      </AdminAuth>,
    );

    await screen.findByRole("heading", { name: "Admin sign in" });
    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "student@example.com" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "ValidPassword123" } });
    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

    expect(
      await screen.findByRole("heading", { name: "Administrator access required" }),
    ).toBeDefined();
    expect(screen.queryByText("Private admin content")).toBeNull();
  });

  it("returns to sign-in when an authenticated session expires and refresh is rejected", async () => {
    api.refreshSession
      .mockRejectedValueOnce(new ApiError("refresh token required", 401))
      .mockRejectedValueOnce(new ApiError("Authentication failed", 401));
    render(
      <AdminAuth>
        <ExpireSessionOnMount />
      </AdminAuth>,
    );

    await screen.findByRole("heading", { name: "Admin sign in" });
    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "admin@example.com" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "ValidPassword123" } });
    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

    await waitFor(() => expect(api.refreshSession).toHaveBeenCalledTimes(2));
    expect(await screen.findByRole("heading", { name: "Admin sign in" })).toBeDefined();
    expect(screen.queryByText("Private admin content")).toBeNull();
    expect(screen.queryByRole("alert")).toBeNull();
  });
});
