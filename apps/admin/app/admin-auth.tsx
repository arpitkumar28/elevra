"use client";

import React, { useState, type FormEvent, type ReactNode } from "react";
import { AuthProvider, useAuth } from "../../web/app/auth-provider";

function AdminSession({ children }: { children: ReactNode }) {
  const { status, user, signIn, signOut, retryRestore, error } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [formError, setFormError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setFormError("");
    try {
      await signIn(email.trim(), password);
      setPassword("");
    } catch (cause) {
      setFormError(cause instanceof Error ? cause.message : "Unable to sign in.");
    } finally {
      setBusy(false);
    }
  }

  if (status === "loading")
    return (
      <p role="status" className="p-8">
        Restoring administrator session…
      </p>
    );
  if (status === "error")
    return (
      <section className="max-w-xl rounded-3xl border border-[#e1e8e1] bg-white p-8 shadow-[0_18px_48px_rgba(25,54,39,.08)]">
        <h1 className="text-2xl font-bold">Session unavailable</h1>
        <p className="mt-2">{error}</p>
        <button
          className="mt-5 rounded-xl bg-[#155b48] px-4 py-2.5 font-semibold text-white transition hover:bg-[#104537]"
          onClick={() => void retryRestore().catch(() => undefined)}
        >
          Try again
        </button>
      </section>
    );
  if (status !== "authenticated" || !user)
    return (
      <main className="mx-auto mt-12 max-w-md rounded-3xl border border-[#e1e8e1] bg-white p-8 shadow-[0_18px_48px_rgba(25,54,39,.08)] sm:mt-20 sm:p-10">
        <span className="grid h-11 w-11 place-items-center rounded-2xl bg-[#155b48] text-lg font-black text-[#dce9d1]">
          e
        </span>
        <h1 className="text-2xl font-bold">Admin sign in</h1>
        <p className="mt-2 text-sm text-slate-600">Sign in with an Elevra administrator account.</p>
        <form onSubmit={submit} className="mt-6 space-y-4">
          <label className="block text-sm font-medium">
            Email
            <input
              className="mt-1 w-full rounded-xl border border-[#d8e1da] bg-white px-3.5 py-3 outline-none transition focus:border-[#56816d] focus:ring-2 focus:ring-[#d5e7cf]"
              type="email"
              autoComplete="username"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </label>
          <label className="block text-sm font-medium">
            Password
            <input
              className="mt-1 w-full rounded-xl border border-[#d8e1da] bg-white px-3.5 py-3 outline-none transition focus:border-[#56816d] focus:ring-2 focus:ring-[#d5e7cf]"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>
          {(formError || error) && (
            <p role="alert" className="text-sm text-red-700">
              {formError || error}
            </p>
          )}
          <button
            disabled={busy}
            className="w-full rounded-xl bg-[#155b48] px-4 py-3 font-semibold text-white shadow-sm transition hover:bg-[#104537] disabled:cursor-not-allowed disabled:opacity-60"
          >
            {busy ? "Signing in…" : "Sign in"}
          </button>
        </form>
      </main>
    );
  if (user.role !== "admin" && user.role !== "super_admin")
    return (
      <main className="mx-auto mt-16 max-w-xl rounded-2xl bg-white p-8">
        <h1 className="text-2xl font-bold">Administrator access required</h1>
        <p className="mt-2">The signed-in account does not have an administrator role.</p>
        <button onClick={() => void signOut()} className="mt-5 rounded-lg border px-4 py-2">
          Sign out
        </button>
      </main>
    );
  return <>{children}</>;
}

export function AdminAuth({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <AdminSession>{children}</AdminSession>
    </AuthProvider>
  );
}
