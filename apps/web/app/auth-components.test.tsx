import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AuthForm, ProtectedContent } from "./auth-components";

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
});
