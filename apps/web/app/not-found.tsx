import Link from "next/link";

export default function NotFound() {
  return (
    <main className="mx-auto max-w-4xl px-6 py-20 text-center">
      <h1 className="text-4xl font-semibold">Page not found</h1>
      <p className="mt-4 text-slate-600">
        The requested page is not available yet in this foundation release.
      </p>
      <Link
        href="/"
        className="mt-6 inline-flex rounded-xl bg-[#F5C542] px-4 py-2 font-semibold text-[#111827]"
      >
        Back to home
      </Link>
    </main>
  );
}
