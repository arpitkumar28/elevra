import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import { ProductNav } from "./product-nav";

export const metadata: Metadata = {
  title: "Elevra",
  description: "Your Career & Exam Companion",
  keywords: ["exams", "careers", "scholarships", "study plans"],
  metadataBase: new URL("https://elevra.app"),
  openGraph: {
    title: "Elevra — Your Career & Exam Companion",
    description: "Discover verified exams and opportunities.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen bg-[#fffcf5] text-[#182033]">
          <header className="sticky top-0 z-30 border-b border-slate-100 bg-white/90 backdrop-blur">
            <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-5 lg:px-8">
              <Link
                href="/"
                className="flex items-center gap-2 text-lg font-extrabold tracking-tight text-slate-900"
              >
                <span className="grid h-7 w-7 place-items-center rounded-lg bg-[#ffbf13] text-base italic text-white">
                  E
                </span>
                Elevra
              </Link>
              <ProductNav />
              <div className="flex items-center gap-3 text-sm font-semibold">
                <Link
                  href="/login"
                  className="hidden rounded-lg border border-slate-200 px-3.5 py-2 text-slate-700 sm:block"
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  className="rounded-lg bg-[#ffbf13] px-3.5 py-2 text-slate-900 shadow-sm transition hover:bg-[#f6b400]"
                >
                  Get Started
                </Link>
              </div>
            </div>
          </header>
          {children}
          <footer className="mt-10 border-t border-slate-200 bg-white pb-20 pt-10 md:pb-10">
            <div className="mx-auto grid max-w-7xl gap-8 px-5 text-sm text-slate-500 sm:grid-cols-2 lg:grid-cols-4 lg:px-8">
              <div>
                <p className="text-lg font-extrabold text-slate-900">Elevra</p>
                <p className="mt-2 leading-6">
                  Your Career &amp; Exam Companion. Clear information for confident next steps.
                </p>
              </div>
              <div>
                <p className="font-bold text-slate-800">Discover</p>
                <p className="mt-2">
                  <Link href="/exams">Exams</Link> · <Link href="/explore">Opportunities</Link>
                </p>
              </div>
              <div>
                <p className="font-bold text-slate-800">Account</p>
                <p className="mt-2">
                  <Link href="/dashboard">Dashboard</Link> · <Link href="/profile">Profile</Link>
                </p>
              </div>
              <div>
                <p className="font-bold text-slate-800">Trust</p>
                <p className="mt-2">Official sources · Verified updates</p>
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
