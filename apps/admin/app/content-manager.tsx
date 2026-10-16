"use client";

import Link from "next/link";
import React, { useCallback, useEffect, useMemo, useState, type ChangeEvent, type FormEvent } from "react";
import {
  ArrowRight,
  BookOpenCheck,
  BriefcaseBusiness,
  ClipboardList,
  FileText,
  GraduationCap,
  Newspaper,
  Plus,
} from "lucide-react";
import {
  type AdminContentKind,
  type AdminQueueItem,
  type AdminTestDetail,
  ApiError,
  createApiClient,
} from "@elevra/api-client";
import { useAuth } from "./admin-session";

const api = createApiClient({
  baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1",
});

type ContentRow = Record<string, unknown> & {
  id: string;
  slug: string;
  title?: string;
  name?: string;
  status: string;
  verified?: boolean;
  questions?: AdminTestDetail["questions"];
};
type Field = {
  name: string;
  label: string;
  kind?: "text" | "textarea" | "select" | "checkbox" | "date" | "number" | "url";
  required?: boolean;
  options?: string[];
  maxLength?: number;
  min?: number;
  max?: number;
  hint?: string;
};

const fields: Record<AdminContentKind, Field[]> = {
  exams: [
    { name: "name", label: "Exam name", required: true, maxLength: 255 },
    { name: "slug", label: "URL slug", required: true, maxLength: 255, hint: "Lowercase letters, numbers, and hyphens." },
    { name: "category", label: "Category", kind: "select", required: true, options: ["government", "engineering", "medical", "management", "university", "defence", "banking", "railway", "teaching", "state_exams", "other"] },
    { name: "conducting_body", label: "Conducting body", maxLength: 255 },
    { name: "short_description", label: "Short description", maxLength: 512 },
    { name: "description", label: "Description", kind: "textarea" },
    { name: "eligibility_summary", label: "Eligibility summary", kind: "textarea" },
    { name: "education_requirements", label: "Education requirements", kind: "textarea" },
    { name: "age_limit", label: "Age limit", maxLength: 255 },
    { name: "application_start", label: "Application starts", kind: "date" },
    { name: "application_deadline", label: "Application deadline", kind: "date" },
    { name: "exam_date", label: "Exam date", kind: "date" },
    { name: "result_date", label: "Result date", kind: "date" },
    { name: "official_website", label: "Official website", kind: "url" },
    { name: "source_name", label: "Source name", maxLength: 255 },
    { name: "source_url", label: "Source URL", kind: "url" },
  ],
  opportunities: [
    { name: "title", label: "Opportunity title", required: true, maxLength: 255 },
    { name: "slug", label: "URL slug", required: true, maxLength: 255 },
    { name: "type", label: "Type", kind: "select", required: true, options: ["job", "internship", "scholarship", "hackathon", "competition", "fellowship", "research", "bootcamp", "event", "other"] },
    { name: "organization", label: "Organization", maxLength: 255 },
    { name: "description", label: "Description", kind: "textarea" },
    { name: "eligibility", label: "Eligibility", kind: "textarea" },
    { name: "location", label: "Location", maxLength: 255 },
    { name: "remote", label: "Remote opportunity", kind: "checkbox" },
    { name: "deadline", label: "Deadline", kind: "date" },
    { name: "application_url", label: "Application URL", kind: "url" },
    { name: "source_url", label: "Source URL", kind: "url" },
  ],
  courses: [
    { name: "title", label: "Course title", required: true, maxLength: 255 },
    { name: "slug", label: "URL slug", required: true, maxLength: 255 },
    { name: "provider", label: "Provider", required: true, maxLength: 255 },
    { name: "description", label: "Description", kind: "textarea" },
    { name: "category", label: "Category", maxLength: 100 },
    { name: "difficulty", label: "Difficulty", maxLength: 50 },
    { name: "duration", label: "Duration", maxLength: 100 },
    { name: "mode", label: "Mode", maxLength: 50 },
    { name: "skills", label: "Skills", hint: "Separate skills with commas." },
    { name: "certificate", label: "Certificate included", kind: "checkbox" },
    { name: "course_url", label: "Course URL", kind: "url" },
    { name: "official_url", label: "Official URL", kind: "url" },
  ],
  "current-affairs": [
    { name: "title", label: "Article title", required: true, maxLength: 320 },
    { name: "slug", label: "URL slug", required: true, maxLength: 255 },
    { name: "summary", label: "Summary", kind: "textarea", required: true },
    { name: "content", label: "Article content", kind: "textarea", required: true },
    { name: "category", label: "Category", required: true, maxLength: 100 },
    { name: "source", label: "Source name", required: true, maxLength: 255 },
    { name: "source_url", label: "Source URL", kind: "url" },
  ],
  tests: [
    { name: "title", label: "Test title", required: true, maxLength: 255 },
    { name: "slug", label: "URL slug", required: true, maxLength: 255 },
    { name: "description", label: "Description", kind: "textarea" },
    { name: "type", label: "Type", kind: "select", required: true, options: ["mock", "practice", "topic", "previous_year"] },
    { name: "duration_minutes", label: "Duration in minutes", kind: "number", required: true, min: 1, max: 600 },
  ],
};

