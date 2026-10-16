"use client";

import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import React, { useEffect, useState } from "react";
import type { FormEvent } from "react";
import type { Route } from "next";
import { useAuth } from "./auth-provider";

const fieldClass =
  "mt-1.5 w-full rounded-xl border border-[#d8e1da] bg-white px-4 py-3 text-sm text-[#14231f] outline-none transition placeholder:text-slate-400 focus:border-[#56816d] focus:ring-2 focus:ring-[#d5e7cf]";

export function AuthForm({ mode }: { mode: "login" | "register" }) {
  const router = useRouter();
  const { status, user, signIn, signUp } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const registering = mode === "register";

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      if (registering) await signUp(name.trim(), email.trim(), password);
      else await signIn(email.trim(), password);
      setPassword("");
      const requested = new URLSearchParams(window.location.search).get("next");
      const next =
        requested?.startsWith("/") && !requested.startsWith("//") ? requested : "/dashboard";
      router.replace(next as Route);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to sign in. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  if (status === "authenticated" && user) {
    return (
      <main className="mx-auto max-w-3xl px-5 py-16 lg:px-8">
        <section className="rounded-3xl border border-[#e3e9e4] bg-white p-8">
          <p className="text-xs font-bold uppercase tracking-[.16em] text-[#668b59]">Account</p>
          <h1 className="mt-3 text-3xl font-semibold">You’re already signed in.</h1>
          <p className="mt-3 text-[#63736c]">Signed in as {user.email}.</p>
          <Link
            href="/dashboard"
            className="mt-6 inline-flex rounded-xl bg-[#145b48] px-5 py-3 text-sm font-semibold text-white"
          >
            Go to your dashboard
          </Link>
        </section>
      </main>
    );
  }

  return (
    <main className="mx-auto grid min-h-[65vh] max-w-6xl items-center gap-10 px-5 py-12 md:grid-cols-[1fr_.8fr] lg:px-8">
      <section>
        <p className="text-xs font-bold uppercase tracking-[.16em] text-[#668b59]">
          {registering ? "Start your journey" : "Welcome back"}
        </p>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">
          {registering ? "Create your account" : "Sign in to Elevra"}
        </h1>
        <p className="mt-4 max-w-lg leading-7 text-[#63736c]">
          {registering
            ? "Save opportunities, track applications and keep your preparation profile together."
            : "Continue with your saved opportunities, applications and profile."}
        </p>
        <form className="mt-8 max-w-md space-y-4" onSubmit={submit}>
          {registering && (
            <div>
              <label htmlFor="auth-name" className="text-sm font-semibold">
                Your name
              </label>
              <input
                id="auth-name"
                name="name"
                autoComplete="name"
                minLength={2}
                maxLength={255}
                required
                value={name}
                onChange={(event) => setName(event.target.value)}
                className={fieldClass}
              />
            </div>
          )}
          <div>
            <label htmlFor="auth-email" className="text-sm font-semibold">
              Email address
            </label>
            <input
              id="auth-email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className={fieldClass}
            />
          </div>
          <div>
            <label htmlFor="auth-password" className="text-sm font-semibold">
              Password
            </label>
            <input
              id="auth-password"
              name="password"
              type="password"
              autoComplete={registering ? "new-password" : "current-password"}
              minLength={registering ? 12 : 1}
              maxLength={128}
              pattern={registering ? "(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9]).{12,128}" : undefined}
              title={
                registering
                  ? "Use at least 12 characters with uppercase, lowercase and a number."
                  : undefined
              }
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className={fieldClass}
            />
            {registering && (
              <p className="mt-1.5 text-xs text-[#63736c]">
                At least 12 characters, including uppercase, lowercase and a number.
              </p>
            )}
          </div>
          {error && (
            <p
              role="alert"
              className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"
            >
              {error}
            </p>
          )}
          <button
            disabled={busy}
            className="w-full rounded-xl bg-[#145b48] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#103f34] disabled:cursor-wait disabled:opacity-60"
          >
            {busy ? "Please wait…" : registering ? "Create account" : "Sign in"}
          </button>
        </form>
        <p className="mt-5 text-sm text-[#63736c]">
          {registering ? "Already have an account?" : "New to Elevra?"}{" "}
          <Link
            href={registering ? "/login" : "/register"}
            className="font-semibold text-[#145b48] underline underline-offset-4"
          >
            {registering ? "Sign in" : "Create an account"}
          </Link>
        </p>
      </section>
      <aside className="rounded-[2rem] bg-[#e9efe4] p-8 sm:p-10">
        <span className="text-xs font-bold uppercase tracking-[.16em] text-[#668b59]">
          Your next step, with more clarity
        </span>
        <p className="mt-4 text-2xl font-semibold leading-snug">
          Keep useful opportunities and your plans close at hand.
        </p>
        <p className="mt-4 text-sm leading-6 text-[#63736c]">
          Elevra brings career opportunities, exam information and your account tools into one
          place.
        </p>
      </aside>
    </main>
  );
}

