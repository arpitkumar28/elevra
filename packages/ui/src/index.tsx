import * as React from "react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
}

export function Button({ className = "", variant = "primary", ...props }: ButtonProps) {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition duration-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#86a875] disabled:cursor-not-allowed disabled:opacity-55";
  const styles =
    variant === "primary"
      ? "bg-[#155b48] text-white shadow-sm hover:bg-[#104537]"
      : "border border-[#d8e1d8] bg-white text-[#28483b] hover:border-[#b7c9b8] hover:bg-[#f7faf5]";
  return <button className={`${base} ${styles} ${className}`.trim()} {...props} />;
}

export function Card({
  className = "",
  children,
}: React.PropsWithChildren<{ className?: string }>) {
  return (
    <div
      className={`rounded-2xl border border-[#e1e8e1] bg-white p-6 shadow-[0_12px_34px_rgba(24,49,38,.06)] ${className}`.trim()}
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
      className={`inline-flex rounded-full bg-[#eef4e8] px-3 py-1 text-sm font-semibold text-[#42634e] ${className}`.trim()}
    >
      {children}
    </span>
  );
}

export function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className="w-full rounded-xl border border-[#d8e1da] bg-white px-4 py-3 text-sm text-[#17251f] outline-none transition placeholder:text-[#8a968e] focus:border-[#56816d] focus:ring-2 focus:ring-[#d5e7cf]"
      {...props}
    />
  );
}