const states: Record<AdminContentKind, string[]> = {
  exams: ["draft", "published", "archived"],
  opportunities: ["draft", "published", "closed", "archived"],
  courses: ["draft", "pending_review", "verified", "published", "rejected", "expired"],
  "current-affairs": ["draft", "pending_review", "verified", "published", "rejected", "expired"],
  tests: ["draft", "published"],
};
const titles: Record<AdminContentKind, string> = {
  exams: "Exams",
  opportunities: "Opportunities",
  courses: "Courses",
  "current-affairs": "Current affairs",
  tests: "Tests",
};
const statusClass = (value: string) =>
  value === "published" ? "bg-[#e8f2e4] text-[#315d40]" : value === "pending_review" ? "bg-[#f1f3e7] text-[#667344]" : "bg-slate-100 text-slate-700";
const inputClass = "mt-1 w-full rounded-xl border border-[#d8e1da] bg-white px-3 py-2.5 text-sm outline-none focus:border-[#56816d] focus:ring-2 focus:ring-[#d5e7cf]";

function contentActions(kind: AdminContentKind, row: ContentRow) {
  const actions: Array<{ action: string; label: string; destructive?: boolean }> = [];
  if (["exams", "opportunities"].includes(kind)) {
    if (row.status === "draft" || (kind === "opportunities" && ["archived", "closed"].includes(row.status))) actions.push({ action: "publish", label: "Publish" });
    if (row.status === "published") actions.push({ action: "unpublish", label: "Unpublish" });
    if (kind === "opportunities" && row.status === "published") actions.push({ action: "close", label: "Close" });
    if (row.status !== "archived") actions.push({ action: "archive", label: "Archive", destructive: true });
    if (["draft", "published", "archived", "closed"].includes(row.status))
      actions.push({ action: row.verified ? "unverify" : "verify", label: row.verified ? "Remove verification" : "Verify" });
  } else if (kind === "courses") {
    const labels: Record<string, string> = { draft: "submit", pending_review: "verify", verified: "publish", published: "expire", rejected: "", expired: "" };
    const action = labels[row.status];
    if (action) actions.push({ action, label: action === "submit" ? "Submit for review" : action[0].toUpperCase() + action.slice(1), destructive: action === "expire" });
    if (row.status === "pending_review") actions.push({ action: "reject", label: "Reject", destructive: true });
  } else if (kind === "current-affairs") {
    const labels: Record<string, string> = { draft: "review", pending_review: "verify", verified: "publish", published: "expire", rejected: "", expired: "" };
    const action = labels[row.status];
    if (action) actions.push({ action, label: action === "review" ? "Submit for review" : action[0].toUpperCase() + action.slice(1), destructive: action === "expire" });
    if (row.status === "pending_review") actions.push({ action: "reject", label: "Reject", destructive: true });
  } else if (kind === "tests") {
    actions.push(row.status === "published" ? { action: "unpublish", label: "Unpublish" } : { action: "publish", label: "Publish" });
  }
  return actions;
}

function titleOf(item: AdminQueueItem) {
  return item.title || item.slug;
}

export function AdminWorkspace({ route }: { route: string }) {
  if (route === "dashboard" || route === "") return <AdminDashboard />;
  if (route === "queue" || route === "verification") return <AdminQueue />;
  const resource = route as AdminContentKind;
  if (!(resource in titles)) return <main className="rounded-2xl bg-white p-8"><h1 className="text-2xl font-bold">Section unavailable</h1><p className="mt-2 text-slate-600">Choose a supported content section from the admin navigation.</p></main>;
  return <ContentManager key={resource} kind={resource} />;
}

