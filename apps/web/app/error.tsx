"use client";

export default function Error({ reset }: { reset: () => void }) {
  return (
    <div className="mx-auto max-w-2xl px-6 py-20 text-center">
      <h2 className="text-2xl font-semibold">Something went wrong</h2>
      <p className="mt-3 text-slate-600">
        The Elevra app encountered an unexpected issue. Please try again.
      </p>
      <button
        onClick={() => reset()}
        className="mt-6 rounded-xl bg-[#155b48] px-4 py-2 font-semibold text-white transition hover:bg-[#104537]"
      >
        Try again
      </button>
    </div>
  );
}
