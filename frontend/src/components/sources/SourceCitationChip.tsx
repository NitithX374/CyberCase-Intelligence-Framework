"use client";

import type { SourceMessageRef } from "@/lib/caseOverview/types";
import { formatSourceCitationText } from "@/lib/caseOverview/source";

interface SourceCitationChipProps {
  sourceRef: SourceMessageRef;
  sourceKey: string;
  isActive: boolean;
  citationRole?: "supporting" | "conflicting";
  onSelect?: (
    sourceRef: SourceMessageRef,
    anchorElement: HTMLElement,
    sourceKey: string,
    citationRole?: "supporting" | "conflicting",
  ) => void;
  onNavigateToSource?: (messageId: string) => void;
}

export function SourceCitationChip({
  sourceRef,
  sourceKey,
  isActive,
  citationRole,
  onSelect,
  onNavigateToSource,
}: SourceCitationChipProps) {
  // The citation text already names the file, or where the source sits in the
  // case, and the page when there is one. Nothing here needs to add to it.
  const citationText = formatSourceCitationText(sourceRef);
  const label = citationRole === "conflicting" ? `Conflicts with ${citationText}` : citationText;

  return (
    <button
      type="button"
      aria-label={label}
      aria-expanded={isActive}
      aria-haspopup="dialog"
      title={citationText}
      onClick={(event) => {
        if (onSelect) {
          onSelect(sourceRef, event.currentTarget, sourceKey, citationRole);
        } else {
          onNavigateToSource?.(sourceRef.id);
        }
      }}
      className={`inline-flex max-w-full items-center gap-1 rounded-sm py-1 text-[11px] font-medium underline decoration-current/40 underline-offset-4 transition-colors focus-visible:ring-2 focus-visible:ring-primary ${
        isActive
          ? "text-ink decoration-current"
          : citationRole === "conflicting"
            ? "text-unresolved hover:decoration-current"
            : "text-ink-secondary hover:text-ink hover:decoration-current"
      }`}
    >
      <span className="min-w-0 text-left [overflow-wrap:anywhere]">{label}</span>
      <span aria-hidden="true">↗</span>
    </button>
  );
}
