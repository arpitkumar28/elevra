"use client";
import Link from "next/link";
import * as React from "react";
import { useCallback, useEffect, useState } from "react";
import {
  createApiClient,
  ApiError,
  type Exam,
  type Opportunity,
} from "@elevra/api-client";

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
function Pill({
  children,
  green = false,
}: {
  children: React.ReactNode;
  green?: boolean;
}) {
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

function Listing({ kind }: { kind: "exams" | "opportunities" }) {
  const isExam = kind === "exams",
    [items, setItems] = useState<(Exam | Opportunity)[]>([]),
    [loading, setLoading] = useState(true),
    [error, setError] = useState(""),
    [q, setQ] = useState(""),
    [filter, setFilter] = useState(""),
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
      <p className="text-sm font-semibold text-amber-700">
        DISCOVER YOUR NEXT STEP
      </p>
      <h1 className="mt-2 text-4xl font-bold tracking-tight">
        {isExam ? "Find the right exam" : "Find your next opportunity"}
      </h1>
      <p className="mt-3 max-w-2xl text-slate-600">
        Verified, official information—organized to help you make a confident
        decision.
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
      <section
        aria-live="polite"
        className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3"
      >
        {loading ? (
          Array.from({ length: 6 }, (_, i) => (
            <div
              key={i}
              className="h-60 animate-pulse rounded-2xl bg-slate-200"
            />
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
                href={`/${kind}/${slug}`}
                key={item.id}
                className="group rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
              >
                <div className="flex justify-between gap-3">
                  <Pill>{titleize(isExam ? e.category : o.type)}</Pill>
                  {item.verified && <Pill green>✓ Verified</Pill>}
                </div>
                <h2 className="mt-5 text-lg font-bold group-hover:text-amber-800">
                  {label}
                </h2>
                <p className="mt-1 text-sm text-slate-600">
                  {isExam
                    ? e.conducting_body || "Conducting body to be announced"
                    : o.organization || "Organization to be announced"}
                </p>
                <div className="mt-5 border-t border-slate-100 pt-4 text-sm text-slate-600">
                  {isExam ? (
                    <>
                      <b>Next date:</b>{" "}
                      {date(e.exam_date || e.application_deadline)}
                      <br />
                      <b>Deadline:</b> {date(e.application_deadline)}
                    </>
                  ) : (
                    <>
                      <b>
                        {o.remote
                          ? "Remote"
                          : o.location || "Location to be announced"}
                      </b>
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
        <nav
          aria-label="Pagination"
          className="mt-8 flex items-center justify-center gap-4"
        >
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
}: {
  kind: "exams" | "opportunities";
  slug: string;
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
      <Link href={`/${kind}`} className="text-sm font-semibold text-amber-800">
        ← Back to {kind}
      </Link>
      <article className="mt-5 overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
        <header className="bg-[#111827] p-8 text-white">
          <div className="flex flex-wrap gap-2">
            <Pill>{titleize(isExam ? e.category : o.type)}</Pill>
            {item.verified && <Pill green>✓ Verified source</Pill>}
          </div>
          <h1 className="mt-5 text-4xl font-bold">{heading}</h1>
          <p className="mt-2 text-slate-300">
            {isExam ? e.conducting_body : o.organization}
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            {source && (
              <a
                href={source}
                target="_blank"
                rel="noreferrer"
                className="rounded-xl bg-[#F5C542] px-4 py-2 font-bold text-slate-900"
              >
                {isExam
                  ? "Visit official website"
                  : "Apply on official website"}{" "}
                ↗
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
              onClick={() =>
                navigator.share?.({ title: heading, url: location.href })
              }
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
                  : o.description ||
                    "Details will be updated from the official source."}
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
                {isExam
                  ? e.source_name || "View official source"
                  : "View official source"}{" "}
                ↗
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
                  <dd className="mt-1 text-sm font-medium">
                    {value || "To be announced"}
                  </dd>
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
  const links: Array<
    [string, string, "/exams" | "/opportunities" | "/career"]
  > = [
    ["Upcoming Exams", "Stay on top of official dates.", "/exams"],
    [
      "Latest Opportunities",
      "Find roles, scholarships, and more.",
      "/opportunities",
    ],
    ["Career Discovery", "Explore the path that fits you.", "/career"],
  ];
  return (
    <main className="mx-auto max-w-7xl px-5 py-12">
      <section className="rounded-3xl bg-[#111827] px-7 py-14 text-white md:px-14">
        <p className="font-semibold text-[#F5C542]">ELEVRA</p>
        <h1 className="mt-3 max-w-2xl text-5xl font-bold tracking-tight">
          Your Career &amp; Exam Companion
        </h1>
        <p className="mt-5 max-w-xl text-lg text-slate-300">
          Clear, official information for the choices that shape your future.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link
            href="/exams"
            className="rounded-xl bg-[#F5C542] px-5 py-3 font-bold text-slate-900"
          >
            Explore Exams
          </Link>
          <Link
            href="/opportunities"
            className="rounded-xl border border-slate-500 px-5 py-3 font-bold"
          >
            Explore Opportunities
          </Link>
        </div>
      </section>
      <section className="mt-10 grid gap-4 md:grid-cols-3">
        {links.map(([h, p, l]) => (
          <Link href={l} key={h} className="rounded-2xl border bg-white p-6">
            <h2 className="font-bold">{h}</h2>
            <p className="mt-2 text-sm text-slate-600">{p}</p>
          </Link>
        ))}
      </section>
    </main>
  );
}
export default function RoutePage({ params }: { params: { slug?: string[] } }) {
  const parts = params.slug || [];
  if (!parts.length) return <Home />;
  if ((parts[0] === "exams" || parts[0] === "opportunities") && parts[1])
    return <Detail kind={parts[0]} slug={parts[1]} />;
  if (parts[0] === "exams" || parts[0] === "opportunities")
    return <Listing kind={parts[0]} />;
  return (
    <main className="mx-auto max-w-4xl px-5 py-16">
      <h1 className="text-4xl font-bold">{titleize(parts[0])}</h1>
      <p className="mt-3 text-slate-600">
        This part of Elevra is being prepared.
      </p>
    </main>
  );
}