export function ProtectedContent({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { status, error, retryRestore } = useAuth();

  useEffect(() => {
    if (status === "unauthenticated") {
      router.replace(`/login?next=${encodeURIComponent(pathname)}`);
    }
  }, [pathname, router, status]);

  if (status === "unauthenticated") {
    return (
      <div className="mx-auto max-w-3xl px-5 py-20 text-center text-[#63736c]" role="status">
        Taking you to sign in…
      </div>
    );
  }
  if (status === "error") {
    return (
      <main className="mx-auto max-w-3xl px-5 py-16">
        <div className="rounded-2xl border border-[#e3e9e4] bg-white p-7">
          <h1 className="text-2xl font-semibold">We couldn’t restore your session.</h1>
          <p className="mt-2 text-sm text-[#63736c]">{error}</p>
          <button
            onClick={() => void retryRestore().catch(() => undefined)}
            className="mt-5 rounded-xl bg-[#145b48] px-5 py-3 text-sm font-semibold text-white"
          >
            Try again
          </button>
          <Link href="/login" className="ml-4 text-sm font-semibold text-[#145b48]">
            Sign in
          </Link>
        </div>
      </main>
    );
  }
  if (status !== "authenticated")
    return (
      <div className="mx-auto max-w-3xl px-5 py-20 text-center text-[#63736c]" role="status">
        Restoring your secure session…
      </div>
    );
  return <>{children}</>;
}

export function HeaderAuthControls() {
  const { status, user, signOut } = useAuth();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  if (status !== "authenticated" || !user) {
    return (
      <div className="flex items-center gap-2 text-sm font-semibold">
        <Link
          href="/login"
          className="hidden rounded-lg border border-[#d8e1da] px-3.5 py-2 text-slate-700 transition hover:bg-white sm:block"
        >
          Login
        </Link>
        <Link
          href="/register"
          className="rounded-lg bg-[#145b48] px-3.5 py-2 text-white shadow-sm transition hover:bg-[#103f34]"
        >
          Get Started
        </Link>
      </div>
    );
  }
  return (
    <div className="flex items-center gap-2 text-sm font-semibold">
      <Link
        href="/dashboard"
        className="hidden max-w-36 truncate rounded-lg px-2 py-2 text-[#28483b] sm:block"
      >
        {user.name}
      </Link>
      <button
        disabled={busy}
        onClick={async () => {
          setBusy(true);
          setError("");
          try {
            await signOut();
          } catch (cause) {
            setError(cause instanceof Error ? cause.message : "Sign out failed. Try again.");
          } finally {
            setBusy(false);
          }
        }}
        className="rounded-lg border border-[#d8e1da] px-3.5 py-2 text-slate-700 hover:bg-white disabled:opacity-60"
      >
        {busy ? "Signing out…" : "Sign out"}
      </button>
      {error && (
        <span role="alert" className="sr-only">
          {error}
        </span>
      )}
    </div>
  );
}
