"use client";
import Link from "next/link";
import * as React from "react";
import { useCallback, useEffect, useState } from "react";
import {
  createApiClient,
  ApiError,
  type Exam,
  type Opportunity,
  type Course,
  type CurrentAffair,
} from "@elevra/api-client";

const apiClient = createApiClient({
  baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1",
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
        <State message={error} retry={() => location.reload()} />
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
  const [exams, setExams] = useState<Exam[]>([]);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  useEffect(() => {
    Promise.all([
      apiClient.listExams({ page_size: 3 }),
      apiClient.listOpportunities({ page_size: 3 }),
    ])
      .then(([examPage, opportunityPage]) => {
        setExams(examPage.items);
        setOpportunities(opportunityPage.items);
      })
      .catch((e: ApiError) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const areas = [
    [
      "01",
      "Exams & preparation",
      "Understand exam dates, eligibility and official sources in one place.",
      "/exams",
      "Browse exams",
    ],
    [
      "02",
      "Career opportunities",
      "Explore jobs, internships, scholarships and competitions.",
      "/explore",
      "Explore opportunities",
    ],
    [
      "03",
      "Learning resources",
      "Find courses and current affairs to support your next step.",
      "/courses",
      "Explore resources",
    ],
    [
      "04",
      "Practice & progress",
      "Build a steady preparation routine with available tests.",
      "/tests",
      "View practice tests",
    ],
  ];

  return (
    <main>
      <section className="mx-auto grid max-w-7xl gap-10 px-5 pb-16 pt-12 lg:grid-cols-[1.1fr_.9fr] lg:px-8 lg:pb-24 lg:pt-20">
        <div className="relative z-10">
          <p className="mb-5 flex items-center gap-2 text-xs font-bold uppercase tracking-[.18em] text-[#145b48]">
            <span className="h-2 w-2 rounded-full bg-[#7fae68]" /> A clearer way forward
          </p>
          <h1 className="max-w-2xl text-5xl font-semibold leading-[1.04] tracking-[-.045em] text-[#14231f] sm:text-6xl lg:text-7xl">
            Your Career &amp; Exam <span className="text-[#668b59]">Companion.</span>
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-8 text-[#63736c]">
            Your next chapter starts here. Find trusted opportunities, make sense of exam
            information, and move forward with confidence.
          </p>
          <form
            action="/explore"
            className="mt-8 flex max-w-xl overflow-hidden rounded-2xl border border-[#d8e1da] bg-white p-1.5 shadow-sm"
          >
            <label className="sr-only" htmlFor="home-search">
              Search opportunities and exams
            </label>
            <input
              id="home-search"
              name="q"
              placeholder="What are you looking for?"
              className="min-w-0 flex-1 bg-transparent px-4 py-3 text-sm outline-none"
            />
            <button className="rounded-xl bg-[#145b48] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#103f34]">
              Search <span aria-hidden="true">→</span>
            </button>
          </form>
          <div className="mt-6 flex flex-wrap gap-x-6 gap-y-2 text-sm text-[#63736c]">
            <span>Curated information</span>
            <span>Official sources</span>
            <span>Free to explore</span>
          </div>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/explore"
              className="rounded-xl bg-[#d4edaa] px-5 py-3 text-sm font-bold text-[#173b2f] transition hover:bg-[#c3e291]"
            >
              Explore opportunities <span aria-hidden="true">↗</span>
            </Link>
            <Link
              href="/exams"
              className="rounded-xl border border-[#cbd8ce] px-5 py-3 text-sm font-semibold text-[#28483b] transition hover:bg-white"
            >
              Find an exam
            </Link>
          </div>
        </div>
        <div className="relative min-h-[310px] overflow-hidden rounded-[2rem] bg-[#e9efe4] p-6 sm:min-h-[410px] lg:p-9">
          <div className="absolute -right-10 -top-16 h-64 w-64 rounded-full bg-[#d4edaa]" />
          <div className="absolute bottom-0 right-0 h-3/5 w-3/5 rounded-tl-[9rem] bg-[#c1d4b8]" />
          <div className="absolute bottom-0 left-0 h-2/5 w-2/5 rounded-tr-[8rem] bg-[#d7dfd1]" />
          <div className="relative flex h-full min-h-[270px] flex-col justify-between sm:min-h-[350px]">
            <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-[.14em] text-[#42634e]">
              <span>Make room for possibility</span>
              <span>Elevra / 01</span>
            </div>
            <div className="self-end rounded-2xl border border-white/80 bg-white/90 p-5 shadow-[0_18px_50px_rgba(31,62,44,.12)] sm:max-w-[285px]">
              <span className="text-xs font-bold uppercase tracking-widest text-[#6b8a60]">
                Your journey, organised
              </span>
              <p className="mt-3 text-2xl font-semibold leading-tight tracking-tight">
                Find the information. Choose your direction.
              </p>
              <Link href="/career" className="mt-5 inline-flex text-sm font-bold text-[#145b48]">
                Start exploring <span className="ml-2">→</span>
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="border-y border-[#e3e9e4] bg-white py-16">
        <div className="mx-auto max-w-7xl px-5 lg:px-8">
          <div className="mb-8 max-w-2xl">
            <p className="text-xs font-bold uppercase tracking-[.16em] text-[#668b59]">
              One companion, many next steps
            </p>
            <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
              Everything you need to keep moving.
            </h2>
            <p className="mt-3 leading-7 text-[#63736c]">
              A single place to discover, prepare and plan—at your own pace.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {areas.map(([number, title, copy, href, action]) => (
              <Link
                key={title}
                href={href as "/exams"}
                className="group rounded-2xl border border-[#e3e9e4] bg-[#fbfcf9] p-5 transition hover:-translate-y-1 hover:border-[#b7c9b8] hover:bg-white hover:shadow-lg"
              >
                <span className="text-xs font-bold tracking-widest text-[#78936c]">{number}</span>
                <h3 className="mt-8 text-lg font-semibold">{title}</h3>
                <p className="mt-2 min-h-[72px] text-sm leading-6 text-[#63736c]">{copy}</p>
                <span className="mt-5 inline-block text-sm font-bold text-[#145b48]">
                  {action} <span aria-hidden="true">→</span>
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-16 lg:px-8">
        <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-[.16em] text-[#668b59]">
              Explore what’s available
            </p>
            <h2 className="mt-2 text-3xl font-semibold tracking-tight">A good place to begin.</h2>
          </div>
          <Link href="/explore" className="text-sm font-bold text-[#145b48]">
            See all opportunities →
          </Link>
        </div>
        {loading ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((x) => (
              <div key={x} className="h-48 animate-pulse rounded-2xl bg-[#e8ede7]" />
            ))}
          </div>
        ) : error ? (
          <State
            message={error}
            retry={() => {
              setLoading(true);
              setError("");
              Promise.all([
                apiClient.listExams({ page_size: 3 }),
                apiClient.listOpportunities({ page_size: 3 }),
              ])
                .then(([e, o]) => {
                  setExams(e.items);
                  setOpportunities(o.items);
                })
                .catch((e: ApiError) => setError(e.message))
                .finally(() => setLoading(false));
            }}
          />
        ) : exams.length + opportunities.length === 0 ? (
          <State message="There are no published opportunities or exams to show yet. Please check back soon." />
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[
              ...exams
                .slice(0, 2)
                .map((item) => ({
                  label: item.name,
                  category: titleize(item.category),
                  org: item.conducting_body || "Exam information",
                  href: `/exams/${item.slug}`,
                  meta: item.application_deadline
                    ? `Deadline ${date(item.application_deadline)}`
                    : "Dates to be announced",
                })),
              ...opportunities
                .slice(0, 4)
                .map((item) => ({
                  label: item.title,
                  category: titleize(item.type),
                  org: item.organization || "Opportunity",
                  href: `/opportunities/${item.slug}`,
                  meta: item.deadline
                    ? `Deadline ${date(item.deadline)}`
                    : item.remote
                      ? "Remote"
                      : item.location || "Location to be announced",
                })),
            ]
              .slice(0, 3)
              .map((item) => (
                <Link
                  key={item.href}
                  href={item.href as "/exams"}
                  className="rounded-2xl border border-[#e3e9e4] bg-white p-5 transition hover:border-[#b7c9b8] hover:shadow-md"
                >
                  <span className="rounded-full bg-[#eef4e8] px-3 py-1 text-xs font-semibold text-[#42634e]">
                    {item.category}
                  </span>
                  <h3 className="mt-5 text-lg font-semibold">{item.label}</h3>
                  <p className="mt-1 text-sm text-[#63736c]">{item.org}</p>
                  <p className="mt-5 border-t border-[#edf0ec] pt-4 text-xs text-[#63736c]">
                    {item.meta}
                  </p>
                </Link>
              ))}
          </div>
        )}
      </section>
      <section className="mx-5 mb-16 rounded-[2rem] bg-[#145b48] px-6 py-12 text-white sm:px-12 lg:mx-auto lg:max-w-7xl">
        <div className="flex flex-col items-start justify-between gap-6 sm:flex-row sm:items-center">
          <div>
            <p className="text-xs font-bold uppercase tracking-[.18em] text-[#d4edaa]">
              Your next step can start today
            </p>
            <h2 className="mt-3 max-w-xl text-3xl font-semibold tracking-tight sm:text-4xl">
              Make your plans feel possible.
            </h2>
            <p className="mt-3 max-w-lg leading-7 text-white/75">
              Explore useful information for the exams and opportunities that matter to you.
            </p>
          </div>
          <Link
            href="/explore"
            className="shrink-0 rounded-xl bg-[#d4edaa] px-5 py-3 text-sm font-bold text-[#173b2f]"
          >
            Explore Elevra <span aria-hidden="true">→</span>
          </Link>
        </div>
      </section>
    </main>
  );
}

function Dashboard() {
  return (
    <main className="mx-auto max-w-5xl px-5 py-12 lg:px-8">
      <p className="text-xs font-bold uppercase tracking-[.16em] text-[#668b59]">Your space</p>
      <h1 className="mt-3 text-4xl font-semibold tracking-tight">Your plans, all in one place.</h1>
      <p className="mt-4 max-w-2xl leading-7 text-[#63736c]">
        Sign in to access account features. Your saved items, applications and notifications are
        connected to your account.
      </p>
      <div className="mt-8 rounded-2xl border border-[#e3e9e4] bg-white p-6 sm:p-8">
        <h2 className="text-xl font-semibold">Account access</h2>
        <p className="mt-2 max-w-xl text-sm leading-6 text-[#63736c]">
          The web app does not yet connect its account screens to the authentication API, so
          personal dashboard data cannot be loaded here.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link
            href="/login"
            className="rounded-xl bg-[#145b48] px-5 py-3 text-sm font-semibold text-white"
          >
            Sign in
          </Link>
          <Link
            href="/explore"
            className="rounded-xl border border-[#d8e1da] px-5 py-3 text-sm font-semibold text-[#28483b]"
          >
            Explore opportunities
          </Link>
        </div>
      </div>
    </main>
  );
}

function SimplePage({ title, eyebrow, copy }: { title: string; eyebrow: string; copy: string }) {
  return (
    <main className="mx-auto grid min-h-[65vh] max-w-6xl items-center gap-10 px-5 py-12 md:grid-cols-[1fr_.8fr] lg:px-8">
      <section>
        <p className="text-xs font-bold uppercase tracking-[.16em] text-[#668b59]">{eyebrow}</p>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">{title}</h1>
        <p className="mt-4 max-w-lg leading-7 text-[#63736c]">{copy}</p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link
            href="/explore"
            className="rounded-xl bg-[#145b48] px-5 py-3 text-sm font-semibold text-white"
          >
            Explore Elevra
          </Link>
          <Link
            href="/register"
            className="rounded-xl border border-[#d8e1da] px-5 py-3 text-sm font-semibold text-[#28483b]"
          >
            Create account
          </Link>
        </div>
      </section>
      <aside className="rounded-[2rem] bg-[#e9efe4] p-8 sm:p-10">
        <span className="text-xs font-bold uppercase tracking-[.16em] text-[#668b59]">
          Coming into focus
        </span>
        <p className="mt-4 text-2xl font-semibold leading-snug">
          A little clarity can make the next step easier.
        </p>
        <p className="mt-4 text-sm leading-6 text-[#63736c]">
          Explore exams, learning resources and career opportunities while account services are
          being connected.
        </p>
      </aside>
    </main>
  );
}

function ResourceHub({ route, slug }: { route: string; slug?: string }) {
  const [courses, setCourses] = useState<Course[]>([]);
  const [affairs, setAffairs] = useState<CurrentAffair[]>([]);
  const [tests, setTests] = useState<
    Array<{ id: string; title: string; type: string; duration_minutes: number }>
  >([]);
  const [detail, setDetail] = useState<Course | CurrentAffair | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const isCourses = route === "courses";
  const isAffairs = route === "current-affairs";
  useEffect(() => {
    setLoading(true);
    setError("");
    const request = isCourses
      ? slug
        ? apiClient.getCourse(slug)
        : apiClient.listCourses({ page_size: 12 })
      : isAffairs
        ? slug
          ? apiClient.getCurrentAffair(slug)
          : apiClient.listCurrentAffairs({ page_size: 12 })
        : apiClient.listTests();
    request
      .then((data) => {
        if (isCourses)
          slug ? setDetail(data as Course) : setCourses((data as { items: Course[] }).items);
        else if (isAffairs)
          slug
            ? setDetail(data as CurrentAffair)
            : setAffairs((data as { items: CurrentAffair[] }).items);
        else
          setTests(
            data as Array<{ id: string; title: string; type: string; duration_minutes: number }>,
          );
      })
      .catch((e: ApiError) => setError(e.message))
      .finally(() => setLoading(false));
  }, [isCourses, isAffairs, route, slug]);

  const title = isCourses ? "Courses" : isAffairs ? "Current affairs" : "Practice tests";
  if (slug && route === "tests")
    return (
      <SimplePage
        title="Practice test"
        eyebrow="Practice"
        copy="Starting and submitting a test requires an authenticated account. Sign in to continue when account access is available."
      />
    );
  if (slug && detail)
    return (
      <main className="mx-auto max-w-4xl px-5 py-12 lg:px-8">
        <Link href={`/${route}`} className="text-sm font-semibold text-[#145b48]">
          ← Back to {title}
        </Link>
        <article className="mt-5 rounded-3xl border border-[#e3e9e4] bg-white p-7 sm:p-10">
          <p className="text-xs font-bold uppercase tracking-[.16em] text-[#668b59]">
            {isCourses ? (detail as Course).provider : (detail as CurrentAffair).category}
          </p>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
            {isCourses ? (detail as Course).title : (detail as CurrentAffair).title}
          </h1>
          <p className="mt-6 whitespace-pre-line leading-7 text-[#63736c]">
            {isCourses
              ? (detail as Course).description || "Course details have not been provided."
              : (detail as CurrentAffair).content}
          </p>
          {isCourses && (detail as Course).course_url && (
            <a
              className="mt-7 inline-block rounded-xl bg-[#145b48] px-5 py-3 text-sm font-semibold text-white"
              href={(detail as Course).course_url}
              target="_blank"
              rel="noreferrer"
            >
              Visit course ↗
            </a>
          )}
        </article>
      </main>
    );

  const items = isCourses
    ? courses.map((x) => ({
        id: x.id,
        title: x.title,
        eyebrow: x.provider,
        copy: x.description || x.category || "Course details",
        meta: [x.difficulty, x.duration, x.mode].filter(Boolean).join(" · "),
      }))
    : isAffairs
      ? affairs.map((x) => ({
          id: x.id,
          title: x.title,
          eyebrow: x.category,
          copy: x.summary,
          meta: x.published_at ? date(x.published_at) : "Publication date not provided",
        }))
      : tests.map((x) => ({
          id: x.id,
          title: x.title,
          eyebrow: titleize(x.type),
          copy: "Practice with a structured test.",
          meta: `${x.duration_minutes} minutes`,
        }));
  return (
    <main className="mx-auto max-w-7xl px-5 py-12 lg:px-8">
      <p className="text-xs font-bold uppercase tracking-[.16em] text-[#668b59]">
        Learn and prepare
      </p>
      <h1 className="mt-3 text-4xl font-semibold tracking-tight">{title}</h1>
      <p className="mt-3 max-w-2xl leading-7 text-[#63736c]">
        Explore resources published through Elevra. Details reflect the information currently
        available.
      </p>
      {loading ? (
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((x) => (
            <div key={x} className="h-44 animate-pulse rounded-2xl bg-[#e8ede7]" />
          ))}
        </div>
      ) : error ? (
        <div className="mt-8">
          <State message={error} retry={() => location.reload()} />
        </div>
      ) : !items.length ? (
        <div className="mt-8">
          <State
            message={`No ${title.toLowerCase()} are available right now. Please check back soon.`}
          />
        </div>
      ) : (
        <section className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((x) => (
            <Link
              key={x.id}
              href={`/${route}/${x.id}`}
              className="rounded-2xl border border-[#e3e9e4] bg-white p-5 transition hover:border-[#b7c9b8] hover:shadow-md"
            >
              <p className="text-xs font-semibold text-[#668b59]">{x.eyebrow}</p>
              <h2 className="mt-3 text-lg font-semibold">{x.title}</h2>
              <p className="mt-2 line-clamp-3 text-sm leading-6 text-[#63736c]">{x.copy}</p>
              <p className="mt-5 border-t border-[#edf0ec] pt-4 text-xs text-[#63736c]">{x.meta}</p>
            </Link>
          ))}
        </section>
      )}
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
  if (parts[0] === "profile")
    return (
      <SimplePage
        title="Your profile"
        eyebrow="Account"
        copy="Profile settings and personal preferences are available when account authentication is connected."
      />
    );
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
  if (["courses", "current-affairs", "tests"].includes(parts[0]))
    return <ResourceHub route={parts[0]} slug={parts[1]} />;
  if (parts[0] === "saved") return <Dashboard />;
  return (
    <main className="mx-auto max-w-4xl px-5 py-16">
      <h1 className="text-4xl font-bold">{titleize(parts[0])}</h1>
      <p className="mt-3 text-slate-600">This part of Elevra is being prepared.</p>
    </main>
  );
}
