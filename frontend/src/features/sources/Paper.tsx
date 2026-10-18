"use client";

import type { ReactNode } from "react";

export function Paper({ label, children }: { label?: string; children: ReactNode }) {
  return (
    <section className="scroll-mt-4">
      {label && <h3 className="mb-2 px-1 text-xs font-medium text-ink-muted">{label}</h3>}
      <div className="rounded-xl border border-line bg-surface px-6 py-6 shadow-xs sm:px-10 sm:py-9">
        {children}
      </div>
    </section>
  );
}