function AdminDashboard() {
  const { withSession } = useAuth();
  const [drafts, setDrafts] = useState<AdminQueueItem[]>([]);
  const [reviews, setReviews] = useState<AdminQueueItem[]>([]);
  const [draftTotal, setDraftTotal] = useState(0);
  const [reviewTotal, setReviewTotal] = useState(0);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [draftPage, reviewPage] = await withSession((token) => Promise.all([
        api.listAdminQueue({ status: "draft", page: 1, page_size: 5 }, token),
        api.listAdminQueue({ status: "pending_review", page: 1, page_size: 5 }, token),
      ]));
      setDrafts(draftPage.items);
      setReviews(reviewPage.items);
      setDraftTotal(draftPage.total);
      setReviewTotal(reviewPage.total);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to load content activity.");
    } finally {
      setLoading(false);
    }
  }, [withSession]);
  useEffect(() => { void load(); }, [load]);
  return (
    <main className="mx-auto max-w-[1500px] space-y-7 pb-10">
      <header className="relative isolate overflow-hidden rounded-[1.75rem] bg-[#174a3a] px-6 py-7 text-white shadow-[0_22px_55px_rgba(23,74,58,.15)] sm:px-9 sm:py-9">
        <div className="pointer-events-none absolute -right-8 -top-24 -z-10 h-72 w-72 rounded-full border-[44px] border-white/[.06]" />
        <div className="pointer-events-none absolute -bottom-36 right-1/4 -z-10 h-72 w-72 rounded-full bg-[#a7c68d]/10 blur-3xl" />
        <div className="flex flex-col justify-between gap-7 sm:flex-row sm:items-end">
          <div className="max-w-2xl">
            <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-[.18em] text-[#d5e7c9]">
              <span className="h-1.5 w-1.5 rounded-full bg-[#b7d49e]" /> Elevra content studio
            </p>
            <h1 className="mt-3 text-3xl font-semibold tracking-[-.045em] sm:text-4xl">A clear view of what needs doing.</h1>
            <p className="mt-3 max-w-xl text-sm leading-6 text-white/75 sm:text-base">
              Create and review the content that helps students decide what comes next.
            </p>
          </div>
          <Link href="/exams" className="inline-flex w-fit shrink-0 items-center gap-2 rounded-xl bg-[#dce9d1] px-4 py-3 text-sm font-bold text-[#173b2f] transition hover:-translate-y-0.5 hover:bg-[#c9ddb9] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white">
            <Plus size={17} aria-hidden="true" /> Create content
          </Link>
        </div>
        <div className="mt-7 flex flex-wrap gap-2 text-xs font-medium text-white/75">
          <span className="rounded-full border border-white/15 bg-white/[.07] px-3 py-1.5">Exams</span>
          <span className="rounded-full border border-white/15 bg-white/[.07] px-3 py-1.5">Opportunities</span>
          <span className="rounded-full border border-white/15 bg-white/[.07] px-3 py-1.5">Courses</span>
          <span className="rounded-full border border-white/15 bg-white/[.07] px-3 py-1.5">Current affairs</span>
          <span className="rounded-full border border-white/15 bg-white/[.07] px-3 py-1.5">Practice tests</span>
        </div>
      </header>

      {error && <Feedback tone="error" message={error} retry={() => void load()} />}

      <section aria-label="Content overview" className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <DashboardMetric label="Drafts" value={loading ? null : draftTotal} note="Saved content not yet published" icon={FileText} tone="sage" />
        <DashboardMetric label="Pending review" value={loading ? null : reviewTotal} note="Submissions awaiting a decision" icon={ClipboardList} tone="olive" />
        <DashboardMetric label="Content areas" value={5} note="Manage the student resource library" icon={BookOpenCheck} tone="mint" />
        <Link href="/queue" className="group flex min-h-[142px] items-center justify-between rounded-2xl border border-[#dbe6d8] bg-[#eef4e8] p-5 transition hover:border-[#bfd2b9] hover:bg-[#e7f0df] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#86a875]">
          <span><span className="block text-sm font-bold text-[#28483b]">Open review queue</span><span className="mt-1 block text-xs leading-5 text-[#64736b]">See drafts and review items</span></span>
          <span className="grid h-10 w-10 place-items-center rounded-xl bg-white text-[#155b48] shadow-sm transition group-hover:translate-x-0.5"><ArrowRight size={17} aria-hidden="true" /></span>
        </Link>
      </section>

      <div className="grid items-start gap-6 xl:grid-cols-[minmax(0,1.45fr)_minmax(280px,.75fr)]">
        <section className="space-y-6" aria-label="Recent content activity">
          <QueuePreview title="Pending review" description="Review these submissions before they move forward." count={reviewTotal} items={reviews} href="/queue?status=pending_review" icon={ClipboardList} loading={loading} />
          <QueuePreview title="Recently saved drafts" description="Pick up where you left off with unpublished content." count={draftTotal} items={drafts} href="/queue?status=draft" icon={FileText} loading={loading} />
        </section>
        <QuickCreatePanel />
      </div>
    </main>
  );
}

