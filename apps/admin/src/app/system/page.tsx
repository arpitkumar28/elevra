import { Activity, Bell, Bot, Database, Server } from "lucide-react";

const services = [
  { icon: Server, name: "Backend API", status: "healthy", p95: "142 ms" },
  { icon: Bot, name: "AI Engine", status: "healthy", p95: "680 ms" },
  { icon: Database, name: "Search", status: "healthy", p95: "38 ms" },
  { icon: Activity, name: "Crawler", status: "degraded", p95: "1.8 s" },
  { icon: Bell, name: "Notifications", status: "healthy", p95: "210 ms" },
];

export default function SystemHealthPage() {
  return (
    <main className="min-h-screen px-6 py-8">
      <div className="mx-auto max-w-7xl">
        <header className="border-b border-slate-200 pb-6">
          <p className="text-sm font-medium text-teal-700">System health</p>
          <h1 className="mt-1 text-3xl font-semibold">Operational telemetry</h1>
        </header>

        <section className="mt-8 grid gap-4 md:grid-cols-2">
          {services.map((service) => (
            <article
              className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
              key={service.name}
            >
              <service.icon className="text-teal-700" size={24} />
              <div className="mt-4 flex items-center justify-between gap-4">
                <div>
                  <h2 className="font-semibold">{service.name}</h2>
                  <p className="text-sm text-slate-600">{service.status}</p>
                </div>
                <p className="text-sm font-medium">p95 {service.p95}</p>
              </div>
            </article>
          ))}
        </section>
      </div>
    </main>
  );
}
