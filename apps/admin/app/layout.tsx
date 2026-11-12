import type { Metadata } from "next";
import "./globals.css";
import { AdminAuth } from "./admin-auth";
import { AdminShell } from "./admin-shell";

export const metadata: Metadata = {
  title: "Elevra Admin",
  description: "Administrative shell",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AdminAuth>
          <AdminShell>{children}</AdminShell>
        </AdminAuth>
      </body>
    </html>
  );
}
