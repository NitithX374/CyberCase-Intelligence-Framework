"use client";

import { formatBytes, formatDate } from "@/lib/format";
import { type RailItem, itemTitle, firstLine } from "./railItems";

export function RailButton({
  item,
  selected,
  onSelect,
}: {
  item: RailItem;
  selected: boolean;
  onSelect: () => void;
}) {
  const detail =
    item.kind === "file"
      ? formatBytes(item.source.size_bytes ?? 0)
      : item.kind === "followup_answer"
        ? firstLine(item.followup.answer)
        : formatDate(item.source.created_at, "day");

  return (
    <button
      type="button"
      aria-pressed={selected}
      onClick={onSelect}
      className={`flex w-full items-start gap-2.5 rounded-lg px-2.5 py-2 text-left transition-colors ${
        selected
          ? "bg-surface text-ink shadow-xs ring-1 ring-line"
          : "text-ink-secondary hover:bg-surface-hover hover:text-ink"
      }`}
    >
      <span className="min-w-0 flex-1">
        <span className="block truncate text-[13px] font-medium">{itemTitle(item)}</span>
        <span className="mt-0.5 block truncate text-xs text-ink-muted">{detail}</span>
      </span>
    </button>
  );
}
