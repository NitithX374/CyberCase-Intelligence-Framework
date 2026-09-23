"use client";

import { useState } from "react";
import type { CaseAnalysisResultRead, CaseSourceRead } from "@/lib/api";
import { Icon } from "@/components/icons";
import { DisclosurePanel, DisclosureToggle } from "@/components/Disclosure";
import { SourceDrawer } from "@/features/sources/SourceDrawer";
import { useSourceDrawer } from "@/features/sources/useSourceDrawer";
import type { SourceMessageRef } from "@/features/sources/types";
import {
  buildTechnicalContext,
  type RetrievedTechnicalContextCard,
  type TechnicalContextCard,
  type TechnicalContextData,
  type TechnicalContextStatus,
} from "./technicalContext";

interface TechnicalContextViewProps {
  analysisResult: CaseAnalysisResultRead | null;
  sources: CaseSourceRead[] | null;
  onOpenSources?: () => void;
  onNavigateToSource?: (messageId: string) => void;
}

const SCORE_EXPLANATION =
  "How closely the case text matched this technique's ATT&CK description. It does not rate whether the mapping itself is right.";

function TechnicalItem({
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
        />
        <RetrievalScore score={item.retrievalScore} retrievedBy={item.retrievedBy} />
      </div>

      {item.shortPlainMeaning && (
        <p className="mt-1 text-sm leading-6 text-ink-secondary">{item.shortPlainMeaning}</p>
      )}

      {item.caseBasisSources.length > 0 && (
        <div className="mt-3 space-y-2">
          {item.caseBasisSources.map((source, index) => {
            const buttonKey = `${item.techniqueId}-source-${source.id}-${index}`;
            const isActive = activeSourceKey === buttonKey;
            const quoted = source.exactQuote ?? source.excerpt;
            return (
              <button
                key={buttonKey}
                type="button"
                onClick={(event) => onSelectSource(source, event.currentTarget, buttonKey)}
                aria-haspopup="dialog"
                className={`block w-full rounded-lg border-l-2 px-3 py-2 text-left transition-colors ${
                  isActive
                    ? "border-ink bg-surface-nested"
                    : "border-mitre/30 bg-surface-nested/60 hover:bg-surface-nested"
                }`}
              >
                <span className="block text-sm leading-6 text-ink">
                  {quoted ? `“${quoted}”` : "No quotation recorded."}
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
            label="Why it applies"
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

function TechniqueTitle({
  techniqueId,
  techniqueName,
  tactic,
  as: Heading = "h3",
}: {
  techniqueId: string;
  techniqueName: string;
  tactic: string;
  as?: "h3" | "h4";
}) {
  return (
    <div className="flex min-w-0 flex-wrap items-baseline gap-x-2 gap-y-0.5">
      <span className="font-mono text-xs text-mitre">{techniqueId}</span>
      <Heading className="text-[15px] font-semibold text-ink">{techniqueName}</Heading>
      {tactic && <span className="text-[13px] text-ink-muted">{tactic}</span>}
    </div>
  );
}

/** How the technique was retrieved, and how closely it matched.
 *
 *  The number is the retriever's similarity between the case text and this
 *  technique's ATT&CK description. It says how strongly the technique was
 *  found, not whether mapping it to this claim is correct — which the analysis
 *  decided afterwards, and which nothing here measures.
 */
function RetrievalScore({
  score,
  retrievedBy,
}: {
  score: number | null;
  retrievedBy: "vector" | "graph";
}) {
  if (retrievedBy === "graph" || score === null) {
    return (
      <span
        className="shrink-0 pt-0.5 text-xs text-ink-muted"
        title="Reached by graph expansion from a matched technique, so it carries no match score."
      >
        via graph
      </span>
    );
  }
  const percent = Math.round(score * 100);
  return (
    <div className="flex shrink-0 items-center gap-2 pt-1" title={SCORE_EXPLANATION}>
      <span className="sr-only">Retrieval match</span>
      <span className="h-1 w-12 overflow-hidden rounded-full bg-surface-nested" aria-hidden="true">
        <span className="block h-full rounded-full bg-mitre/70" style={{ width: `${percent}%` }} />
      </span>
      <span className="font-mono text-[13px] text-ink-secondary">{score.toFixed(2)}</span>
    </div>
  );
}

function RetrievedOnlyItem({ item }: { item: RetrievedTechnicalContextCard }) {
  return (
    <li className="py-3">
      <TechniqueTitle
        techniqueId={item.techniqueId}
        techniqueName={item.techniqueName}
        tactic={item.tactic}
        as="h4"
      />
      {item.fullTechnicalDefinition && (
        <p className="mt-1 line-clamp-2 text-sm leading-6 text-ink-secondary select-text">
          {item.fullTechnicalDefinition}
        </p>
      )}
    </li>
  );
}

function statusMessage(data: TechnicalContextData): string {
  const stage = data.failureStage ? ` during ${data.failureStage}` : "";
  const messages: Record<TechnicalContextStatus, string> = {
    not_applicable: "Not applicable — the case has no technical indicators.",
    insufficient_context: "No supported ATT&CK context was found.",
    retrieved_with_matches: "",
    retrieved_without_supported_match:
      "Techniques were retrieved, but none is supported by the case sources.",
    retrieved_from_rag: "Suggested by the knowledge base. Not tied to a case source.",
    failed: `The ATT&CK lookup failed${stage}.`,
    invalid_trace: "The saved ATT&CK context could not be verified, so it is not shown.",
    unavailable: "No ATT&CK context is available for this analysis.",
  };
  return messages[data.status];
}

export function TechnicalContextView({
  analysisResult,
  sources,
  onOpenSources,
  onNavigateToSource,
}: TechnicalContextViewProps) {
  const contextData = buildTechnicalContext(analysisResult, sources);
  const drawer = useSourceDrawer();
  const handleSelectSource = (
    sourceRef: SourceMessageRef,
    anchorElement: HTMLElement,
    key: string,
  ) => drawer.toggle({ sourceRef, anchorElement, key });

  const message = statusMessage(contextData);
  const retrievedOnly = contextData.retrievedOnlyTechniques;
  const count = contextData.techniques.length || retrievedOnly.length;

  return (
    <section
      id="workspace-technical-context-panel"
      aria-label="Technical Context"
      className="flex shrink-0 flex-col bg-surface"
    >
      <div className="mx-auto w-full max-w-[52rem] px-5 pt-16 sm:px-8">
        <header className="flex flex-wrap items-center justify-between gap-3 border-b border-line pb-3">
          <div className="flex items-baseline gap-2">
            <h2 className="text-base font-semibold text-ink">MITRE ATT&amp;CK</h2>
            {count > 0 && <span className="text-[13px] font-medium text-ink-muted">{count}</span>}
          </div>
          <span
            className="tag bg-mitre/[0.07] text-mitre"
            title="External technical reference. It is not a case source."
          >
            External reference
          </span>
        </header>

        {!contextData.hasContext ? (
          <div className="flex flex-wrap items-center justify-between gap-3 py-5" role="status">
            <p className="text-sm text-ink-muted">{message}</p>
            {onOpenSources && !analysisResult && (
              <button type="button" onClick={onOpenSources} className="btn-secondary h-8 px-3">
                <Icon name="sources" className="h-3.5 w-3.5" />
                Go to sources
              </button>
            )}
          </div>
        ) : (
          <>
            {message && (
              <p className="pt-5 text-sm text-ink-muted" role="status">
                {message}
                {contextData.failureCode && (
                  <span className="ml-2 font-mono text-xs text-critical">
                    {contextData.failureCode}
                  </span>
                )}
              </p>
            )}

            {contextData.techniques.length > 0 && (
              <div className="divide-y divide-line">
                {contextData.techniques.map((item) => (
                  <TechnicalItem
                    key={item.associationId}
                    item={item}
                    onSelectSource={handleSelectSource}
                    activeSourceKey={drawer.openKey}
                  />
                ))}
              </div>
            )}

            {retrievedOnly.length > 0 &&
              (contextData.techniques.length > 0 ? (
                <details className="group border-t border-line py-3">
                  <summary className="inline-flex h-8 cursor-pointer list-none items-center gap-1 rounded-md text-[13px] font-medium text-ink-secondary hover:text-ink">
                    Also retrieved, not linked to the case
                    <span className="text-ink-muted">{retrievedOnly.length}</span>
                    <Icon
                      name="chevron"
                      className="h-4 w-4 transition-transform group-open:rotate-180"
                    />
                  </summary>
                  <ul className="divide-y divide-line">
                    {retrievedOnly.map((item) => (
                      <RetrievedOnlyItem key={item.techniqueId} item={item} />
                    ))}
                  </ul>
                </details>
              ) : (
                <ul className="mt-2 divide-y divide-line">
                  {retrievedOnly.map((item) => (
                    <RetrievedOnlyItem key={item.techniqueId} item={item} />
                  ))}
                </ul>
              ))}

            {contextData.techniques.some((item) => item.retrievalScore !== null) && (
              <p className="border-t border-line pt-3 text-xs text-ink-muted">
                Scores show retrieval similarity, not whether a mapping is right.
              </p>
            )}
          </>
        )}
      </div>

      {drawer.open && (
        <SourceDrawer
          sourceRef={drawer.open.sourceRef}
          anchorElement={drawer.open.anchorElement}
          onClose={drawer.close}
          onNavigateToSource={onNavigateToSource}
        />
      )}
    </section>
  );
}
