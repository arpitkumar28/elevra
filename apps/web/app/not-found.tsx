import Link from "next/link";

export default function NotFound() {
  return (
    <main className="mx-auto max-w-4xl px-6 py-20 text-center">
      <h1 className="text-4xl font-semibold">Page not found</h1>
      <p className="mt-4 text-[#63736c]">We couldn’t find the page you’re looking for.</p>
      <Link
        href="/"
        className="mt-6 inline-flex rounded-xl bg-[#155b48] px-4 py-2 font-semibold text-white transition hover:bg-[#104537]"
      >
        Back to home
      </Link>
    </main>
  );
}
