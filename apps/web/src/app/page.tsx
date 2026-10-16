const tiles = [
  { icon: "⌁", title: "Discover", value: "128", label: "matched opportunities" },
  { icon: "✓", title: "Learn", value: "72%", label: "exam readiness" },
  { icon: "▦", title: "Plan", value: "9", label: "upcoming deadlines" },
  { icon: "◉", title: "Alerts", value: "4", label: "priority notifications" },
];

export default function StudentHome() {
  return (
    <main className="min-h-screen px-6 py-8">
      <div className="mx-auto max-w-6xl">
        <header className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 pb-6">
          <div>
            <p className="text-sm font-medium text-[#155b48]">Student workspace</p>
            <h1 className="mt-1 text-3xl font-semibold">Today in Elevra</h1>
          </div>
          <div className="rounded-md border border-slate-200 bg-white px-4 py-2 text-sm text-slate-700">
            AI plan refreshed 12 minutes ago
          </div>
        </header>

        <section className="mt-8 grid gap-4 md:grid-cols-4">
          {tiles.map((tile) => (
            <article
              className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
              key={tile.title}
            >
              <span className="text-2xl text-[#155b48]">{tile.icon}</span>
              <p className="mt-4 text-sm font-medium text-slate-600">{tile.title}</p>
              <p className="mt-2 text-3xl font-semibold">{tile.value}</p>
              <p className="mt-1 text-sm text-slate-500">{tile.label}</p>
            </article>
          ))}
        </section>

        <section className="mt-6 rounded-lg border border-slate-200 bg-white p-6">
          <h2 className="text-xl font-semibold">Recommended next action</h2>
          <p className="mt-2 max-w-3xl text-slate-600">
            Complete the machine learning scholarship essay draft, then run the AI reviewer before
            the deadline enters the high-priority window.
          </p>
        </section>
      </div>
    </main>
  );
}
