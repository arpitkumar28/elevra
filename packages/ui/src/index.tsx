import * as React from "react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
}

export function Button({
  className = "",
  variant = "primary",
  ...props
}: ButtonProps) {
  const base =
    "inline-flex items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold transition";
  const styles =
    variant === "primary"
      ? "bg-[#F5C542] text-[#111827] hover:bg-[#FFD966]"
      : "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50";
  return (
    <button className={`${base} ${styles} ${className}`.trim()} {...props} />
  );
}

export function Card({
  className = "",
  children,
}: React.PropsWithChildren<{ className?: string }>) {
  return (
    <div
      className={`rounded-2xl border border-slate-200 bg-white p-6 shadow-sm ${className}`.trim()}
    >
      {children}
    </div>
  );
}

export function Badge({
  className = "",
  children,
}: React.PropsWithChildren<{ className?: string }>) {
  return (
    <span
      className={`inline-flex rounded-full bg-[#FFFCF2] px-3 py-1 text-sm font-medium text-[#111827] ${className}`.trim()}
    >
      {children}
    </span>
  );
}

export function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-[#F5C542] focus:ring-2 focus:ring-[#FFD966]"
      {...props}
    />
  );
}
