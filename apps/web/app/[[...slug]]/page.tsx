"use client";
import Link from "next/link";
import * as React from "react";
import { useCallback, useEffect, useState } from "react";
import { createApiClient, ApiError, type Exam, type Opportunity } from "@elevra/api-client";

const apiClient = createApiClient({
  baseUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
});

const examCategories = [
  "government",
  "engineering",
  "medical",
  "management",
  "university",
  "defence",
  "banking",
  "railway",
  "teaching",
  "state_exams",
];
const opportunityTypes = [
  "job",
  "internship",
  "scholarship",
  "hackathon",
  "competition",
  "fellowship",
];
const date = (value?: string) =>
  value
    ? new Intl.DateTimeFormat("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric",
      }).format(new Date(value))
    : "To be announced";
const titleize = (value?: string) =>
  value?.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase()) || "—";
function Pill({ children, green = false }: { children: React.ReactNode; green?: boolean }) {
  return (
    <span
      className={`rounded-full px-2.5 py-1 text-xs font-semibold ${green ? "bg-green-50 text-green-700" : "bg-amber-50 text-amber-900"}`}
    >
      {children}
    </span>
  );
}
function State({ message, retry }: { message: string; retry?: () => void }) {
  return (
    <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-10 text-center text-slate-600">
      <p>{message}</p>
      {retry && (
        <button
          onClick={retry}
          className="mt-4 rounded-lg bg-[#F5C542] px-4 py-2 font-semibold text-slate-900"
        >
          Try again
        </button>
      )}
    </div>
  );
}

