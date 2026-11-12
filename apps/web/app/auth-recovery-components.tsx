"use client";

import Link from "next/link";
import React, { useEffect, useState } from "react";
import type { FormEvent } from "react";

const apiBaseUrl = (
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1"
).replace(/\/+$/, "");
const inputClass =
  "mt-1.5 w-full rounded-xl border border-[#d8e1da] bg-white px-4 py-3 text-sm outline-none focus:border-[#56816d] focus:ring-2 focus:ring-[#d5e7cf]";
const buttonClass =
  "w-full rounded-xl bg-[#145b48] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#103f34] disabled:cursor-wait disabled:opacity-60";

async function postAuth(path: string, body: Record<string, string>): Promise<{ message?: string }> {
  const response = await fetch(`${apiBaseUrl}/auth/${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const payload = (await response.json().catch(() => ({}))) as {
    message?: string;
    detail?: string;
    error?: { message?: string };
  };
  if (!response.ok) {
    throw new Error(
      payload.detail || payload.error?.message || payload.message || "The request could not be completed.",
    );
  }
  return payload;
}

function RecoveryShell({
  eyebrow,
  title,
  description,
  children,
}: {
  eyebrow: string;
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <main className="mx-auto max-w-2xl px-5 py-14 lg:px-8">
      <section className="rounded-3xl border border-[#e3e9e4] bg-white p-7 sm:p-9">
        <p className="text-xs font-bold uppercase tracking-[.16em] text-[#668b59]">{eyebrow}</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight">{title}</h1>
        <p className="mt-3 leading-7 text-[#63736c]">{description}</p>
        {children}
        <Link
          href="/login"
          className="mt-6 inline-flex text-sm font-semibold text-[#145b48] underline underline-offset-4"
        >
          Back to sign in
        </Link>
      </section>
    </main>
  );
}

export function PasswordResetRecovery() {
  const [token, setToken] = useState("");
  const [tokenReady, setTokenReady] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    setToken(new URLSearchParams(window.location.search).get("token") || "");
    setTokenReady(true);
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setMessage("");
    try {
      if (token) {
        if (password !== confirmPassword) throw new Error("The passwords do not match.");
        const result = await postAuth("password-reset/confirm", { token, password });
        setMessage(result.message || "Your password has been reset. You can sign in now.");
        setPassword("");
        setConfirmPassword("");
      } else {
        const result = await postAuth("password-reset/request", { email: email.trim() });
        setMessage(
          result.message ||
            "If the account exists, password reset instructions will be sent when email delivery is available.",
        );
      }
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to complete the request.");
    } finally {
      setBusy(false);
    }
  }

  if (!tokenReady) {
    return (
      <main className="mx-auto max-w-2xl px-5 py-20 text-sm text-[#63736c]" role="status">
        Preparing password reset…
      </main>
    );
  }

  return (
    <RecoveryShell
      eyebrow="Account recovery"
      title={token ? "Choose a new password" : "Reset your password"}
      description={
        token
          ? "Use a new password with at least 12 characters, including uppercase, lowercase and a number."
          : "Enter the email address associated with your Elevra account. The response is the same whether or not an account exists."
      }
    >
      <form className="mt-7 space-y-4" onSubmit={submit}>
        {token ? (
          <>
            <label className="block text-sm font-semibold" htmlFor="reset-password">
              New password
              <input
                id="reset-password"
                name="password"
                type="password"
                autoComplete="new-password"
                minLength={12}
                maxLength={128}
                pattern="(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9]).{12,128}"
                title="Use at least 12 characters with uppercase, lowercase and a number."
                required
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className={inputClass}
              />
            </label>
            <label className="block text-sm font-semibold" htmlFor="reset-confirm-password">
              Confirm new password
              <input
                id="reset-confirm-password"
                name="confirmPassword"
                type="password"
                autoComplete="new-password"
                minLength={12}
                maxLength={128}
                required
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                className={inputClass}
              />
            </label>
          </>
        ) : (
          <label className="block text-sm font-semibold" htmlFor="reset-email">
            Email address
            <input
              id="reset-email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className={inputClass}
            />
          </label>
        )}
        {error && (
          <p role="alert" className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
            {error}
          </p>
        )}
        {message && (
          <p role="status" className="rounded-xl bg-[#eef4e8] px-4 py-3 text-sm text-[#28483b]">
            {message}
          </p>
        )}
        <button className={buttonClass} disabled={busy}>
          {busy
            ? "Please wait…"
            : token
              ? "Save new password"
              : "Send password reset link"}
        </button>
      </form>
    </RecoveryShell>
  );
}

export function EmailVerificationRecovery() {
  const [token, setToken] = useState("");
  const [tokenReady, setTokenReady] = useState(false);
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    setToken(new URLSearchParams(window.location.search).get("token") || "");
    setTokenReady(true);
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const result = token
        ? await postAuth("verify-email/confirm", { token })
        : await postAuth("verify-email/request", { email: email.trim() });
      setMessage(
        result.message ||
          (token
            ? "Your email address has been verified."
            : "If the account exists, verification instructions will be sent when email delivery is available."),
      );
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to complete the request.");
    } finally {
      setBusy(false);
    }
  }

  if (!tokenReady) {
    return (
      <main className="mx-auto max-w-2xl px-5 py-20 text-sm text-[#63736c]" role="status">
        Preparing email verification…
      </main>
    );
  }

  return (
    <RecoveryShell
      eyebrow="Account verification"
      title={token ? "Verify your email address" : "Resend verification email"}
      description={
        token
          ? "Confirm that you control this email address. This link can only be used once and expires."
          : "Enter your Elevra email address and we’ll send a verification link when email delivery is configured."
      }
    >
      <form className="mt-7 space-y-4" onSubmit={submit}>
        {token ? (
          <p className="rounded-xl border border-[#e3e9e4] bg-[#f7faf7] px-4 py-3 text-sm text-[#63736c]">
            For your security, this page will not verify your email automatically. Select the button below to use the one-time link.
          </p>
        ) : (
          <label className="block text-sm font-semibold" htmlFor="verify-email">
            Email address
            <input
              id="verify-email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className={inputClass}
            />
          </label>
        )}
        {error && (
          <p role="alert" className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
            {error}
          </p>
        )}
        {message && (
          <p role="status" className="rounded-xl bg-[#eef4e8] px-4 py-3 text-sm text-[#28483b]">
            {message}
          </p>
        )}
        <button className={buttonClass} disabled={busy}>
          {busy ? "Please wait…" : token ? "Verify email address" : "Send verification link"}
        </button>
      </form>
    </RecoveryShell>
  );
}
