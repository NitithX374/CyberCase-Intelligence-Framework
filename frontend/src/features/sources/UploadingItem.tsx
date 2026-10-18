"use client";

import { Icon } from "@/components/icons";

export function UploadingItem({ filename }: { filename?: string | null }) {
  return (
    <div
      aria-live="polite"
      className="mx-0.5 flex items-start gap-2.5 rounded-lg border border-dashed border-line-strong bg-surface px-2.5 py-2"
    >
      <Icon name="spinner" className="mt-0.5 h-4 w-4 shrink-0 text-ink-muted" />
      <span className="min-w-0 flex-1">
        <span className="block truncate text-[13px] font-medium text-ink">
          {filename || "Uploading file…"}
        </span>
        <span className="mt-0.5 block text-xs text-ink-muted">Extracting text…</span>
      </span>
    </div>
  );
}
