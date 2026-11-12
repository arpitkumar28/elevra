import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  EmailVerificationRecovery,
  PasswordResetRecovery,
} from "./auth-recovery-components";

describe("account recovery pages", () => {
  beforeEach(() => {
    window.history.pushState({}, "", "/");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ message: "Request accepted." }),
      }),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("requests a password reset without disclosing whether the account exists", async () => {
    render(<PasswordResetRecovery />);
    fireEvent.change(screen.getByLabelText("Email address"), {
      target: { value: "student@example.com" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Send password reset link" }));

    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(1));
    expect(String(vi.mocked(fetch).mock.calls[0][0])).toContain("/auth/password-reset/request");
    expect(screen.getByRole("status").textContent).toContain("Request accepted.");
  });

  it("submits a new password only after the reset link is opened", async () => {
    window.history.pushState({}, "", "/reset-password?token=one-time-token");
    render(<PasswordResetRecovery />);
    fireEvent.change(await screen.findByLabelText("New password"), {
      target: { value: "NewSecurePass123" },
    });
    fireEvent.change(screen.getByLabelText("Confirm new password"), {
      target: { value: "NewSecurePass123" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save new password" }));

    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(1));
    expect(String(vi.mocked(fetch).mock.calls[0][0])).toContain("/auth/password-reset/confirm");
    const options = vi.mocked(fetch).mock.calls[0][1] as RequestInit;
    expect(JSON.parse(String(options.body))).toEqual({
      token: "one-time-token",
      password: "NewSecurePass123",
    });
  });

  it("does not consume email-verification links until the user confirms", async () => {
    window.history.pushState({}, "", "/verify-email?token=verify-token");
    render(<EmailVerificationRecovery />);
    expect(await screen.findByRole("button", { name: "Verify email address" })).toBeDefined();
    expect(fetch).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole("button", { name: "Verify email address" }));
    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(1));
    expect(String(vi.mocked(fetch).mock.calls[0][0])).toContain("/auth/verify-email/confirm");
  });
});