function DashboardMetric({
  label,
  value,
  note,
  icon: Icon,
  tone,
}: {
  label: string;
  value: number | null;
  note: string;
  icon: typeof FileText;
  tone: "sage" | "olive" | "mint";
}) {
  const tones = {
    sage: "bg-[#eaf1e5] text-[#42634e]",
    olive: "bg-[#f1f3e7] text-[#667344]",
    mint: "bg-[#e8f2ed] text-[#3d6a59]",
  };
  return (
    <article className="rounded-2xl border border-[#e1e8e1] bg-white p-5 shadow-[0_8px_24px_rgba(25,54,39,.035)]">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-[#64736b]">{label}</p>
          <p className="mt-3 text-3xl font-semibold tracking-[-.05em] text-[#17251f]" aria-live="polite">
            {value === null ? <span className="inline-block h-9 w-12 animate-pulse rounded-lg bg-[#edf1eb]" aria-label="Loading" /> : value}
          </p>
        </div>
        <span className={`grid h-10 w-10 place-items-center rounded-xl ${tones[tone]}`}><Icon size={19} strokeWidth={1.8} aria-hidden="true" /></span>
      </div>
      <p className="mt-2 text-xs leading-5 text-[#7a867e]">{note}</p>
    </article>
  );
}

function QueuePreview({
  title,
  description,
  count,
  items,
  href,
  icon: Icon,
  loading,
}: {
  title: string;
  description: string;
  count: number;
  items: AdminQueueItem[];
  href: string;
  icon: typeof FileText;
  loading: boolean;
}) {
  return (
    <section className="overflow-hidden rounded-2xl border border-[#e1e8e1] bg-white shadow-[0_8px_24px_rgba(25,54,39,.035)]">
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-[#edf1eb] px-5 py-5 sm:px-6">
        <div className="flex items-center gap-3">
          <span className="grid h-10 w-10 place-items-center rounded-xl bg-[#eef4e8] text-[#42634e]"><Icon size={18} aria-hidden="true" /></span>
          <div><h2 className="font-semibold tracking-tight text-[#20352a]">{title}</h2><p className="mt-0.5 text-xs text-[#7a867e]">{description}</p></div>
        </div>
        <div className="flex items-center gap-3">
          {!loading && <span className="rounded-full bg-[#f3f6f0] px-2.5 py-1 text-xs font-bold text-[#42634e]">{count}</span>}
          <Link href={href} className="inline-flex items-center gap-1.5 text-sm font-semibold text-[#155b48] hover:text-[#104537] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#86a875]">View all <ArrowRight size={15} aria-hidden="true" /></Link>
        </div>
      </div>
      {loading ? (
        <div role="status" className="space-y-3 p-5 sm:p-6"><span className="sr-only">Loading {title.toLowerCase()}</span>{[0, 1, 2].map((item) => <div key={item} className="h-12 animate-pulse rounded-xl bg-[#f3f6f0]" />)}</div>
      ) : items.length ? (
        <ul className="divide-y divide-[#edf1eb] px-5 sm:px-6">
          {items.map((item) => (
            <li key={`${item.kind}-${item.id}`} className="flex items-center gap-3 py-3.5">
              <span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-[#f4f7f1] text-[#6f8568]"><ContentKindIcon kind={item.kind} /></span>
              <div className="min-w-0 flex-1"><p className="truncate text-sm font-semibold text-[#263a30]">{titleOf(item)}</p><p className="mt-1 text-xs text-[#7a867e]">{titles[item.kind]} <span aria-hidden="true">·</span> {new Date(item.created_at).toLocaleDateString()}</p></div>
              <StatusBadge value={item.status} />
            </li>
          ))}
        </ul>
      ) : (
        <div className="px-6 py-8 text-center"><span className="mx-auto grid h-11 w-11 place-items-center rounded-2xl bg-[#f3f6f0] text-[#71876a]"><Icon size={19} aria-hidden="true" /></span><p className="mt-3 text-sm font-semibold text-[#34493c]">Nothing here right now</p><p className="mt-1 text-xs text-[#7a867e]">New {title.toLowerCase()} will appear here.</p></div>
      )}
    </section>
  );
}

function ContentKindIcon({ kind }: { kind: AdminContentKind }) {
  const Icon = {
    exams: GraduationCap,
    opportunities: BriefcaseBusiness,
    courses: BookOpenCheck,
    "current-affairs": Newspaper,
    tests: ClipboardList,
  }[kind];
  return <Icon size={17} strokeWidth={1.8} aria-hidden="true" />;
}

function QuickCreatePanel() {
  const actions: Array<{ kind: AdminContentKind; label: string; detail: string; icon: typeof FileText }> = [
    { kind: "exams", label: "Exam", detail: "Add exam details", icon: GraduationCap },
    { kind: "opportunities", label: "Opportunity", detail: "Add a new listing", icon: BriefcaseBusiness },
    { kind: "courses", label: "Course", detail: "Create a learning resource", icon: BookOpenCheck },
    { kind: "current-affairs", label: "Current affairs", detail: "Write an article", icon: Newspaper },
    { kind: "tests", label: "Practice test", detail: "Build a test", icon: ClipboardList },
  ];
  return (
    <aside className="rounded-2xl border border-[#e1e8e1] bg-white p-5 shadow-[0_8px_24px_rgba(25,54,39,.035)] sm:p-6">
      <div><p className="text-xs font-bold uppercase tracking-[.14em] text-[#668b59]">Quick create</p><h2 className="mt-2 text-xl font-semibold tracking-tight text-[#20352a]">Add to the library</h2><p className="mt-1 text-sm leading-6 text-[#7a867e]">Choose a content type to open its workspace.</p></div>
      <ul className="mt-5 space-y-1.5">
        {actions.map(({ kind, label, detail, icon: Icon }) => (
          <li key={kind}><Link href={`/${kind}`} className="group flex items-center gap-3 rounded-xl p-3 transition hover:bg-[#f5f8f2] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#86a875]"><span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-[#eef4e8] text-[#42634e] transition group-hover:bg-[#e3eddb]"><Icon size={18} aria-hidden="true" /></span><span className="min-w-0 flex-1"><span className="block text-sm font-semibold text-[#28483b]">{label}</span><span className="mt-0.5 block text-xs text-[#7a867e]">{detail}</span></span><ArrowRight size={16} className="text-[#91a294] transition group-hover:translate-x-0.5 group-hover:text-[#155b48]" aria-hidden="true" /></Link></li>
        ))}
      </ul>
      <div className="mt-5 rounded-xl bg-[#f4f7f1] p-4"><p className="text-xs font-semibold text-[#42634e]">Publishing tip</p><p className="mt-1 text-xs leading-5 text-[#6d7b70]">Save as a draft first, then review the source and details before publishing.</p></div>
    </aside>
  );
}

function AdminQueue() {
  const { withSession } = useAuth();
  const [queueStatus, setQueueStatus] = useState<"draft" | "pending_review">("draft");
  const [items, setItems] = useState<AdminQueueItem[]>([]);
  const [page, setPage] = useState(1);
  const [pageCount, setPageCount] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const result = await withSession(token => api.listAdminQueue({ status: queueStatus, page, page_size: 20 }, token));
      setItems(result.items); setTotal(result.total); setPageCount(result.total_pages || 1);
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Unable to load the queue."); }
    finally { setLoading(false); }
  }, [page, queueStatus, withSession]);
  useEffect(() => { void load(); }, [load]);
  return <main className="space-y-6"><header><p className="text-sm font-bold uppercase tracking-[.14em] text-[#668b59]">Content operations</p><h1 className="mt-2 text-3xl font-semibold">Draft and review queue</h1><p className="mt-2 text-slate-600">Items are selected by their persisted status. Exams, opportunities and tests have no pending-review state.</p></header>
    <div className="flex flex-wrap items-center gap-2" role="group" aria-label="Queue status">{(["draft", "pending_review"] as const).map(value => <button key={value} aria-pressed={queueStatus === value} onClick={() => { setQueueStatus(value); setPage(1); }} className={`rounded-full border px-4 py-2 text-sm font-semibold ${queueStatus === value ? "border-[#145b48] bg-[#e8f2e4] text-[#145b48]" : "bg-white text-slate-600"}`}>{value === "draft" ? "Drafts" : "Pending review"}</button>)}</div>
    {error && <Feedback tone="error" message={error} retry={() => void load()} />}
    {loading ? <p role="status" className="rounded-xl bg-white p-6">Loading queue…</p> : items.length === 0 ? <p className="rounded-xl border border-dashed bg-white p-8 text-center text-slate-600">No {queueStatus === "draft" ? "drafts" : "items pending review"}.</p> : <div className="overflow-hidden rounded-2xl border bg-white"><div className="overflow-x-auto"><table className="w-full min-w-[620px] text-left text-sm"><thead className="bg-[#f7f8f4] text-slate-600"><tr><th className="p-4">Content</th><th className="p-4">Type</th><th className="p-4">Status</th><th className="p-4">Created</th><th className="p-4">Action</th></tr></thead><tbody className="divide-y">{items.map(item => <tr key={`${item.kind}-${item.id}`}><td className="p-4 font-semibold">{titleOf(item)}</td><td className="p-4">{titles[item.kind]}</td><td className="p-4"><StatusBadge value={item.status} /></td><td className="p-4">{new Date(item.created_at).toLocaleDateString()}</td><td className="p-4"><Link className="font-semibold text-[#145b48] underline underline-offset-4" href={`/${item.kind}?search=${encodeURIComponent(item.slug)}`}>Open items</Link></td></tr>)}</tbody></table></div></div>}
    {!loading && !error && pageCount > 1 && <Pagination page={page} pages={pageCount} total={total} onPage={setPage} />}
  </main>;
}

function ContentManager({ kind }: { kind: AdminContentKind }) {
  const { withSession } = useAuth();
  const [items, setItems] = useState<ContentRow[]>([]);
  const [selected, setSelected] = useState<ContentRow | null>(null);
  const [form, setForm] = useState<Record<string, string | boolean>>({});
  const [filterStatus, setFilterStatus] = useState("");
  const [filterCategory, setFilterCategory] = useState("");
  const [filterType, setFilterType] = useState("");
  const [searchDraft, setSearchDraft] = useState("");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [questionEditId, setQuestionEditId] = useState("");
  const [questionText, setQuestionText] = useState("");
  const [questionExplanation, setQuestionExplanation] = useState("");
  const [optionTexts, setOptionTexts] = useState(["", "", "", ""]);
  const [correctOption, setCorrectOption] = useState(0);

  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const params: Record<string, string | number | undefined> = {
        page,
        page_size: 12,
        q: search || undefined,
        status: filterStatus || undefined,
        category: filterCategory || undefined,
        type: filterType || undefined,
      };
      const result = await withSession(token => api.listAdminContent<ContentRow>(kind, params, token));
      setItems(result.items); setPages(result.total_pages || 1); setTotal(result.total);
      if (selected) {
        const refreshed = result.items.find(item => item.id === selected.id);
        if (refreshed) { setSelected(refreshed); setForm(toForm(kind, refreshed)); }
      }
    } catch (cause) { setError(cause instanceof Error ? cause.message : `Unable to load ${titles[kind].toLowerCase()}.`); }
    finally { setLoading(false); }
  }, [filterCategory, filterStatus, filterType, kind, page, search, selected, withSession]);
  useEffect(() => { void load(); }, [load]);

  useEffect(() => {
    const requested = new URLSearchParams(window.location.search).get("search");
    if (requested) { setSearchDraft(requested); setSearch(requested); }
  }, []);

  function startCreate() {
    setSelected(null); setForm(defaultForm(kind)); setMessage(""); setError("");
    setQuestionEditId(""); resetQuestion();
  }

  function startEdit(item: ContentRow) {
    setSelected(item); setForm(toForm(kind, item)); setMessage(""); setError("");
    setQuestionEditId(""); resetQuestion();
    void withSession(token => api.getAdminContent<ContentRow>(kind, item.id, token))
      .then(detail => { setSelected(detail); setForm(toForm(kind, detail)); })
      .catch(cause => setError(cause instanceof Error ? cause.message : "Unable to load content details."));
  }

  function resetQuestion() {
    setQuestionText(""); setQuestionExplanation(""); setOptionTexts(["", "", "", ""]); setCorrectOption(0);
  }

  async function submitContent(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setSaving(true); setError(""); setMessage("");
    const data: Record<string, unknown> = {};
    for (const field of fields[kind]) {
      const raw = form[field.name];
      if (field.kind === "checkbox") data[field.name] = Boolean(raw);
      else if (field.name === "skills") data.skills = String(raw || "").split(",").map(value => value.trim()).filter(Boolean);
      else if (field.kind === "number") data[field.name] = Number(raw);
      else data[field.name] = raw === "" && !field.required ? null : raw;
    }
    try {
      const item = await withSession(token => selected
        ? api.updateAdminContent<ContentRow>(kind, selected.id, data, token)
        : api.createAdminContent<ContentRow>(kind, data, token));
      setSelected(item); setForm(toForm(kind, item)); setMessage(selected ? "Content changes saved." : "Draft created.");
      await load();
    } catch (cause) { setError(cause instanceof ApiError ? cause.message : cause instanceof Error ? cause.message : "Unable to save content."); }
    finally { setSaving(false); }
  }

  async function runAction(action: string) {
    if (!selected) return;
    const destructive = ["archive", "expire"].includes(action);
    if (destructive && !window.confirm(`Confirm ${action} for “${selected.title || selected.name}”?`)) return;
    setSaving(true); setError(""); setMessage("");
    try {
      const updated = await withSession(token => api.adminContentAction<ContentRow>(kind, selected.id, action, token));
      setSelected(updated); setForm(toForm(kind, updated)); setMessage(`Status action completed: ${action}.`); await load();
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Unable to update publication status."); }
    finally { setSaving(false); }
  }

  async function deleteDraftTest() {
    if (!selected || kind !== "tests" || !window.confirm("Delete this draft test? This cannot be undone.")) return;
    setSaving(true); setError(""); setMessage("");
    try { await withSession(token => api.deleteAdminContent(kind, selected.id, token)); setSelected(null); setForm({}); setMessage("Draft test deleted."); await load(); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Unable to delete this test."); }
    finally { setSaving(false); }
  }

  async function saveQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selected || kind !== "tests") return;
    const options = optionTexts.map((text, position) => ({ text: text.trim(), position, is_correct: position === correctOption })).filter(option => option.text);
    setSaving(true); setError(""); setMessage("");
    try {
      const data = { text: questionText.trim(), explanation: questionExplanation.trim() || null, position: questionEditId ? selected.questions?.find(item => item.id === questionEditId)?.position ?? 0 : selected.questions?.length ?? 0, options };
      await withSession(token => questionEditId
        ? api.updateAdminTestQuestion(selected.id, questionEditId, data, token)
        : api.addAdminTestQuestion(selected.id, data, token));
      const detail = await withSession(token => api.getAdminContent<ContentRow>(kind, selected.id, token));
      setSelected(detail); setForm(toForm(kind, detail)); setQuestionEditId(""); resetQuestion(); setMessage(questionEditId ? "Question updated." : "Question added."); await load();
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Unable to save the question."); }
    finally { setSaving(false); }
  }

  async function editQuestion(questionId: string) {
    const question = selected?.questions?.find(item => item.id === questionId);
    if (!question) return;
    setQuestionEditId(question.id); setQuestionText(question.text); setQuestionExplanation(question.explanation || "");
    setOptionTexts(Array.from({ length: 4 }, (_, index) => question.options[index]?.text || ""));
    setCorrectOption(Math.max(0, question.options.findIndex(option => option.is_correct)));
  }

  async function removeQuestion(questionId: string) {
    if (!selected || !window.confirm("Remove this question from the draft test?")) return;
    setSaving(true); setError("");
    try {
      await withSession(token => api.deleteAdminTestQuestion(selected.id, questionId, token));
      const detail = await withSession(token => api.getAdminContent<ContentRow>(kind, selected.id, token));
      setSelected(detail); setForm(toForm(kind, detail)); setMessage("Question removed."); await load();
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Unable to remove the question."); }
    finally { setSaving(false); }
  }

  const actions = useMemo(() => selected ? contentActions(kind, selected) : [], [kind, selected]);
  return <main className="space-y-6">
    <header className="flex flex-wrap items-end justify-between gap-4"><div><p className="text-sm font-bold uppercase tracking-[.14em] text-[#668b59]">Content management</p><h1 className="mt-2 text-3xl font-semibold">{titles[kind]}</h1><p className="mt-2 text-slate-600">Create, revise and publish persisted {titles[kind].toLowerCase()}.</p></div><button onClick={startCreate} className="rounded-xl bg-[#145b48] px-4 py-2.5 text-sm font-semibold text-white hover:bg-[#103f34] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2">Create {kind === "current-affairs" ? "article" : kind === "tests" ? "test" : kind.slice(0, -1)}</button></header>
    <section className="grid gap-3 rounded-2xl border border-[#e2e9e2] bg-white p-4 sm:grid-cols-2 lg:grid-cols-4 lg:items-end"><label className="text-sm font-semibold">Search<input value={searchDraft} onChange={event => setSearchDraft(event.target.value)} onKeyDown={event => { if (event.key === "Enter") { setPage(1); setSearch(searchDraft.trim()); } }} placeholder={`Search ${titles[kind].toLowerCase()}`} className={inputClass} /></label><label className="text-sm font-semibold">Status<select value={filterStatus} onChange={event => { setFilterStatus(event.target.value); setPage(1); }} className={inputClass}><option value="">All statuses</option>{states[kind].map(value => <option key={value} value={value}>{value.replaceAll("_", " ")}</option>)}</select></label>{["exams", "courses", "current-affairs"].includes(kind) && <label className="text-sm font-semibold">Category<input value={filterCategory} onChange={event => { setFilterCategory(event.target.value); setPage(1); }} className={inputClass} /></label>}{["opportunities", "tests"].includes(kind) && <label className="text-sm font-semibold">Type<select value={filterType} onChange={event => { setFilterType(event.target.value); setPage(1); }} className={inputClass}><option value="">All types</option>{(kind === "tests" ? fields.tests.find(field => field.name === "type")?.options : fields.opportunities.find(field => field.name === "type")?.options)?.map(value => <option key={value} value={value}>{value.replaceAll("_", " ")}</option>)}</select></label>}<button onClick={() => { setPage(1); setSearch(searchDraft.trim()); }} className="rounded-xl border border-[#cbd8ce] px-4 py-2.5 text-sm font-semibold text-[#145b48]">Search</button></section>
    {error && <Feedback tone="error" message={error} retry={() => void load()} />}{message && <Feedback tone="success" message={message} />}
    <section className="overflow-hidden rounded-2xl border border-[#e2e9e2] bg-white"><div className="overflow-x-auto"><table className="w-full min-w-[680px] text-left text-sm"><thead className="bg-[#f7f8f4] text-slate-600"><tr><th className="p-4">Title</th><th className="p-4">Slug</th><th className="p-4">Status</th><th className="p-4">Updated</th><th className="p-4">Edit</th></tr></thead><tbody className="divide-y">{loading ? <tr><td className="p-6" colSpan={5} role="status">Loading {titles[kind].toLowerCase()}…</td></tr> : items.length ? items.map(item => <tr key={item.id}><td className="p-4 font-semibold">{String(item.title || item.name || "Untitled")}</td><td className="p-4 text-slate-600">{item.slug}</td><td className="p-4"><StatusBadge value={item.status} verified={Boolean(item.verified)} /></td><td className="p-4">{item.updated_at ? new Date(String(item.updated_at)).toLocaleDateString() : "—"}</td><td className="p-4"><button onClick={() => startEdit(item)} className="font-semibold text-[#145b48] underline underline-offset-4">Edit</button></td></tr>) : <tr><td className="p-8 text-center text-slate-600" colSpan={5}>No {titles[kind].toLowerCase()} match these filters.</td></tr>}</tbody></table></div></section>
    {!loading && !error && pages > 1 && <Pagination page={page} pages={pages} total={total} onPage={setPage} />}
    {selected !== null || Object.keys(form).length > 0 ? <section className="rounded-2xl border border-[#dfe7df] bg-white p-5 sm:p-7"><div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-xs font-bold uppercase tracking-wider text-[#668b59]">{selected ? "Edit record" : "New draft"}</p><h2 className="mt-1 text-2xl font-semibold">{String(form.title || form.name || (selected ? "Content details" : `Create ${titles[kind].toLowerCase()}`))}</h2>{selected && <div className="mt-2"><StatusBadge value={selected.status} verified={Boolean(selected.verified)} /></div>}</div><button onClick={() => { setSelected(null); setForm({}); setQuestionEditId(""); resetQuestion(); }} className="rounded-lg border px-3 py-2 text-sm">Close editor</button></div>
      <form onSubmit={event => void submitContent(event)} className="mt-6 grid gap-4 sm:grid-cols-2">{fields[kind].map(field => <FieldControl key={field.name} field={field} value={form[field.name]} disabled={saving} onChange={value => setForm(current => ({ ...current, [field.name]: value }))} />)}<div className="flex flex-wrap gap-3 sm:col-span-2"><button disabled={saving} className="rounded-xl bg-[#145b48] px-5 py-2.5 font-semibold text-white disabled:opacity-60">{saving ? "Saving…" : selected ? "Save changes" : "Create draft"}</button>{selected && <div className="flex flex-wrap gap-2">{actions.map(action => <button key={action.action} type="button" disabled={saving} onClick={() => void runAction(action.action)} className={`rounded-xl border px-4 py-2.5 text-sm font-semibold disabled:opacity-50 ${action.destructive ? "border-red-200 text-red-800" : "border-[#cbd8ce] text-[#145b48]"}`}>{action.label}</button>)}{kind === "tests" && selected.status === "draft" && <button type="button" disabled={saving} onClick={() => void deleteDraftTest()} className="rounded-xl border border-red-200 px-4 py-2.5 text-sm font-semibold text-red-800 disabled:opacity-50">Delete draft test</button>}</div>}</div></form>
      {kind === "tests" && selected && <TestQuestionEditor selected={selected} saving={saving} questionEditId={questionEditId} questionText={questionText} setQuestionText={setQuestionText} questionExplanation={questionExplanation} setQuestionExplanation={setQuestionExplanation} optionTexts={optionTexts} setOptionTexts={setOptionTexts} correctOption={correctOption} setCorrectOption={setCorrectOption} onSubmit={saveQuestion} onEdit={editQuestion} onRemove={removeQuestion} onCancel={() => { setQuestionEditId(""); resetQuestion(); }} />}
    </section> : null}
  </main>;
}

function TestQuestionEditor({ selected, saving, questionEditId, questionText, setQuestionText, questionExplanation, setQuestionExplanation, optionTexts, setOptionTexts, correctOption, setCorrectOption, onSubmit, onEdit, onRemove, onCancel }: {
  selected: ContentRow; saving: boolean; questionEditId: string; questionText: string; setQuestionText: (value: string) => void; questionExplanation: string; setQuestionExplanation: (value: string) => void; optionTexts: string[]; setOptionTexts: (value: string[]) => void; correctOption: number; setCorrectOption: (value: number) => void; onSubmit: (event: FormEvent<HTMLFormElement>) => void; onEdit: (id: string) => void; onRemove: (id: string) => void; onCancel: () => void;
}) {
  const canEdit = selected.status === "draft";
  return <section className="mt-8 border-t border-slate-200 pt-6"><h3 className="text-xl font-semibold">Test questions</h3>{selected.questions?.length ? <ol className="mt-4 space-y-3">{selected.questions.map((question, index) => <li key={question.id} className="rounded-xl border border-slate-200 p-4"><div className="flex flex-wrap items-start justify-between gap-3"><div><p className="font-semibold">{index + 1}. {question.text}</p><ul className="mt-2 space-y-1 text-sm text-slate-600">{question.options.map(option => <li key={option.id}>{option.is_correct ? "✓ " : ""}{option.text}</li>)}</ul>{question.explanation && <p className="mt-2 text-sm text-slate-500">Explanation: {question.explanation}</p>}</div>{canEdit && <div className="flex gap-3"><button type="button" onClick={() => onEdit(question.id)} className="text-sm font-semibold text-[#145b48] underline">Edit</button><button type="button" onClick={() => onRemove(question.id)} className="text-sm font-semibold text-red-700 underline">Remove</button></div>}</div></li>)}</ol> : <p className="mt-3 rounded-xl bg-[#f7f8f4] p-4 text-sm text-slate-600">Add at least one question before publishing this test.</p>}
    {canEdit && <form onSubmit={onSubmit} className="mt-5 space-y-4 rounded-xl bg-[#f7f8f4] p-4 sm:p-5"><h4 className="font-semibold">{questionEditId ? "Edit question" : "Add a question"}</h4><label className="block text-sm font-medium">Question<textarea required minLength={1} value={questionText} onChange={event => setQuestionText(event.target.value)} className={inputClass} /></label><label className="block text-sm font-medium">Explanation<textarea value={questionExplanation} onChange={event => setQuestionExplanation(event.target.value)} className={inputClass} /></label><fieldset><legend className="text-sm font-semibold">Options — select the correct answer</legend><div className="mt-2 space-y-2">{optionTexts.map((value, index) => <div key={index} className="flex items-center gap-2"><input aria-label={`Option ${index + 1}`} required={index < 2} value={value} onChange={event => setOptionTexts(optionTexts.map((item, i) => i === index ? event.target.value : item))} className={inputClass} /><input type="radio" name="correct-option" aria-label={`Mark option ${index + 1} correct`} checked={correctOption === index} onChange={() => setCorrectOption(index)} className="h-4 w-4 accent-[#145b48]" /></div>)}</div></fieldset><div className="flex flex-wrap gap-2"><button disabled={saving} className="rounded-lg bg-[#145b48] px-4 py-2 font-semibold text-white">{saving ? "Saving…" : questionEditId ? "Save question" : "Add question"}</button>{questionEditId && <button type="button" onClick={onCancel} className="rounded-lg border px-4 py-2">Cancel edit</button>}</div></form>}
    {!canEdit && <p className="mt-4 text-sm text-slate-500">Published test questions are locked because student attempts may refer to them.</p>}
  </section>;
}

function FieldControl({ field, value, disabled, onChange }: { field: Field; value: string | boolean | undefined; disabled: boolean; onChange: (value: string | boolean) => void }) {
  const id = `content-${field.name}`;
  if (field.kind === "checkbox") return <label htmlFor={id} className="flex items-center gap-3 rounded-xl border border-[#d8e1da] p-3 text-sm font-semibold"><input id={id} type="checkbox" checked={Boolean(value)} disabled={disabled} onChange={event => onChange(event.target.checked)} className="h-4 w-4 accent-[#145b48]" />{field.label}</label>;
  const common = { id, name: field.name, required: field.required, maxLength: field.maxLength, min: field.min, max: field.max, disabled, value: String(value ?? ""), onChange: (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => onChange(event.target.value), className: inputClass, "aria-describedby": field.hint ? `${id}-hint` : undefined };
  return <label htmlFor={id} className={`block text-sm font-semibold ${field.kind === "textarea" ? "sm:col-span-2" : ""}`}>{field.label}{field.kind === "textarea" ? <textarea {...common} rows={4} /> : field.kind === "select" ? <select {...common}><option value="">Select…</option>{field.options?.map(option => <option key={option} value={option}>{option.replaceAll("_", " ")}</option>)}</select> : <input {...common} type={field.kind || "text"} />}{field.hint && <span id={`${id}-hint`} className="mt-1 block text-xs font-normal text-slate-500">{field.hint}</span>}</label>;
}

function StatusBadge({ value, verified }: { value: string; verified?: boolean }) {
  return <span className="inline-flex flex-wrap items-center gap-1.5"><span className={`rounded-full px-2.5 py-1 text-xs font-semibold capitalize ${statusClass(value)}`}>{value.replaceAll("_", " ")}</span>{verified && <span className="rounded-full bg-[#e8f2e4] px-2.5 py-1 text-xs font-semibold text-[#315d40]">Verified</span>}</span>;
}

function Pagination({ page, pages, total, onPage }: { page: number; pages: number; total: number; onPage: (page: number) => void }) {
  return <nav aria-label="Content pagination" className="flex flex-wrap items-center justify-center gap-4 text-sm"><button disabled={page <= 1} onClick={() => onPage(page - 1)} className="rounded-lg border bg-white px-4 py-2 disabled:opacity-40">Previous</button><span>Page {page} of {pages} · {total} records</span><button disabled={page >= pages} onClick={() => onPage(page + 1)} className="rounded-lg border bg-white px-4 py-2 disabled:opacity-40">Next</button></nav>;
}

function Feedback({ tone, message, retry }: { tone: "error" | "success"; message: string; retry?: () => void }) {
  return <div role={tone === "error" ? "alert" : "status"} className={`rounded-xl border p-3 text-sm ${tone === "error" ? "border-red-200 bg-red-50 text-red-800" : "border-[#d7e6d4] bg-[#eef4e8] text-[#28483b]"}`}><span>{message}</span>{retry && <button onClick={retry} className="ml-3 font-semibold underline">Retry</button>}</div>;
}

function defaultForm(kind: AdminContentKind): Record<string, string | boolean> {
  return Object.fromEntries(fields[kind].map(field => [field.name, field.kind === "checkbox" ? false : field.name === "duration_minutes" ? "30" : ""]));
}

function toForm(kind: AdminContentKind, item: ContentRow): Record<string, string | boolean> {
  return Object.fromEntries(fields[kind].map(field => {
    const value = item[field.name];
    if (field.kind === "checkbox") return [field.name, Boolean(value)];
    if (field.name === "skills") return [field.name, Array.isArray(value) ? value.join(", ") : ""];
    if (field.kind === "date" && typeof value === "string") return [field.name, value.slice(0, 10)];
    return [field.name, value === null || value === undefined ? "" : String(value)];
  }));
}
