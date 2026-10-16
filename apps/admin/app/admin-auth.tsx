"use client";

import { useState, type FormEvent, type ReactNode } from "react";
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
      <section className="max-w-xl rounded-2xl bg-white p-8">
        <h1 className="text-2xl font-bold">Session unavailable</h1>
        <p className="mt-2">{error}</p>
        <button
          className="mt-5 rounded-lg bg-[#145b48] px-4 py-2 text-white"
          onClick={() => void retryRestore().catch(() => undefined)}
        >
          Try again
        </button>
      </section>
    );
  if (status !== "authenticated" || !user)
    return (
      <main className="mx-auto mt-16 max-w-md rounded-2xl bg-white p-8 shadow-sm">
        <h1 className="text-2xl font-bold">Admin sign in</h1>
        <p className="mt-2 text-sm text-slate-600">Sign in with an Elevra administrator account.</p>
        <form onSubmit={submit} className="mt-6 space-y-4">
          <label className="block text-sm font-medium">
            Email
            <input
              className="mt-1 w-full rounded-lg border px-3 py-2"
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
              className="mt-1 w-full rounded-lg border px-3 py-2"
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
            className="w-full rounded-lg bg-[#145b48] px-4 py-3 font-semibold text-white disabled:opacity-60"
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
