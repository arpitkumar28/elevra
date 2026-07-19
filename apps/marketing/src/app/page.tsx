import { ArrowRight, GraduationCap, Search, Sparkles } from "lucide-react";

import { Button } from "@elevra/ui";

const features = [
  {
    icon: Search,
    label: "Opportunity discovery",
    copy: "Scholarships, internships, exams, and competitions in one graph.",
  },
  {
    icon: Sparkles,
    label: "AI learning copilot",
    copy: "Personal study plans, revision loops, and adaptive explanations.",
  },
  {
    icon: GraduationCap,
    label: "Career operating system",
    copy: "Portfolio, readiness, and applications tracked from school to first role.",
  },
];

export default function MarketingHome() {
  return (
    <main>
      <section className="min-h-[92vh] bg-[linear-gradient(135deg,#eef7f4_0%,#ffffff_48%,#fff5e3_100%)] px-6 py-8">
        <nav className="mx-auto flex max-w-6xl items-center justify-between">
          <span className="text-xl font-semibold">Elevra</span>
          <Button variant="outline">Join waitlist</Button>
        </nav>

        <div className="mx-auto grid max-w-6xl gap-12 py-20 md:grid-cols-[1.05fr_0.95fr] md:items-center">
          <div>
            <p className="mb-4 text-sm font-semibold uppercase tracking-wide text-teal-700">
              AI Student Operating System
            </p>
            <h1 className="max-w-3xl text-5xl font-semibold leading-tight md:text-7xl">Elevra</h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-700">
              A unified platform that helps students discover opportunities, learn smarter, prepare
              for exams, and build successful careers.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button>
                Start building <ArrowRight size={18} />
              </Button>
              <Button variant="ghost">Explore platform</Button>
            </div>
          </div>

          <div className="rounded-lg border border-teal-900/10 bg-white p-5 shadow-sm">
            <div className="grid gap-3">
              {features.map((feature) => (
                <div className="rounded-md border border-slate-200 p-4" key={feature.label}>
                  <feature.icon className="mb-3 text-teal-700" size={24} />
                  <h2 className="text-base font-semibold">{feature.label}</h2>
                  <p className="mt-1 text-sm leading-6 text-slate-600">{feature.copy}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
