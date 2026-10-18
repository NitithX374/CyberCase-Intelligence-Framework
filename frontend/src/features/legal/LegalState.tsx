"use client";

import { EmptyState } from "@/components/EmptyState";

export function LegalState({ title, description }: { title: string; description: string }) {
  return (
    <section
      id="workspace-legal-panel"
      aria-label="Legal references"
      className="flex shrink-0 flex-col bg-surface"
    >
      <EmptyState
        title={title}
        description={description}
        className="mx-auto min-h-[420px] w-full max-w-[52rem] justify-center px-5 py-16 sm:px-8"
      />
    </section>
  );
}
