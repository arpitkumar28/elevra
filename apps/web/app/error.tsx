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
        className="mt-6 rounded-xl bg-[#F5C542] px-4 py-2 font-semibold text-[#111827]"
      >
        Try again
      </button>
    </div>
  );
}
