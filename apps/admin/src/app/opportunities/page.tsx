import { CheckCircle2, Clock3, Search, ShieldAlert } from "lucide-react";

const queue = [
  {
    title: "Global AI Scholars Program",
    provider: "Elevra Verified Network",
    risk: "low",
    status: "Pending approval",
  },
  {
    title: "International Startup Fellowship",
    provider: "External crawler",
    risk: "medium",
    status: "Needs source review",
  },
];

export default function OpportunityApprovalPage() {
  return (
    <main className="min-h-screen px-6 py-8">
      <div className="mx-auto max-w-7xl">
        <header className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 pb-6">
          <div>
            <p className="text-sm font-medium text-teal-700">Opportunity approval</p>
            <h1 className="mt-1 text-3xl font-semibold">Review queue</h1>
          </div>
          <div className="flex h-10 items-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-600">
            <Search size={18} />
            Search, filter, and triage
          </div>
        </header>

        <section className="mt-8 grid gap-4">
          {queue.map((item) => (
            <article
              className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
              key={item.title}
            >
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <h2 className="text-lg font-semibold">{item.title}</h2>
                  <p className="mt-1 text-sm text-slate-600">{item.provider}</p>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <span className="inline-flex items-center gap-1 text-amber-700">
                    <ShieldAlert size={16} /> {item.risk}
                  </span>
                  <span className="inline-flex items-center gap-1 text-slate-600">
                    <Clock3 size={16} /> {item.status}
                  </span>
                  <span className="inline-flex items-center gap-1 text-teal-700">
                    <CheckCircle2 size={16} /> approve
                  </span>
                </div>
              </div>
            </article>
          ))}
        </section>
      </div>
    </main>
  );
}
