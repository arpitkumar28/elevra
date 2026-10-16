import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import { ProductNav } from "./product-nav";
import { AuthProvider } from "./auth-provider";
import { HeaderAuthControls } from "./auth-components";

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
        <AuthProvider>
          <div className="min-h-screen bg-[#f7f8f4] text-[#14231f]">
            <header className="sticky top-0 z-30 border-b border-[#e3e9e4] bg-[#f7f8f4]/95 backdrop-blur">
              <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-5 lg:px-8">
                <Link
                  href="/"
                  className="flex items-center gap-2 text-lg font-extrabold tracking-tight text-[#14231f]"
                >
                  <span className="grid h-8 w-8 place-items-center rounded-xl bg-[#145b48] text-sm font-black text-[#d4edaa]">
                    e
                  </span>
                  Elevra
                </Link>
                <ProductNav />
                <HeaderAuthControls />
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
        </AuthProvider>
      </body>
    </html>
  );
}
