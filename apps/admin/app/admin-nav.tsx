"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BookOpenCheck,
  BriefcaseBusiness,
  ClipboardList,
  GraduationCap,
  LayoutDashboard,
  Newspaper,
  ShieldCheck,
} from "lucide-react";

const items = [
  { label: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { label: "Opportunities", href: "/opportunities", icon: BriefcaseBusiness },
  { label: "Exams", href: "/exams", icon: GraduationCap },
  { label: "Draft & review queue", href: "/queue", icon: ClipboardList },
  { label: "Courses", href: "/courses", icon: BookOpenCheck },
  { label: "Current affairs", href: "/current-affairs", icon: Newspaper },
  { label: "Practice tests", href: "/tests", icon: ShieldCheck },
];

export function AdminNav() {
  const pathname = usePathname();

  return (
    <nav
      aria-label="Admin navigation"
      className="-mx-1 mt-5 flex gap-2 overflow-x-auto px-1 pb-1 text-sm lg:mx-0 lg:mt-10 lg:flex-col lg:gap-1.5 lg:px-0"
    >
      {items.map(({ label, href, icon: Icon }) => {
        const active = pathname === href || pathname.startsWith(`${href}/`);
        return (
          <Link
            key={href}
            href={href}
            aria-current={active ? "page" : undefined}
            className={`flex shrink-0 items-center gap-3 rounded-xl px-3 py-2.5 font-medium transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#86a875] ${
              active
                ? "bg-[#eaf1e5] text-[#155b48]"
                : "text-slate-600 hover:bg-[#f5f8f2] hover:text-[#155b48]"
            }`}
          >
            <Icon size={17} strokeWidth={1.8} aria-hidden="true" />
            {label}
          </Link>
        );
      })}
    </nav>
  );
}
