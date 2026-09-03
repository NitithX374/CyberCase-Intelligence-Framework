"use client";

import { useState } from "react";
import type { PersistedChatMessage } from "@/lib/api";
import type { SourceMessageRef } from "@/lib/case-overview";
import { sourceReferencesForAnalysisMessage } from "@/lib/analysis-citations";
import { SourceEvidencePopover } from "@/components/overview/SourceEvidencePopover";
import { EvidenceCitationChip } from "@/components/evidence/EvidenceCitationChip";

interface AnalysisEvidenceReferencesProps {
  analysisMessage: PersistedChatMessage;
  messages: PersistedChatMessage[];
}

export function AnalysisEvidenceReferences({
  analysisMessage,
  messages,
}: AnalysisEvidenceReferencesProps) {
  const references = sourceReferencesForAnalysisMessage(analysisMessage, messages);
  const [active, setActive] = useState<{
    key: string;
    source: SourceMessageRef;
    anchor: HTMLElement;
    role: "supporting" | "conflicting";
  } | null>(null);
  if (references.length === 0) return null;

  return (
    <div className="mt-4 border-t border-line/70 pt-3">
      <p className="text-[10px] font-bold uppercase tracking-[0.1em] text-ink-muted">
        Evidence references
      </p>
      <div className="mt-2 flex flex-wrap gap-1.5">
        {references.map((reference, index) => {
          const key = `${reference.role}-${reference.source.id}-${index}`;
          const isActive = active?.key === key;
          return (
            <EvidenceCitationChip
              key={key}
              sourceRef={reference.source}
              sourceKey={key}
              isActive={isActive}
              citationRole={reference.role}
              onSelect={(source, anchor, sourceKey) => setActive((current) =>
                current?.key === sourceKey
                  ? null
                  : { key: sourceKey, source, anchor, role: reference.role }
              )}
            />
          );
        })}
      </div>
      {active && (
        <SourceEvidencePopover
          sourceRef={active.source}
          anchorElement={active.anchor}
          onClose={() => setActive(null)}
          citationRole={active.role}
        />
      )}
    </div>
  );
}
