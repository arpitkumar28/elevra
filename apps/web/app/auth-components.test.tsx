import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AuthForm, HeaderAuthControls, ProtectedContent } from "./auth-components";

const mocks = vi.hoisted(() => ({
  useAuth: vi.fn(),
  replace: vi.fn(),
}));

vi.mock("./auth-provider", () => ({ useAuth: mocks.useAuth }));
vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: mocks.replace }),
  usePathname: () => "/dashboard",
}));

describe("auth routes", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mocks.useAuth.mockReturnValue({
      status: "unauthenticated",
      user: null,
      signIn: vi.fn().mockResolvedValue(undefined),
      signUp: vi.fn().mockResolvedValue(undefined),
      signOut: vi.fn(),
    });
  });

  it("submits the login form and provides an accessible response", async () => {
    const signIn = vi.fn().mockResolvedValue(undefined);
    mocks.useAuth.mockReturnValue({
      status: "unauthenticated",
      user: null,
      signIn,
      signUp: vi.fn(),
      signOut: vi.fn(),
    });
    render(<AuthForm mode="login" />);
    fireEvent.change(screen.getByLabelText("Email address"), {
      target: { value: "student@example.com" },
    });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "SecurePass123" } });
    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));
    await waitFor(() =>
      expect(signIn).toHaveBeenCalledWith("student@example.com", "SecurePass123"),
    );
  });

  it("redirects a protected account route to login when no session exists", async () => {
    render(
      <ProtectedContent>
        <p>Private dashboard</p>
      </ProtectedContent>,
    );
    await waitFor(() => expect(mocks.replace).toHaveBeenCalledWith("/login?next=%2Fdashboard"));
    expect(screen.queryByText("Private dashboard")).toBeNull();
  });

  it("renders protected content only for an authenticated user", () => {
    mocks.useAuth.mockReturnValue({
      status: "authenticated",
      user: { email: "student@example.com" },
    });
    render(
      <ProtectedContent>
        <p>Private dashboard</p>
      </ProtectedContent>,
    );
    expect(screen.getByText("Private dashboard")).toBeDefined();
  });

  it("shows the admin navigation link only for a backend-verified admin role", () => {
    mocks.useAuth.mockReturnValue({
      status: "authenticated",
      user: { id: "admin-id", name: "Admin", email: "admin@example.com", role: "admin" },
      signOut: vi.fn(),
    });
    const { rerender } = render(<HeaderAuthControls />);
    expect(screen.getByRole("link", { name: "Admin Panel" }).getAttribute("href")).toBe(
      "http://localhost:3002",
    );

    mocks.useAuth.mockReturnValue({
      status: "authenticated",
      user: { id: "student-id", name: "Student", email: "student@example.com", role: "student" },
      signOut: vi.fn(),
    });
    rerender(<HeaderAuthControls />);
    expect(screen.queryByRole("link", { name: "Admin Panel" })).toBeNull();
  });
});
