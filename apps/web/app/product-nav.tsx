"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  ["Exams", "/exams"],
  ["Jobs", "/jobs"],
  ["Internships", "/internships"],
  ["Scholarships", "/scholarships"],
  ["Courses", "/courses"],
  ["Competitions", "/competitions"],
  ["Current Affairs", "/current-affairs"],
  ["Tests", "/tests"],
];

export function ProductNav() {
  const pathname = usePathname();
  return (
    <>
      <nav
        className="hidden items-center gap-5 text-sm font-medium text-slate-600 lg:flex"
        aria-label="Primary navigation"
      >
        {links.map(([label, href]) => (
          <Link
            key={href}
            href={href as "/exams"}
            className={
              pathname === href || pathname.startsWith(`${href}/`)
                ? "border-b-2 border-[#145b48] py-5 text-[#145b48]"
                : "py-5 transition hover:text-[#145b48]"
            }
          >
            {label}
          </Link>
        ))}
      </nav>
      <nav
        className="fixed inset-x-0 bottom-0 z-40 flex justify-around border-t border-[#e3e9e4] bg-white px-2 py-2 text-[11px] font-semibold md:hidden"
        aria-label="Mobile navigation"
      >
        {[
          ["Home", "/", "⌂"],
          ["Explore", "/explore", "⌕"],
          ["Career", "/career", "↗"],
          ["Tests", "/tests", "▦"],
          ["Profile", "/profile", "◉"],
        ].map(([label, href, icon]) => (
          <Link
            key={href}
            href={href as "/"}
            className={`grid place-items-center gap-0.5 px-2 ${pathname === href ? "text-[#d99400]" : "text-slate-500"}`}
          >
            <span className="text-base">{icon}</span>
            {label}
          </Link>
        ))}
      </nav>
    </>
  );
}
