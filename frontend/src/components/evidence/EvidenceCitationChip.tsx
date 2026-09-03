"use client";

import type { SourceMessageRef } from "@/lib/case-overview";
import { formatEvidenceCitationText } from "@/lib/evidence-citation";

interface EvidenceCitationChipProps {
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

export function EvidenceCitationChip({
  sourceRef,
  sourceKey,
  isActive,
  citationRole,
  onSelect,
  onNavigateToSource,
}: EvidenceCitationChipProps) {
  const citationText = formatEvidenceCitationText(sourceRef);
  const title = sourceRef.filename
    ? `${sourceRef.filename} · ${citationText}`
    : sourceRef.sourceTypeLabel;

  return (
    <button
      type="button"
      aria-label={
        citationRole === "conflicting"
          ? `Conflict · ${citationText}`
          : citationText
      }
      aria-expanded={isActive}
      aria-haspopup="dialog"
      title={title}
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
      {citationRole === "conflicting" && <span>Conflict · </span>}
      <span className="min-w-0 break-words">{citationText}</span>
      <span aria-hidden="true">↗</span>
    </button>
  );
}
