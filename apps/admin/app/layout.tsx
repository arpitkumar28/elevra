import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Elevra Admin",
  description: "Administrative shell",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen bg-slate-50">
          <aside className="fixed inset-y-0 left-0 w-64 border-r border-slate-200 bg-white p-6">
            <h1 className="text-xl font-semibold">Elevra Admin</h1>
            <nav className="mt-6 flex flex-col gap-3 text-sm">
              <Link href="/dashboard">Dashboard</Link>
              <Link href="/opportunities">Opportunities</Link>
              <Link href="/exams">Exams</Link>
              <Link href="/users">Users</Link>
              <Link href="/notifications">Notifications</Link>
              <Link href="/content">Content</Link>
              <Link href="/verification">Verification</Link>
              <Link href="/settings">Settings</Link>
            </nav>
          </aside>
          <main className="ml-64 min-h-screen p-8">{children}</main>
        </div>
      </body>
    </html>
  );
}
