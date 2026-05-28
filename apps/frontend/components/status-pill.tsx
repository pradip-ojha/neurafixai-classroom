import type { ReactNode } from "react";

export function StatusPill({
  children,
  tone = "neutral"
}: {
  children: ReactNode;
  tone?: "neutral" | "good" | "warn";
}) {
  const toneClass =
    tone === "good"
      ? "bg-emerald-50 text-emerald-700"
      : tone === "warn"
        ? "bg-amber-50 text-amber-700"
        : "bg-slate-100 text-slate-700";

  return (
    <span className={`inline-flex min-h-6 items-center rounded-full px-2.5 text-xs font-bold ${toneClass}`}>
      {children}
    </span>
  );
}

