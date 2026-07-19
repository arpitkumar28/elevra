import { Activity, Database, ShieldCheck, Users } from "lucide-react";

const metrics = [
  { icon: Users, title: "Students", value: "2.4M", note: "active profiles" },
  { icon: Database, title: "Content graph", value: "18.6M", note: "indexed records" },
  { icon: Activity, title: "Crawler health", value: "99.94%", note: "successful jobs" },
  { icon: ShieldCheck, title: "Risk queue", value: "23", note: "items for review" },
];

export default function AdminHome() {
  return (
    <main className="min-h-screen px-6 py-8">
      <div className="mx-auto max-w-7xl">
        <header className="border-b border-slate-200 pb-6">
          <p className="text-sm font-medium text-teal-700">Admin dashboard</p>
          <h1 className="mt-1 text-3xl font-semibold">Platform operations</h1>
        </header>

        <section className="mt-8 grid gap-4 md:grid-cols-4">
          {metrics.map((metric) => (
            <article
              className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
              key={metric.title}
            >
              <metric.icon className="text-teal-700" size={24} />
              <p className="mt-4 text-sm font-medium text-slate-600">{metric.title}</p>
              <p className="mt-2 text-3xl font-semibold">{metric.value}</p>
              <p className="mt-1 text-sm text-slate-500">{metric.note}</p>
            </article>
          ))}
        </section>

        <section className="mt-6 rounded-lg border border-slate-200 bg-white p-6">
          <h2 className="text-xl font-semibold">Operational focus</h2>
          <p className="mt-2 max-w-3xl text-slate-600">
            Prioritize crawler anomaly review, scholarship taxonomy cleanup, and model evaluation
            for admissions essay feedback before the next release window.
          </p>
        </section>
      </div>
    </main>
  );
}
