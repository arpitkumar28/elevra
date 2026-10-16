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
            ["Exams returned (max 20)", exams.length],
            ["Opportunities returned (max 20)", opps.length],
            [
              "Unverified records in loaded public sample",
              [...exams, ...opps].filter((x) => !x.verified).length,
            ],
            ["Loaded items with deadlines", opps.filter((o) => o.deadline).length],
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
        <p className="text-slate-600">
          The current API only exposes published exam and opportunity listings. It has no
          administrator queue endpoint for drafts or pending review, so this page cannot report
          review work yet.
        </p>
      </Panel>
    );
  if (route !== "exams" && route !== "opportunities")
    return (
      <Panel title={`${nice(route)} is unavailable`}>
        <p className="text-slate-600">
          This section does not have a connected API view in the current admin application.
        </p>
      </Panel>
    );
  const records = route === "exams" ? exams : opps;
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
          className="rounded-xl bg-[#145b48] px-4 py-2 font-bold text-white opacity-60"
        >
          Create {label}
        </button>
      </div>
      <Panel title={`${nice(route)} returned by API`}>
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
                    <td>{x.status}</td>
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