function Listing({
  kind,
  title,
  defaultType,
  basePath,
}: {
  kind: "exams" | "opportunities";
  title?: string;
  defaultType?: string;
  basePath?: string;
}) {
  const isExam = kind === "exams",
    [items, setItems] = useState<(Exam | Opportunity)[]>([]),
    [loading, setLoading] = useState(true),
    [error, setError] = useState(""),
    [q, setQ] = useState(""),
    [filter, setFilter] = useState(defaultType || ""),
    [page, setPage] = useState(1),
    [pages, setPages] = useState(1);
  const load = useCallback(() => {
    setLoading(true);
    setError("");
    const params: Record<string, string | number> = { page, page_size: 12 };
    if (q) params.q = q;
    if (filter) params[isExam ? "category" : "type"] = filter;
    (isExam ? apiClient.listExams(params) : apiClient.listOpportunities(params))
      .then((data) => {
        setItems(data.items);
        setPages(data.total_pages || 1);
      })
      .catch((e: ApiError) => setError(e.message))
      .finally(() => setLoading(false));
  }, [filter, isExam, page, q]);
  useEffect(() => {
    void load();
  }, [load]);
  const filters = isExam ? examCategories : opportunityTypes;
  return (
    <main className="mx-auto max-w-7xl px-5 py-10">
      <p className="text-sm font-semibold text-amber-700">DISCOVER YOUR NEXT STEP</p>
      <h1 className="mt-2 text-4xl font-bold tracking-tight">
        {title || (isExam ? "Find the right exam" : "Find your next opportunity")}
      </h1>
      <p className="mt-3 max-w-2xl text-slate-600">
        Verified, official information—organized to help you make a confident decision.
      </p>
      <div className="mt-8 flex flex-col gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm md:flex-row">
        <label className="sr-only" htmlFor="search">
          Search
        </label>
        <input
          id="search"
          value={q}
          onChange={(e) => {
            setPage(1);
            setQ(e.target.value);
          }}
          placeholder={`Search ${kind}, organizations, or categories`}
          className="min-w-0 flex-1 rounded-xl border border-slate-300 px-4 py-3 outline-none focus:ring-2 focus:ring-[#F5C542]"
        />
        <select
          aria-label="Filter results"
          value={filter}
          onChange={(e) => {
            setPage(1);
            setFilter(e.target.value);
          }}
          className="rounded-xl border border-slate-300 bg-white px-3 py-3"
        >
          <option value="">All {isExam ? "categories" : "types"}</option>
          {filters.map((x) => (
            <option key={x} value={x}>
              {titleize(x)}
            </option>
          ))}
        </select>
      </div>
      <div className="mt-7 flex flex-wrap gap-2">
        {filters.map((x) => (
          <button
            key={x}
            onClick={() => {
              setPage(1);
              setFilter(filter === x ? "" : x);
            }}
            className={`rounded-full border px-3 py-1.5 text-sm ${filter === x ? "border-amber-400 bg-amber-50" : "border-slate-200 bg-white"}`}
          >
            {titleize(x)}
          </button>
        ))}
      </div>
      <section aria-live="polite" className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {loading ? (
          Array.from({ length: 6 }, (_, i) => (
            <div key={i} className="h-60 animate-pulse rounded-2xl bg-slate-200" />
          ))
        ) : error ? (
          <div className="md:col-span-2 lg:col-span-3">
            <State message={error} retry={load} />
          </div>
        ) : !items.length ? (
          <div className="md:col-span-2 lg:col-span-3">
            <State message="No results match those filters. Try a broader search." />
          </div>
        ) : (
          items.map((item) => {
            const e = item as Exam,
              o = item as Opportunity,
              label = isExam ? e.name : o.title,
              slug = item.slug;
            return (
              <Link
                href={`${basePath || `/${kind}`}/${slug}` as "/exams"}
                key={item.id}
                className="group rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
              >
                <div className="flex justify-between gap-3">
                  <Pill>{titleize(isExam ? e.category : o.type)}</Pill>
                  {item.verified && <Pill green>✓ Verified</Pill>}
                </div>
                <h2 className="mt-5 text-lg font-bold group-hover:text-amber-800">{label}</h2>
                <p className="mt-1 text-sm text-slate-600">
                  {isExam
                    ? e.conducting_body || "Conducting body to be announced"
                    : o.organization || "Organization to be announced"}
                </p>
                <div className="mt-5 border-t border-slate-100 pt-4 text-sm text-slate-600">
                  {isExam ? (
                    <>
                      <b>Next date:</b> {date(e.exam_date || e.application_deadline)}
                      <br />
                      <b>Deadline:</b> {date(e.application_deadline)}
                    </>
                  ) : (
                    <>
                      <b>{o.remote ? "Remote" : o.location || "Location to be announced"}</b>
                      <br />
                      <b>Deadline:</b> {date(o.deadline)}
                    </>
                  )}
                </div>
              </Link>
            );
          })
        )}
      </section>
      {!loading && !error && pages > 1 && (
        <nav aria-label="Pagination" className="mt-8 flex items-center justify-center gap-4">
          <button
            disabled={page === 1}
            onClick={() => setPage(page - 1)}
            className="rounded-lg border px-4 py-2 disabled:opacity-40"
          >
            Previous
          </button>
          <span>
            Page {page} of {pages}
          </span>
          <button
            disabled={page === pages}
            onClick={() => setPage(page + 1)}
            className="rounded-lg border px-4 py-2 disabled:opacity-40"
          >
            Next
          </button>
        </nav>
      )}
    </main>
  );
}
function Detail({
  kind,
  slug,
  basePath,
}: {
  kind: "exams" | "opportunities";
  slug: string;
  basePath?: string;
}) {
  const isExam = kind === "exams",
    [item, setItem] = useState<Exam | Opportunity | null>(null),
    [error, setError] = useState("");
  useEffect(() => {
    (isExam ? apiClient.getExam(slug) : apiClient.getOpportunity(slug))
      .then(setItem)
      .catch((e: ApiError) => setError(e.message));
  }, [isExam, slug]);
  if (error)
    return (
      <main className="mx-auto max-w-4xl px-5 py-12">
        <State message={error} />
      </main>
    );
  if (!item)
    return (
      <main className="mx-auto max-w-4xl px-5 py-12">
        <div className="h-96 animate-pulse rounded-3xl bg-slate-200" />
      </main>
    );
  const e = item as Exam,
    o = item as Opportunity,
    heading = isExam ? e.name : o.title;
  const rows = isExam
    ? [
        ["Conducting body", e.conducting_body],
        ["Application deadline", date(e.application_deadline)],
        ["Exam date", date(e.exam_date)],
        ["Category", titleize(e.category)],
      ]
    : [
        ["Organization", o.organization],
        ["Location", o.remote ? "Remote" : o.location],
        ["Deadline", date(o.deadline)],
        ["Type", titleize(o.type)],
      ];
  const source = isExam ? e.official_website : o.application_url;
  return (
    <main className="mx-auto max-w-4xl px-5 py-10">
      <Link
        href={(basePath || `/${kind}`) as "/exams"}
        className="text-sm font-semibold text-amber-800"
      >
        ← Back to {kind}
      </Link>
      <article className="mt-5 overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
        <header className="bg-[#111827] p-8 text-white">
          <div className="flex flex-wrap gap-2">
            <Pill>{titleize(isExam ? e.category : o.type)}</Pill>
            {item.verified && <Pill green>✓ Verified source</Pill>}
          </div>
          <h1 className="mt-5 text-4xl font-bold">{heading}</h1>
          <p className="mt-2 text-slate-300">{isExam ? e.conducting_body : o.organization}</p>
          <div className="mt-6 flex flex-wrap gap-3">
            {source && (
              <a
                href={source}
                target="_blank"
                rel="noreferrer"
                className="rounded-xl bg-[#F5C542] px-4 py-2 font-bold text-slate-900"
              >
                {isExam ? "Visit official website" : "Apply on official website"} ↗
              </a>
            )}
            <button
              disabled
              title="Saved items require the account API"
              className="rounded-xl border border-slate-600 px-4 py-2 text-sm opacity-70"
            >
              Save (coming soon)
            </button>
            <button
              onClick={() => navigator.share?.({ title: heading, url: location.href })}
              className="rounded-xl border border-slate-600 px-4 py-2 text-sm"
            >
              Share
            </button>
          </div>
        </header>
        <div className="grid gap-8 p-8 md:grid-cols-[1.4fr_1fr]">
          <div className="space-y-8">
            <section>
              <h2 className="text-xl font-bold">Overview</h2>
              <p className="mt-3 whitespace-pre-line leading-7 text-slate-700">
                {isExam
                  ? e.description ||
                    e.short_description ||
                    "Details will be updated from the official source."
                  : o.description || "Details will be updated from the official source."}
              </p>
            </section>
            <section>
              <h2 className="text-xl font-bold">
                {isExam ? "Eligibility & syllabus" : "Eligibility"}
              </h2>
              <p className="mt-3 leading-7 text-slate-700">
                {isExam
                  ? "Eligibility and syllabus are published with official exam updates."
                  : o.eligibility ||
                    "Eligibility details will be updated from the official source."}
              </p>
            </section>
            <section>
              <h2 className="text-xl font-bold">Official source</h2>
              <a
                className="mt-3 inline-block text-amber-800 underline"
                href={
                  (isExam
                    ? e.source_url || e.official_website
                    : o.source_url || o.application_url) || "#"
                }
                target="_blank"
                rel="noreferrer"
              >
                {isExam ? e.source_name || "View official source" : "View official source"} ↗
              </a>
            </section>
          </div>
          <aside className="h-fit rounded-2xl bg-[#FFFCF2] p-5">
            <h2 className="font-bold">At a glance</h2>
            <dl className="mt-4 space-y-4">
              {rows.map(([label, value]) => (
                <div key={label}>
                  <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    {label}
                  </dt>
                  <dd className="mt-1 text-sm font-medium">{value || "To be announced"}</dd>
                </div>
              ))}
            </dl>
          </aside>
        </div>
      </article>
    </main>
  );
}
function Home() {
  const categories: Array<[string, string, string, string]> = [
    ["▤", "Exams", "250+ Exams", "/exams"],
    ["▣", "Jobs", "25K+ Jobs", "/opportunities?type=job"],
    ["⌁", "Internships", "15K+ Opportunities", "/opportunities?type=internship"],
    ["✿", "Scholarships", "8K+ Scholarships", "/opportunities?type=scholarship"],
    ["▦", "Hackathons", "2K+ Events", "/opportunities?type=hackathon"],
    ["♜", "Test Series", "5K+ Tests", "/career"],
    ["▰", "Courses", "3K+ Courses", "/career"],
    ["▧", "Current Affairs", "Daily Updates", "/career"],
  ];
  const trending: Array<[string, string, string, string, string]> = [
    ["🏛️", "UPSC CSE 2025", "Apply before", "22 May 2025", "/exams"],
    [
      "G",
      "Google Summer Internship 2025",
      "Apply before",
      "15 May 2025",
      "/opportunities?type=internship",
    ],
    ["GATE", "GATE 2026 Registration", "Apply before", "31 May 2025", "/exams"],
    ["⚕", "JNVU Research Fellowship 2025", "Apply before", "10 May 2025", "/opportunities"],
  ];
  return (
    <main>
      <section className="mx-auto grid max-w-7xl overflow-hidden px-5 pb-9 pt-7 lg:grid-cols-[1.05fr_.95fr] lg:px-8 lg:pt-12">
        <div className="relative z-10 py-8 lg:py-16">
          <p className="mb-5 text-sm font-bold uppercase tracking-[.18em] text-[#e5a300]">
            One platform. Every opportunity.
          </p>
          <h1 className="max-w-xl text-4xl font-extrabold leading-[1.08] tracking-tight text-[#172039] sm:text-6xl">
            Your{" "}
            <span className="text-[#f4aa00]">
              Career &amp;
              <br />
              Exam
            </span>{" "}
            Companion
          </h1>
          <p className="mt-5 max-w-lg text-base leading-7 text-slate-500">
            Discover opportunities, prepare smarter, and build your future with everything you need
            in one place.
          </p>
          <form
            action="/exams"
            className="mt-7 flex max-w-xl overflow-hidden rounded-xl border border-slate-200 bg-white p-1.5 shadow-sm"
          >
            <input
              name="q"
              aria-label="Search exams, jobs, courses and more"
              placeholder="Search exams, jobs, courses, and more..."
              className="min-w-0 flex-1 px-3 text-sm text-slate-700 outline-none"
            />
            <button className="rounded-lg bg-[#ffbf13] px-5 py-2.5 text-sm font-bold text-slate-900">
              Search
            </button>
          </form>
          <div className="mt-6 flex flex-wrap gap-x-5 gap-y-2 text-xs font-medium text-slate-500">
            <span>◉ Trusted &amp; Verified</span>
            <span>◉ Personalised for You</span>
            <span>◉ All in One Platform</span>
          </div>
        </div>
        <div className="relative hidden min-h-[440px] items-center justify-center overflow-hidden lg:flex">
          <div className="hero-orb absolute right-0 top-8 h-72 w-72 rounded-full bg-[#ffe59a]" />
          <div className="absolute right-16 top-4 h-28 w-28 rounded-full bg-[#ffbf13] opacity-80" />
          <div className="grid-dot absolute right-16 top-32 h-16 w-16" />
          <div className="relative mt-8 h-72 w-60 overflow-hidden rounded-[7rem_7rem_2.5rem_2.5rem] bg-gradient-to-b from-[#ffe7b1] to-[#f9c83e] shadow-2xl">
            <div className="absolute inset-x-8 top-10 h-24 rounded-[50%] bg-[#f7c289]" />
            <div className="absolute inset-x-7 top-7 h-32 rounded-t-[50%] bg-[#1e273a]" />
            <div className="absolute bottom-0 left-5 right-5 h-36 rounded-t-[2rem] bg-[#f4a900]" />
            <div className="absolute bottom-7 left-10 right-10 h-14 rounded-lg bg-slate-800 shadow-xl" />
          </div>
          <div className="soft-card absolute left-2 top-24 rounded-xl bg-white px-4 py-3 text-xs">
            <span className="text-slate-500">Opportunities</span>
            <b className="mt-1 block text-lg">12.6K+</b>
            <span className="text-slate-400">Live Opportunities</span>
          </div>
          <div className="soft-card absolute left-14 bottom-14 rounded-xl bg-white px-4 py-3 text-xs">
            <span className="text-slate-500">Exams</span>
            <b className="mt-1 block text-lg">250+</b>
            <span className="text-slate-400">Exams Covered</span>
          </div>
          <div className="soft-card absolute right-2 bottom-5 rounded-xl bg-white px-4 py-3 text-xs">
            <span className="text-slate-500">Students</span>
            <b className="mt-1 block text-lg">1M+</b>
            <span className="text-slate-400">Trust Elevra</span>
          </div>
        </div>
      </section>
      <section className="mx-auto max-w-7xl px-5 pb-8 lg:px-8">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-extrabold">Explore Top Categories</h2>
          <Link href="/exams" className="text-sm font-semibold text-slate-500 hover:text-[#d99400]">
            View all →
          </Link>
        </div>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-8">
          {categories.map(([icon, title, count, href]) => (
            <Link
              href={href as "/exams"}
              key={title}
              className="soft-card rounded-xl border border-slate-100 bg-white p-3 text-center transition hover:-translate-y-1 hover:border-amber-200"
            >
              <span className="mx-auto grid h-10 w-10 place-items-center rounded-xl bg-amber-50 text-lg text-[#e4a000]">
                {icon}
              </span>
              <h3 className="mt-2 text-sm font-bold">{title}</h3>
              <p className="mt-1 text-[10px] text-slate-400">{count}</p>
            </Link>
          ))}
        </div>
      </section>
      <section className="mx-auto max-w-7xl px-5 pb-16 pt-5 lg:px-8">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-xl font-extrabold">Trending Now</h2>
            <p className="mt-1 text-sm text-slate-500">
              Don&apos;t miss the most popular opportunities this week.
            </p>
          </div>
          <Link href="/opportunities" className="text-sm font-semibold text-[#d99400]">
            View all →
          </Link>
        </div>
        <div className="mb-4 flex gap-2 overflow-auto pb-1 text-sm">
          <span className="rounded-full bg-[#ffedbf] px-4 py-1.5 font-semibold text-[#b97800]">
            All
          </span>
          <span className="rounded-full px-4 py-1.5 text-slate-500">Exams</span>
          <span className="rounded-full px-4 py-1.5 text-slate-500">Jobs</span>
          <span className="rounded-full px-4 py-1.5 text-slate-500">Scholarships</span>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {trending.map(([icon, title, prefix, deadline, href]) => (
            <Link
              href={href as "/exams"}
              key={title}
              className="soft-card group rounded-xl border border-slate-100 bg-white p-4 transition hover:-translate-y-1"
            >
              <div className="flex items-start gap-3">
                <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-amber-50 font-bold text-[#dc9b00]">
                  {icon}
                </span>
                <div>
                  <h3 className="text-sm font-bold group-hover:text-[#c88600]">{title}</h3>
                  <p className="mt-1 text-xs text-slate-400">{prefix}</p>
                  <p className="text-xs font-semibold text-[#ef6657]">{deadline}</p>
                </div>
              </div>
              <div className="mt-4 border-t border-slate-100 pt-3 text-xs font-semibold text-[#ef6657]">
                16 days left
              </div>
            </Link>
          ))}
        </div>
      </section>
    </main>
  );
}

function Dashboard() {
  const plans = [
    ["09:00", "GATE – Operating Systems", "Study · 60 min"],
    ["11:00", "Complete DBMS Notes", "Study · 45 min"],
    ["14:00", "Solve DSA Problems", "Practice · 60 min"],
    ["16:00", "Apply: Microsoft Internship", "Application · 30 min"],
  ];
  const progress = [
    ["GATE 2026", "72%", "bg-amber-400"],
    ["JEE Main 2026", "48%", "bg-blue-500"],
    ["SSC CGL 2025", "61%", "bg-amber-400"],
  ];
  return (
    <main className="mx-auto max-w-7xl px-5 py-8 lg:px-8">
      <section className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-3xl font-extrabold">Hi, Arpit 👋</p>
          <p className="mt-1 text-sm text-slate-500">Keep going! You&apos;re doing great.</p>
        </div>
        <div className="flex gap-3 text-lg text-slate-500">
          <span>⌕</span>
          <span>♧</span>
          <span>▦</span>
          <span className="grid h-9 w-9 place-items-center rounded-full bg-amber-100 text-sm">
            A
          </span>
        </div>
      </section>
      <section className="mt-7 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {[
          ["◎", "Opportunities", "128", "Matched for you"],
          ["⌁", "Exam Readiness", "72%", "Keep it up!"],
          ["▦", "Upcoming Deadlines", "9", "This week"],
          ["♧", "Notifications", "4", "Priority alerts"],
        ].map(([icon, label, value, caption]) => (
          <article
            key={label}
            className="soft-card rounded-xl border border-slate-100 bg-white p-4"
          >
            <span className="text-[#e3a000]">{icon}</span>
            <p className="mt-2 text-xs text-slate-500">{label}</p>
            <b className="mt-1 block text-2xl">{value}</b>
            <p className="mt-1 text-xs text-slate-400">{caption}</p>
          </article>
        ))}
      </section>
      <section className="mt-5 grid gap-5 lg:grid-cols-[1.45fr_.9fr]">
        <article className="soft-card rounded-2xl border border-slate-100 bg-white p-5">
          <div className="flex items-center justify-between">
            <h2 className="font-bold">Today&apos;s Plan</h2>
            <Link href="/career" className="text-sm font-semibold text-[#d99400]">
              View Full Plan →
            </Link>
          </div>
          <div className="mt-4 space-y-1">
            {plans.map(([time, title, meta], i) => (
              <div
                key={time}
                className="grid grid-cols-[56px_1fr_24px] items-center gap-3 rounded-lg px-2 py-3 hover:bg-amber-50"
              >
                <span className="text-xs font-semibold text-emerald-600">{time}</span>
                <div>
                  <p className="text-sm font-semibold">{title}</p>
                  <p className="text-xs text-slate-400">{meta}</p>
                </div>
                <span className={i === 0 ? "text-emerald-500" : "text-slate-300"}>
                  {i === 0 ? "●" : "○"}
                </span>
              </div>
            ))}
          </div>
        </article>
        <article className="soft-card rounded-2xl border border-slate-100 bg-white p-5">
          <div className="flex items-center justify-between">
            <h2 className="font-bold">Exam Progress</h2>
            <Link href="/exams" className="text-sm text-[#d99400]">
              View all
            </Link>
          </div>
          <div className="mt-6 space-y-5">
            {progress.map(([name, value, color]) => (
              <div key={name}>
                <div className="flex justify-between text-sm">
                  <span>{name}</span>
                  <b>{value}</b>
                </div>
                <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
                  <div className={`h-full rounded-full ${color}`} style={{ width: value }} />
                </div>
              </div>
            ))}
          </div>
        </article>
      </section>
      <section className="mt-5 grid gap-5 lg:grid-cols-[1.45fr_.9fr]">
        <article className="soft-card rounded-2xl border border-slate-100 bg-white p-5">
          <div className="flex items-center justify-between">
            <h2 className="font-bold">Recommended for You</h2>
            <Link href="/opportunities" className="text-sm text-[#d99400]">
              View all →
            </Link>
          </div>
          {[
            ["G", "Google Internship 2025", "Software Engineering Intern"],
            ["a", "Amazon SDE Intern", "Summer Internship"],
            ["▰", "Flipkart Grid 6.0", "Campus Ambassador Program"],
          ].map(([badge, title, role]) => (
            <Link
              href="/opportunities"
              key={title}
              className="mt-3 flex items-center gap-3 rounded-lg p-2 transition hover:bg-amber-50"
            >
              <span className="grid h-9 w-9 place-items-center rounded-lg bg-slate-100 font-bold text-[#d99400]">
                {badge}
              </span>
              <div className="flex-1">
                <p className="text-sm font-semibold">{title}</p>
                <p className="text-xs text-slate-400">{role}</p>
              </div>
              <span className="rounded-full bg-emerald-50 px-2 py-1 text-[10px] text-emerald-600">
                95% Match
              </span>
            </Link>
          ))}
        </article>
        <article className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#7143e8] to-[#3820a9] p-5 text-white">
          <span className="text-lg">✦</span>
          <h2 className="mt-4 text-lg font-bold">AI Mentor</h2>
          <p className="mt-2 max-w-[190px] text-sm leading-6 text-violet-100">
            Ask me anything about exams, careers, and study plans.
          </p>
          <Link
            href="/career"
            className="mt-5 inline-block rounded-lg bg-white px-3 py-2 text-xs font-bold text-violet-700"
          >
            Chat Now
          </Link>
          <span className="absolute bottom-3 right-4 text-6xl opacity-30">🤖</span>
        </article>
      </section>
    </main>
  );
}

