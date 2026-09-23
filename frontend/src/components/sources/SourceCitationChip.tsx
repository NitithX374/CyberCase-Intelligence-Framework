"use client";

import type { SourceMessageRef } from "@/lib/caseOverview/types";
import { formatSourceCitationText } from "@/lib/caseOverview/source";
import { Icon } from "@/components/common/icons";

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

/** A citation, as a small chip that opens the passage it points at. */
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
  const isConflicting = citationRole === "conflicting";
  const label = isConflicting ? `Conflicts with ${citationText}` : citationText;
  const icon = sourceRef.filename
    ? "sources"
    : sourceRef.sourceType === "followup_response"
      ? "reply"
      : "narrative";

  return (
    <button
      type="button"
      aria-label={label}
      aria-expanded={isActive}
      aria-haspopup="dialog"
      title={label}
      onClick={(event) => {
        if (onSelect) {
          onSelect(sourceRef, event.currentTarget, sourceKey, citationRole);
        } else {
          onNavigateToSource?.(sourceRef.id);
        }
      }}
      className={`inline-flex h-6 max-w-full items-center gap-1 rounded-md px-1.5 text-xs font-medium transition-colors ${
        isConflicting
          ? isActive
            ? "bg-critical/15 text-critical"
            : "bg-critical/[0.07] text-critical hover:bg-critical/15"
          : isActive
            ? "bg-ink text-ivory"
            : "bg-surface-nested text-ink-secondary hover:bg-line hover:text-ink"
      }`}
    >
      <Icon name={isConflicting ? "error" : icon} className="h-3.5 w-3.5 shrink-0 opacity-80" />
      {isConflicting && <span className="shrink-0">Conflicts</span>}
      <span className="min-w-0 truncate">{citationText}</span>
    </button>
  );
}
