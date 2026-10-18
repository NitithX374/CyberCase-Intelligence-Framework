"use client";

import type { ReactNode } from "react";

export function ViewportMessage({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="flex h-full min-h-[24rem] flex-col items-center justify-center p-8 text-center">
      <p className="text-sm text-ink-muted">{title}</p>
      {children}
    </div>
  );
}
