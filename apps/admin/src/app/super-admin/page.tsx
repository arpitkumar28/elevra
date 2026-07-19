import { KeyRound, LockKeyhole, ShieldCheck, Users } from "lucide-react";

const controls = [
  {
    icon: Users,
    name: "Tenant governance",
    description: "Organizations, ownership, and data residency policy.",
  },
  {
    icon: ShieldCheck,
    name: "Role matrix",
    description: "RBAC permissions and emergency access review.",
  },
  {
    icon: KeyRound,
    name: "OAuth clients",
    description: "Google login, future Apple login, and public API credentials.",
  },
  {
    icon: LockKeyhole,
    name: "Audit policy",
    description: "Retention, export review, and privileged action monitoring.",
  },
];

export default function SuperAdminPage() {
  return (
    <main className="min-h-screen px-6 py-8">
      <div className="mx-auto max-w-7xl">
        <header className="border-b border-slate-200 pb-6">
          <p className="text-sm font-medium text-teal-700">Super admin</p>
          <h1 className="mt-1 text-3xl font-semibold">Platform governance</h1>
        </header>

        <section className="mt-8 grid gap-4 md:grid-cols-2">
          {controls.map((control) => (
            <article
              className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
              key={control.name}
            >
              <control.icon className="text-teal-700" size={24} />
              <h2 className="mt-4 font-semibold">{control.name}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">{control.description}</p>
            </article>
          ))}
        </section>
      </div>
    </main>
  );
}
