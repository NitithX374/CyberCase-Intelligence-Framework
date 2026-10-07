"use client";

import type { SourceMessageRef } from "./types";
import { hasThai } from "@/lib/language";

interface SourceCitationChipProps {
  sourceRef: SourceMessageRef;
  sourceKey: string;
  isActive: boolean;
  citationRole?: "supporting" | "conflicting";
  onSelect: (
    sourceRef: SourceMessageRef,
    anchorElement: HTMLElement,
    sourceKey: string,
    citationRole?: "supporting" | "conflicting",
  ) => void;
}

export function SourceCitationChip({
  sourceRef,
  sourceKey,
  isActive,
  citationRole,
  onSelect,
}: SourceCitationChipProps) {
  const passageCount = sourceRef.passages?.length ?? 0;
  const passageLabel = hasThai(sourceRef.exactQuote ?? sourceRef.label) ? "ข้อความ" : "passages";
  const citationText =
    passageCount > 1 ? `${sourceRef.label} · ${passageCount} ${passageLabel}` : sourceRef.label;
  const isConflicting = citationRole === "conflicting";
  const label = isConflicting ? `Conflicts with ${citationText}` : citationText;

  return (
    <button
      type="button"
      aria-label={label}
      aria-expanded={isActive}
      aria-haspopup="dialog"
      title={label}
      onClick={(event) => onSelect(sourceRef, event.currentTarget, sourceKey, citationRole)}
      className={`inline-flex h-6 max-w-full items-center gap-1 rounded-md px-1.5 text-xs font-medium transition-colors ${
        isActive
          ? "bg-ink text-ivory"
          : isConflicting
            ? "bg-surface-nested text-critical hover:bg-line"
            : "bg-surface-nested text-ink-secondary hover:bg-line hover:text-ink"
      }`}
    >
      {isConflicting && <span className="shrink-0">Conflicts</span>}
      <span className="min-w-0 truncate">{citationText}</span>
    </button>
  );
}
