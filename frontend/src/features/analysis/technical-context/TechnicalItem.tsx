"use client";

import { useState } from "react";
import { DisclosurePanel, DisclosureToggle } from "@/components/Disclosure";
import type { SourceMessageRef } from "@/features/citations/types";
import { NO_CHECKED_QUOTE } from "@/features/citations/unconfirmed";
import type { TechnicalContextCard } from "./technicalContext";
import { TechniqueTitle } from "./TechniqueTitle";
import { RetrievalScore } from "./RetrievalScore";

export function TechnicalItem({
  item,
  onSelectSource,
  activeSourceKey,
}: {
  item: TechnicalContextCard;
  onSelectSource: (source: SourceMessageRef, element: HTMLElement, key: string) => void;
  activeSourceKey: string | null;
}) {
  const [isOpen, setIsOpen] = useState(false);
  const detailsId = `mitre-${item.techniqueId}-details`;
  const hasDefinition =
    Boolean(item.fullTechnicalDefinition) &&
    item.fullTechnicalDefinition !== item.shortPlainMeaning;

  return (
    <article id={`mitre-${item.techniqueId}`} className="scroll-mt-24 py-5">
      <div className="flex items-start justify-between gap-4">
        <TechniqueTitle
          techniqueId={item.techniqueId}
          techniqueName={item.techniqueName}
          tactic={item.tactic}
          mitreUrl={item.mitreUrl}
        />
        <RetrievalScore score={item.retrievalScore} retrievedBy={item.retrievedBy} />
      </div>

      {item.shortPlainMeaning && (
        <p className="mt-1 text-sm leading-6 text-ink-secondary">{item.shortPlainMeaning}</p>
      )}

      {item.caseBasisSources.length === 0 && !item.casePassage && (
        <p className="mt-2 text-xs text-ink-muted">
          No case source is recorded for this technique.
        </p>
      )}

      {item.casePassage && (
        <div className="mt-3 border-l-2 border-line-strong py-1 pl-3">
          <p className="text-sm leading-6 text-ink">{item.casePassage}</p>
          <p className="mt-0.5 text-xs text-ink-muted">
            Tied to this technique by the retrieval service, not checked
          </p>
        </div>
      )}

      {item.caseBasisSources.length > 0 && (
        <div className="mt-3 space-y-2">
          {item.caseBasisSources.map((source, index) => {
            const buttonKey = `${item.techniqueId}-source-${source.id}-${index}`;
            const isActive = activeSourceKey === buttonKey;
            return (
              <button
                key={buttonKey}
                type="button"
                onClick={(event) => onSelectSource(source, event.currentTarget, buttonKey)}
                aria-haspopup="dialog"
                className={`block w-full border-l-2 py-1 pl-3 text-left transition-colors ${
                  isActive ? "border-ink" : "border-line-strong hover:border-ink"
                }`}
              >
                <span
                  className={`block text-sm leading-6 ${source.exactQuote ? "text-ink" : "text-ink-muted"}`}
                >
                  {source.exactQuote ? `“${source.exactQuote}”` : NO_CHECKED_QUOTE}
                </span>
                <span className="mt-0.5 block text-xs text-ink-muted">{source.label}</span>
              </button>
            );
          })}
        </div>
      )}

      {(item.whyRelevantHere || hasDefinition) && (
        <>
          <DisclosureToggle
            label={item.whyRelevantHere ? "Why it applies" : "ATT&CK definition"}
            isOpen={isOpen}
            onToggle={() => setIsOpen((open) => !open)}
            controls={detailsId}
            className="-ml-1.5 mt-2"
          />
          {isOpen && (
            <DisclosurePanel id={detailsId} className="mt-1 space-y-2">
              {item.whyRelevantHere && <p className="text-ink">{item.whyRelevantHere}</p>}
              {hasDefinition && <p className="select-text">{item.fullTechnicalDefinition}</p>}
            </DisclosurePanel>
          )}
        </>
      )}
    </article>
  );
}
