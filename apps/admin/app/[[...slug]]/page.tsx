"use client";
import { useEffect, useState } from "react";
import { createApiClient, ApiError, type Exam, type Opportunity } from "@elevra/api-client";
const apiClient = createApiClient({
  baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1",
});
const nice = (v: string) => v.replace(/_/g, " ").replace(/\b\w/g, (x) => x.toUpperCase());
const Panel = ({ title, children }: { title: string; children: React.ReactNode }) => (
  <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
    <h2 className="text-lg font-bold">{title}</h2>
    <div className="mt-4">{children}</div>
  </section>
);
export default function AdminPage({ params }: { params: { slug?: string[] } }) {
  const route = params.slug?.[0] || "dashboard",
    [exams, setExams] = useState<Exam[]>([]),
    [opps, setOpps] = useState<Opportunity[]>([]),
    [error, setError] = useState("");
  useEffect(() => {
    Promise.all([
      apiClient.listExams({ page_size: 20 }),
      apiClient.listOpportunities({ page_size: 20 }),
    ])
      .then(([e, o]) => {
        setExams(e.items);
        setOpps(o.items);
      })
      .catch((e: ApiError) => setError(e.message));
  }, []);
  const pending = [...exams, ...opps].filter((x) => !x.verified);
  if (error)
    return (
      <Panel title="Connection issue">
        <p className="text-slate-600">{error}</p>
        <p className="mt-2 text-sm">
          Admin mutations use the existing authenticated API and require an administrator session.
        </p>
      </Panel>
    );
  if (route === "dashboard")
    return (
      <div className="space-y-6">
        <div>
          <p className="text-sm font-semibold text-amber-700">OPERATIONS</p>
          <h1 className="mt-1 text-3xl font-bold">Platform dashboard</h1>
        </div>
        <div className="grid gap-4 md:grid-cols-4">
          {[
            ["Published exams", exams.length],
            ["Published opportunities", opps.length],
            ["Pending verification", pending.length],
            ["Upcoming deadlines", opps.filter((o) => o.deadline).length],
          ].map(([label, n]) => (
            <Panel key={String(label)} title={String(label)}>
              <p className="text-3xl font-bold">{n}</p>
            </Panel>
          ))}
        </div>
        <Panel title="Recent activity">
          <p className="text-slate-600">
            Published content is supplied by the live API. Verification and publication remain
            authorization-protected backend actions.
          </p>
        </Panel>
      </div>
    );
  if (route === "verification")
    return (
      <Panel title="Verification queue">
        {pending.length ? (
          <div className="space-y-3">
            {pending.map((x) => (
              <div className="rounded-xl border p-4" key={x.id}>
                <b>{"name" in x ? x.name : x.title}</b>
                <p className="mt-1 text-sm text-slate-600">
                  Status: New · Source verification required
                </p>
                <p className="text-xs text-slate-500">
                  Verification actions require the existing authenticated admin API.
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-slate-600">No published items currently require verification.</p>
        )}
      </Panel>
    );
  const records = route === "exams" ? exams : route === "opportunities" ? opps : [];
  const label = route === "exams" ? "Exam" : "Opportunity";
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-amber-700">CONTENT OPERATIONS</p>
          <h1 className="text-3xl font-bold">{nice(route)}</h1>
        </div>
        <button
          disabled
          title="Requires authenticated admin session"
          className="rounded-xl bg-[#F5C542] px-4 py-2 font-bold text-slate-900 opacity-70"
        >
          Create {label}
        </button>
      </div>
      <Panel title={`Published ${nice(route)}`}>
        {records.length ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b text-slate-500">
                <tr>
                  <th className="pb-3">Name</th>
                  <th className="pb-3">Status</th>
                  <th className="pb-3">Verification</th>
                  <th className="pb-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {records.map((x) => (
                  <tr className="border-b" key={x.id}>
                    <td className="py-4 font-medium">{"name" in x ? x.name : x.title}</td>
                    <td>Published</td>
                    <td>{x.verified ? "Verified" : "New"}</td>
                    <td>
                      <button
                        disabled
                        className="text-slate-400"
                        title="Requires authenticated admin session"
                      >
                        Edit · Publish · Archive
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-slate-600">No published records returned by the API.</p>
        )}
      </Panel>
    </div>
  );
}