function SimplePage({ title, eyebrow, copy }: { title: string; eyebrow: string; copy: string }) {
  return (
    <main className="mx-auto flex min-h-[70vh] max-w-7xl items-center px-5 py-12 lg:px-8">
      <section className="grid w-full overflow-hidden rounded-3xl bg-white shadow-sm md:grid-cols-2">
        <div className="p-8 sm:p-14">
          <p className="text-sm font-bold uppercase tracking-[.16em] text-[#e4a000]">{eyebrow}</p>
          <h1 className="mt-4 text-4xl font-extrabold tracking-tight">{title}</h1>
          <p className="mt-4 max-w-md leading-7 text-slate-500">{copy}</p>
          <div className="mt-8 space-y-3">
            <input
              placeholder="Email address"
              className="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-amber-400"
            />
            <input
              placeholder="Password"
              type="password"
              className="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-amber-400"
            />
            <button className="w-full rounded-xl bg-[#ffbf13] py-3 font-bold text-slate-900">
              Continue
            </button>
          </div>
        </div>
        <div className="hidden bg-gradient-to-br from-[#fff4cb] via-[#ffe69a] to-[#ffbf13] p-14 md:block">
          <div className="grid h-full place-items-center rounded-[3rem] border-[12px] border-white/60 bg-white/20 text-center">
            <div>
              <span className="text-7xl">🎓</span>
              <p className="mt-5 text-2xl font-extrabold text-slate-800">
                Your future,
                <br />
                organised.
              </p>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
export default function RoutePage({ params }: { params: { slug?: string[] } }) {
  const parts = params.slug || [];
  if (!parts.length) return <Home />;
  if (parts[0] === "dashboard") return <Dashboard />;
  if (parts[0] === "login")
    return (
      <SimplePage
        title="Welcome back"
        eyebrow="Elevra account"
        copy="Sign in to keep your study plan, saved opportunities, and exam progress in one place."
      />
    );
  if (parts[0] === "register")
    return (
      <SimplePage
        title="Create your account"
        eyebrow="Start your journey"
        copy="Join Elevra to discover trusted opportunities and prepare with a plan made for you."
      />
    );
  if (parts[0] === "profile") return <Dashboard />;
  if (parts[0] === "career")
    return (
      <SimplePage
        title="Find your direction"
        eyebrow="Career discovery"
        copy="Explore roles, courses, and opportunities that match your goals and interests."
      />
    );
  const opportunityViews: Record<string, { title: string; type?: string }> = {
    explore: { title: "Explore opportunities" },
    jobs: { title: "Find your next job", type: "job" },
    internships: { title: "Find an internship", type: "internship" },
    scholarships: { title: "Scholarships for your goals", type: "scholarship" },
    competitions: { title: "Competitions & hackathons", type: "competition" },
  };
  if ((parts[0] === "exams" || parts[0] === "opportunities") && parts[1])
    return <Detail kind={parts[0]} slug={parts[1]} />;
  if (parts[0] === "exams" || parts[0] === "opportunities") return <Listing kind={parts[0]} />;
  if (parts[0] in opportunityViews) {
    const view = opportunityViews[parts[0]];
    if (parts[1]) return <Detail kind="opportunities" slug={parts[1]} basePath={`/${parts[0]}`} />;
    return (
      <Listing
        kind="opportunities"
        title={view.title}
        defaultType={view.type}
        basePath={`/${parts[0]}`}
      />
    );
  }
  return (
    <main className="mx-auto max-w-4xl px-5 py-16">
      <h1 className="text-4xl font-bold">{titleize(parts[0])}</h1>
      <p className="mt-3 text-slate-600">This part of Elevra is being prepared.</p>
    </main>
  );
}
