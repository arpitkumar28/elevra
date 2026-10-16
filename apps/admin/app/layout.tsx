import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import "./globals.css";
import { AdminAuth } from "./admin-auth";
import { AdminNav } from "./admin-nav";

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
            <aside className="border-b border-[#dfe7df] bg-white/95 px-5 py-4 shadow-[0_8px_28px_rgba(25,54,39,.035)] backdrop-blur lg:fixed lg:inset-y-0 lg:left-0 lg:w-64 lg:border-b-0 lg:border-r lg:p-6 lg:shadow-none">
              <Link href="/dashboard" className="flex items-center gap-3 text-lg font-bold">
                <Image
                  src="/elevra-logo.png"
                  alt=""
                  width={36}
                  height={36}
                  priority
                  className="h-9 w-9 rounded-xl object-cover"
                />
                Elevra <span className="text-xs font-medium text-slate-400">Admin</span>
              </Link>
              <AdminNav />
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
