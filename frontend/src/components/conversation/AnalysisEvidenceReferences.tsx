"use client";

import { useState } from "react";
import type { PersistedChatMessage } from "@/lib/api";
import type { SourceMessageRef } from "@/lib/case-overview";
import { sourceReferencesForAnalysisMessage } from "@/lib/analysis-citations";
import { SourceEvidencePopover } from "@/components/overview/SourceEvidencePopover";

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
            <button
              key={key}
              type="button"
              aria-expanded={isActive}
              onClick={(event) => setActive((current) =>
                current?.key === key
                  ? null
                  : { key, source: reference.source, anchor: event.currentTarget }
              )}
              className={`rounded-full border px-2.5 py-1 text-[10px] font-bold transition-colors focus-visible:ring-2 focus-visible:ring-primary ${
                isActive
                  ? "border-primary bg-primary text-ivory"
                  : reference.role === "conflicting"
                    ? "border-unresolved/35 bg-unresolved/8 text-unresolved"
                    : "border-line bg-surface text-ink-secondary hover:border-ink"
              }`}
            >
              {reference.role === "conflicting" ? "Conflict · " : ""}
              {reference.source.label}
            </button>
          );
        })}
      </div>
      {active && (
        <SourceEvidencePopover
          sourceRef={active.source}
          anchorElement={active.anchor}
          onClose={() => setActive(null)}
        />
      )}
    </div>
  );
}
