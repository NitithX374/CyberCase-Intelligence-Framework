"use client";

import { SourceCitationChip } from "@/features/citations/SourceCitationChip";
import { UNCONFIRMED_NOTES } from "@/features/citations/unconfirmed";
import type { ClaimBacked } from "./types";
import { ClaimViewReview } from "./ClaimViewReview";
import type { CaseDetailsProps } from "./CaseDetails";

export function Backing({
  row,
  caseId,
  owner,
  onSelectSource,
  activeSourceKey,
}: {
  row: ClaimBacked;
  caseId?: string;
  owner: string;
  onSelectSource: CaseDetailsProps["onSelectSource"];
  activeSourceKey: string | null;
}) {
  const hasReview = Boolean(row.linkedClaims?.length);
  if (
    !row.inferred &&
    !row.sources.length &&
    !row.unconfirmed.length &&
    !row.supportNote &&
    !hasReview
  ) {
    return null;
  }
  return (
    <div className="mt-2">
      <div className="flex flex-wrap items-center gap-1.5">
        {row.inferred && <span className="text-xs text-ink-muted">Inference</span>}
        {row.unconfirmed.map((status) => (
          <span key={status} className="text-xs text-ink-muted">
            {UNCONFIRMED_NOTES[status]}
          </span>
        ))}
        {row.sources.map((source, index) => {
          const key = `${owner}-${source.id}-${index}`;
          return (
            <SourceCitationChip
              key={key}
              sourceRef={source}
              sourceKey={key}
              isActive={activeSourceKey === key}
              onSelect={onSelectSource}
            />
          );
        })}
        {row.supportNote && <span className="text-xs text-ink-muted">{row.supportNote}</span>}
      </div>
      {hasReview && <ClaimViewReview row={row} caseId={caseId} />}
    </div>
  );
}
