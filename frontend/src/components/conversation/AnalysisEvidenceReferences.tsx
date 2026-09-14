"use client";

import { useState } from "react";
import type { PersistedChatMessage } from "@/lib/api";
import type { SourceMessageRef } from "@/lib/case-overview-contracts";
import { sourceReferencesForAnalysisMessage } from "@/lib/analysis-citations";
import { SourceEvidenceDrawer } from "@/components/evidence/SourceEvidenceDrawer";
import { EvidenceCitationChip } from "@/components/evidence/EvidenceCitationChip";

interface AnalysisEvidenceReferencesProps {
  analysisMessage: PersistedChatMessage;
  messages: PersistedChatMessage[];
  onNavigateToSource?: (messageId: string) => void;
}

export function AnalysisEvidenceReferences({
  analysisMessage,
  messages,
  onNavigateToSource,
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
      <p className="text-[10px] font-semibold tracking-[0.04em] text-ink-muted">
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
        <SourceEvidenceDrawer
          sourceRef={active.source}
          anchorElement={active.anchor}
          onClose={() => setActive(null)}
          citationRole={active.role}
          onNavigateToSource={onNavigateToSource}
        />
      )}
    </div>
  );
}
