"use client";

import React, { useState, type ReactNode } from "react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LogOut } from "lucide-react";
import { useAuth } from "./admin-session";
import { AdminNav } from "./admin-nav";

const sectionTitles: Record<string, string> = {
  dashboard: "Overview",
  opportunities: "Opportunities",
  exams: "Exams",
  queue: "Draft & review queue",
  verification: "Draft & review queue",
  courses: "Courses",
  "current-affairs": "Current affairs",
  tests: "Practice tests",
};

function initials(name: string) {
  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("") || "A";
}

export function AdminShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const { user, signOut } = useAuth();
  const [signingOut, setSigningOut] = useState(false);
  const [signOutError, setSignOutError] = useState("");
  const route = pathname.split("/").filter(Boolean)[0] || "dashboard";
  const title = sectionTitles[route] || "Admin workspace";
  const displayName = user?.name?.trim() || user?.email || "Administrator";

  async function handleSignOut() {
    if (signingOut) return;
    setSigningOut(true);
    setSignOutError("");
    try {
      await signOut();
    } catch (cause) {
      setSignOutError(cause instanceof Error ? cause.message : "Unable to sign out. Try again.");
    } finally {
      setSigningOut(false);
    }
  }

  return (
    <div className="min-h-screen lg:flex">
      <a
        href="#admin-main"
        className="fixed left-4 top-4 z-50 -translate-y-24 rounded-lg bg-white px-4 py-2 font-semibold text-[#155b48] shadow-lg focus:translate-y-0"
      >
        Skip to workspace
      </a>

      <aside className="border-b border-[#dfe7df] bg-white/95 px-5 py-4 shadow-[0_8px_28px_rgba(25,54,39,.035)] backdrop-blur lg:fixed lg:inset-y-0 lg:left-0 lg:z-30 lg:flex lg:w-[17.5rem] lg:flex-col lg:border-b-0 lg:border-r lg:px-6 lg:py-6 lg:shadow-none">
        <Link href="/dashboard" className="flex items-center gap-3 text-lg font-bold">
          <Image
            src="/elevra-logo.png"
            alt=""
            width={40}
            height={40}
            priority
            className="h-10 w-10 rounded-xl object-cover"
          />
          <span>
            Elevra <span className="text-xs font-medium text-slate-400">Admin</span>
          </span>
        </Link>
        <p className="mb-0 mt-7 hidden text-[11px] font-bold uppercase tracking-[.16em] text-[#87938a] lg:block">
          Workspace
        </p>
        <AdminNav />

        <div className="mt-6 hidden rounded-2xl border border-[#e6ece3] bg-[#f8faf6] p-4 lg:mt-auto lg:block">
          <div className="flex items-center gap-3">
            <span className="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-[#e4eddd] text-sm font-bold text-[#315943]">
              {initials(displayName)}
            </span>
            <span className="min-w-0">
              <span className="block truncate text-sm font-semibold text-[#23382d]">
                {displayName}
              </span>
              <span className="mt-0.5 block text-xs capitalize text-[#718078]">
                {user?.role?.replaceAll("_", " ") || "Administrator"}
              </span>
            </span>
          </div>
          <button
            type="button"
            onClick={() => void handleSignOut()}
            disabled={signingOut}
            className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-xl border border-[#dfe7df] bg-white px-3 py-2.5 text-sm font-semibold text-[#53645a] transition hover:border-[#c7d7c5] hover:bg-[#f4f8f1] disabled:cursor-wait disabled:opacity-60"
          >
            <LogOut size={16} aria-hidden="true" />
            {signingOut ? "Signing out…" : "Sign out"}
          </button>
        </div>
      </aside>

      <div id="admin-main" className="min-w-0 flex-1 lg:ml-[17.5rem]">
        <header className="sticky top-0 z-20 border-b border-[#e2e9e0] bg-[#f8faf7]/90 px-5 py-3 backdrop-blur-xl sm:px-8 lg:px-10">
          <div className="mx-auto flex max-w-[1500px] items-center justify-between gap-4">
            <div className="min-w-0">
              <p className="text-[11px] font-bold uppercase tracking-[.15em] text-[#7c8b80]">
                Elevra / Admin
              </p>
              <h1 className="mt-1 truncate text-lg font-semibold tracking-tight text-[#1c3025]">
                {title}
              </h1>
            </div>
            <div className="flex items-center gap-2 sm:gap-3">
              <span className="hidden max-w-48 truncate text-sm font-medium text-[#53645a] sm:block">
                {displayName}
              </span>
              <button
                type="button"
                onClick={() => void handleSignOut()}
                disabled={signingOut}
                aria-label={signingOut ? "Signing out" : "Sign out"}
                title="Sign out"
                className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-[#dfe7df] bg-white text-[#53645a] transition hover:bg-[#f4f8f1] disabled:cursor-wait disabled:opacity-60 lg:hidden"
              >
                <LogOut size={17} aria-hidden="true" />
              </button>
            </div>
          </div>
          {signOutError && (
            <p role="alert" className="mx-auto mt-2 max-w-[1500px] text-sm text-red-700">
              {signOutError}
            </p>
          )}
        </header>
        <div className="px-5 py-6 sm:px-8 sm:py-8 lg:px-10">{children}</div>
      </div>
    </div>
  );
}
