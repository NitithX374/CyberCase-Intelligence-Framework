"use client";

import type { ReactNode } from "react";

export function DetailSection({
  id,
  title,
  count,
  children,
}: {
  id: string;
  title: string;
  count: number;
  children: ReactNode;
}) {
  return (
    <section aria-labelledby={`${id}-heading`} className="min-w-0">
      <h2
        id={`${id}-heading`}
        className="flex items-baseline gap-2 text-base font-semibold text-ink"
      >
        {title} <span className="text-[13px] font-medium text-ink-muted">{count}</span>
      </h2>
      <div className="mt-4">{children}</div>
    </section>
  );
}
