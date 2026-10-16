import Link from "next/link";
import {
  ArrowDownRight,
  ArrowRight,
  BookOpenCheck,
  BriefcaseBusiness,
  GraduationCap,
  Search,
  Sparkles,
} from "lucide-react";

const features = [
  {
    icon: Search,
    number: "01",
    label: "Find your options",
    title: "See the paths open to you.",
    copy: "Explore exams, scholarships, internships, and competitions in one calm workspace.",
  },
  {
    icon: BookOpenCheck,
    number: "02",
    label: "Prepare with purpose",
    title: "Turn information into progress.",
    copy: "Keep the details that matter close: requirements, dates, learning resources, and practice.",
  },
  {
    icon: BriefcaseBusiness,
    number: "03",
    label: "Move forward",
    title: "Make your next step yours.",
    copy: "Save opportunities and keep your plans organised as your goals take shape.",
  },
];

const productUrl = "https://elevra.app";

export default function MarketingHome() {
  return (
    <main className="overflow-hidden">
      <header className="relative z-10 mx-auto flex max-w-7xl items-center justify-between px-5 py-5 sm:px-8 lg:py-7">
        <Link href="/" className="flex items-center gap-3" aria-label="Elevra home">
          <span className="grid h-10 w-10 place-items-center rounded-2xl bg-[#155b48] text-lg font-black text-[#dce9d1] shadow-sm">
            e
          </span>
          <span className="text-xl font-bold tracking-[-.04em]">Elevra</span>
        </Link>
        <nav className="flex items-center gap-3" aria-label="Main navigation">
          <a
            href={`${productUrl}/login`}
            className="hidden rounded-xl px-4 py-2.5 text-sm font-semibold text-[#42634e] transition hover:bg-white sm:inline-flex"
          >
            Log in
          </a>
          <a
            href={`${productUrl}/register`}
            className="inline-flex items-center gap-2 rounded-xl bg-[#155b48] px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-[#104537]"
          >
            Get started <ArrowRight size={16} aria-hidden="true" />
          </a>
        </nav>
      </header>

      <section className="relative mx-auto grid max-w-7xl gap-12 px-5 pb-20 pt-10 sm:px-8 sm:pt-16 lg:grid-cols-[1.05fr_.95fr] lg:items-center lg:gap-16 lg:pb-28 lg:pt-14">
        <div className="relative z-[1]">
          <p className="inline-flex items-center gap-2 rounded-full border border-[#dce7d8] bg-white/75 px-3.5 py-2 text-xs font-bold uppercase tracking-[.13em] text-[#42634e] shadow-sm">
            <Sparkles size={14} aria-hidden="true" /> A clearer way forward
          </p>
          <h1 className="mt-7 max-w-3xl text-[3.25rem] font-semibold leading-[.99] tracking-[-.065em] text-[#17251f] sm:text-6xl lg:text-[5.35rem]">
            Your next chapter, <span className="text-[#668b59]">within reach.</span>
          </h1>
          <p className="mt-7 max-w-xl text-base leading-8 text-[#64736b] sm:text-lg">
            Find trusted opportunities, make sense of exam information, and plan your next move—all
            in one place built for the journey ahead.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <a
              href={`${productUrl}/explore`}
              className="inline-flex items-center gap-2 rounded-xl bg-[#155b48] px-5 py-3.5 text-sm font-semibold text-white shadow-[0_10px_24px_rgba(21,91,72,.18)] transition hover:-translate-y-0.5 hover:bg-[#104537]"
            >
              Explore Elevra <ArrowRight size={17} aria-hidden="true" />
            </a>
            <a
              href="#how-it-helps"
              className="inline-flex items-center gap-2 rounded-xl border border-[#d8e1d8] bg-white/70 px-5 py-3.5 text-sm font-semibold text-[#28483b] transition hover:border-[#b7c9b8] hover:bg-white"
            >
              How it helps <ArrowDownRight size={17} aria-hidden="true" />
            </a>
          </div>
          <div className="mt-9 flex flex-wrap gap-x-6 gap-y-2 text-xs font-medium text-[#6e7b73] sm:text-sm">
            <span className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-[#83a873]" /> Clear, organised
              information
            </span>
            <span className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-[#83a873]" /> Your goals, your pace
            </span>
          </div>
        </div>

        <div className="relative mx-auto w-full max-w-[570px]">
          <div className="absolute -right-16 -top-16 h-64 w-64 rounded-full bg-[#e0ecd6] blur-3xl" />
          <div className="absolute -bottom-16 -left-12 h-64 w-64 rounded-full bg-[#d5e3d0] blur-3xl" />
          <div className="relative rounded-[2rem] border border-white/80 bg-[#eaf0e6] p-3 shadow-[0_35px_90px_rgba(31,62,44,.13)] sm:p-5">
            <div className="overflow-hidden rounded-[1.5rem] border border-[#e4eae1] bg-white">
              <div className="flex items-center justify-between border-b border-[#edf0ec] px-5 py-4 sm:px-6">
                <div className="flex items-center gap-2.5">
                  <span className="grid h-8 w-8 place-items-center rounded-xl bg-[#155b48] text-sm font-black text-[#dce9d1]">
                    e
                  </span>
                  <span className="text-sm font-bold tracking-tight">Your next steps</span>
                </div>
                <span className="rounded-full bg-[#eef4e8] px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-[#42634e]">
                  Made for you
                </span>
              </div>
              <div className="p-5 sm:p-6">
                <p className="text-xs font-semibold uppercase tracking-[.15em] text-[#7b8d7e]">
                  A little more clarity
                </p>
                <h2 className="mt-2 max-w-sm text-2xl font-semibold leading-tight tracking-[-.04em] text-[#17251f] sm:text-3xl">
                  Bring your possibilities into focus.
                </h2>
                <div className="mt-6 space-y-3">
                  {[
                    {
                      icon: GraduationCap,
                      title: "Exams & preparation",
                      copy: "Dates, eligibility, and official details",
                      tint: "bg-[#edf3e8] text-[#42634e]",
                    },
                    {
                      icon: Search,
                      title: "Opportunities",
                      copy: "Scholarships, work, and more",
                      tint: "bg-[#f1f4e9] text-[#61784d]",
                    },
                    {
                      icon: BookOpenCheck,
                      title: "Learning & practice",
                      copy: "Resources for the road ahead",
                      tint: "bg-[#eaf2ed] text-[#3d6a59]",
                    },
                  ].map(({ icon: Icon, title, copy, tint }) => (
                    <div
                      key={title}
                      className="flex items-center gap-3.5 rounded-2xl border border-[#edf0ec] p-3.5 transition hover:border-[#d5e1d3] hover:bg-[#fbfcfa] sm:p-4"
                    >
                      <span
                        className={`grid h-11 w-11 shrink-0 place-items-center rounded-xl ${tint}`}
                      >
                        <Icon size={20} aria-hidden="true" />
                      </span>
                      <span className="min-w-0">
                        <span className="block text-sm font-semibold text-[#263a30]">{title}</span>
                        <span className="mt-1 block text-xs text-[#77837b]">{copy}</span>
                      </span>
                      <ArrowRight
                        className="ml-auto shrink-0 text-[#91a294]"
                        size={16}
                        aria-hidden="true"
                      />
                    </div>
                  ))}
                </div>
                <a
                  href={`${productUrl}/explore`}
                  className="mt-5 flex items-center justify-between rounded-xl bg-[#155b48] px-4 py-3.5 text-sm font-semibold text-white transition hover:bg-[#104537]"
                >
                  Start exploring <ArrowRight size={17} aria-hidden="true" />
                </a>
              </div>
            </div>
            <div className="absolute -bottom-5 -left-4 hidden items-center gap-3 rounded-2xl border border-white/80 bg-white/95 px-4 py-3 shadow-lg sm:flex">
              <span className="grid h-9 w-9 place-items-center rounded-xl bg-[#dce9d1] text-[#315d40]">
                <Sparkles size={18} aria-hidden="true" />
              </span>
              <span>
                <span className="block text-xs font-bold text-[#263a30]">One step at a time</span>
                <span className="mt-0.5 block text-[11px] text-[#77837b]">
                  Your path can take shape here
                </span>
              </span>
            </div>
          </div>
        </div>
      </section>

      <section id="how-it-helps" className="border-y border-[#e1e8e1] bg-white/80 py-20 sm:py-24">
        <div className="mx-auto max-w-7xl px-5 sm:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-xs font-bold uppercase tracking-[.17em] text-[#668b59]">
              A steady companion
            </p>
            <h2 className="mt-4 text-3xl font-semibold tracking-[-.045em] text-[#17251f] sm:text-5xl">
              Less scattered. More possible.
            </h2>
            <p className="mt-4 leading-7 text-[#64736b]">
              Keep discovery, preparation, and planning connected as you work toward what comes
              next.
            </p>
          </div>
          <div className="mt-12 grid gap-4 md:grid-cols-3">
            {features.map(({ icon: Icon, number, label, title, copy }) => (
              <article
                key={number}
                className="group rounded-[1.5rem] border border-[#e1e8e1] bg-[#fbfcfa] p-6 transition duration-200 hover:-translate-y-1 hover:border-[#c5d5c0] hover:bg-white hover:shadow-[0_18px_42px_rgba(25,54,39,.08)] sm:p-7"
              >
                <div className="flex items-center justify-between">
                  <span className="grid h-12 w-12 place-items-center rounded-2xl bg-[#eaf1e5] text-[#42634e] transition group-hover:bg-[#dce9d1]">
                    <Icon size={22} aria-hidden="true" />
                  </span>
                  <span className="text-xs font-bold tracking-[.14em] text-[#91a294]">
                    {number}
                  </span>
                </div>
                <p className="mt-8 text-xs font-bold uppercase tracking-[.14em] text-[#668b59]">
                  {label}
                </p>
                <h3 className="mt-2 text-xl font-semibold tracking-[-.025em] text-[#20352a]">
                  {title}
                </h3>
                <p className="mt-3 text-sm leading-6 text-[#64736b]">{copy}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-16 sm:px-8 sm:py-20">
        <div className="relative overflow-hidden rounded-[2rem] bg-[#155b48] px-6 py-10 text-white sm:px-12 sm:py-14">
          <div className="absolute -right-10 -top-28 h-72 w-72 rounded-full border-[48px] border-white/[.06]" />
          <div className="absolute -bottom-40 right-1/4 h-72 w-72 rounded-full bg-[#dce9d1]/10 blur-2xl" />
          <div className="relative flex flex-col items-start justify-between gap-8 sm:flex-row sm:items-center">
            <div>
              <p className="text-xs font-bold uppercase tracking-[.16em] text-[#dce9d1]">
                Begin wherever you are
              </p>
              <h2 className="mt-3 max-w-2xl text-3xl font-semibold tracking-[-.04em] sm:text-4xl">
                Your next chapter starts with one small step.
              </h2>
              <p className="mt-3 max-w-xl text-sm leading-6 text-white/75">
                Explore what is available and find the information that helps you move forward.
              </p>
            </div>
            <a
              href={`${productUrl}/explore`}
              className="inline-flex shrink-0 items-center gap-2 rounded-xl bg-[#dce9d1] px-5 py-3.5 text-sm font-bold text-[#173b2f] transition hover:bg-[#c9ddb9]"
            >
              Explore Elevra <ArrowRight size={17} aria-hidden="true" />
            </a>
          </div>
        </div>
      </section>

      <footer className="border-t border-[#e1e8e1] bg-white/70 px-5 py-7 text-sm text-[#77837b] sm:px-8">
        <div className="mx-auto flex max-w-7xl flex-col justify-between gap-3 sm:flex-row sm:items-center">
          <span className="font-bold tracking-tight text-[#28483b]">Elevra</span>
          <span>Clearer information for confident next steps.</span>
        </div>
      </footer>
    </main>
  );
}
