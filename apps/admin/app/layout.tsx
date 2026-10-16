import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import { AdminAuth } from "./admin-auth";

export const metadata: Metadata = {
  title: "Elevra Admin",
  description: "Administrative shell",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AdminAuth>
          <div className="min-h-screen bg-[#f5f7f3] text-[#14231f] lg:flex">
            <aside className="border-b border-[#dfe7df] bg-white px-5 py-4 lg:fixed lg:inset-y-0 lg:left-0 lg:w-64 lg:border-b-0 lg:border-r lg:p-6">
              <Link href="/dashboard" className="flex items-center gap-3 text-lg font-bold">
                <span className="grid h-9 w-9 place-items-center rounded-xl bg-[#145b48] font-black text-[#d4edaa]">
                  e
                </span>
                Elevra <span className="text-xs font-medium text-slate-400">Admin</span>
              </Link>
              <nav
                aria-label="Admin navigation"
                className="mt-5 flex gap-2 overflow-x-auto pb-1 text-sm lg:mt-10 lg:flex-col lg:gap-1"
              >
                {[
                  ["Overview", "/dashboard"],
                  ["Opportunities", "/opportunities"],
                  ["Exams", "/exams"],
                ["Draft & review queue", "/queue"],
                ["Courses", "/courses"],
                ["Current affairs", "/current-affairs"],
                ["Practice tests", "/tests"],
                ].map(([label, href]) => (
                  <Link
                    key={href}
                    href={href}
                    className="shrink-0 rounded-lg px-3 py-2.5 font-medium text-slate-600 transition hover:bg-[#eef4e8] hover:text-[#145b48]"
                  >
                    {label}
                  </Link>
                ))}
              </nav>
              <p className="mt-8 hidden rounded-xl bg-[#f5f7f3] p-4 text-xs leading-5 text-slate-500 lg:block">
                Content actions require an authenticated administrator session.
              </p>
            </aside>
            <main className="min-h-screen flex-1 p-5 sm:p-8 lg:ml-64">{children}</main>
          </div>
        </AdminAuth>
      </body>
    </html>
  );
}
