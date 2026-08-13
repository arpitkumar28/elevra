import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Elevra",
  description: "Your Career & Exam Companion",
  keywords: ["exams", "careers", "scholarships", "study plans"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen bg-[#FFFCF2] text-[#111827]">
          <header className="border-b border-slate-200 bg-white/90 backdrop-blur">
            <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
              <Link
                href="/"
                className="text-xl font-semibold tracking-wide text-[#111827]"
              >
                ELEVRA
              </Link>
              <nav className="flex gap-4 text-sm font-medium text-slate-600">
                <Link href="/exams">Exams</Link>
                <Link href="/opportunities">Opportunities</Link>
                <Link href="/career">Career</Link>
                <Link href="/login">Login</Link>
              </nav>
            </div>
          </header>
          {children}
        </div>
      </body>
    </html>
  );
}
