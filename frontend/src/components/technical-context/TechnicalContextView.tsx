"use client";

import { useState } from "react";
import type { CaseAnalysisResultRead, CaseSourceRead } from "@/lib/api";
import { Icon } from "@/components/common/icons";
import { SourceDrawer } from "@/components/sources/SourceDrawer";
import type { SourceMessageRef } from "@/lib/caseOverview/types";
import {
  buildTechnicalContext,
  type RetrievedTechnicalContextCard,
  type TechnicalContextCard,
  type TechnicalContextData,
  type TechnicalContextStatus,
} from "@/lib/technicalContext";

interface TechnicalContextViewProps {
  analysisResult: CaseAnalysisResultRead | null;
  sources: CaseSourceRead[] | null;
  onOpenSources?: () => void;
  onNavigateToSource?: (messageId: string) => void;
}

function TechnicalItem({
  item,
  onSelectSource,
  activeSourceKey,
}: {
  item: TechnicalContextCard;
  onSelectSource: (source: SourceMessageRef, element: HTMLElement, key: string) => void;
  activeSourceKey: string | null;
}) {
  const [isDefinitionOpen, setIsDefinitionOpen] = useState(false);

  return (
    <article
      id={`mitre-${item.techniqueId}`}
      className="flex min-w-[17rem] flex-1 basis-[22rem] flex-col gap-4 rounded-lg border border-line bg-surface p-4 shadow-xs"
    >
      <div>
        <div className="flex flex-wrap items-baseline gap-2.5">
          <span className="font-mono text-[11px] text-mitre">{item.techniqueId}</span>
          <h2 className="text-sm font-extrabold text-ink">{item.techniqueName}</h2>
        </div>
        {item.tactic && <p className="mt-1 text-xs font-medium text-ink-muted">{item.tactic}</p>}
      </div>

      <RetrievalNote score={item.retrievalScore} retrievedBy={item.retrievedBy} />

      {item.shortPlainMeaning && (
        <div className="space-y-1">
          <h3 className="text-[11px] font-semibold text-ink-muted">What this technique means</h3>
          <p className="text-xs leading-relaxed text-ink-secondary">{item.shortPlainMeaning}</p>
        </div>
      )}

      <div className="space-y-1">
        <h3 className="text-[11px] font-semibold text-ink-muted">Analytical relevance</h3>
        <p className="text-xs leading-relaxed text-ink">{item.whyRelevantHere}</p>
      </div>

      {item.caseBasisSources.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-[11px] font-semibold text-ink-muted">Case source</h3>
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
                className={`block w-full rounded-md border-l-2 bg-surface-nested px-3 py-2 text-left transition-colors focus-visible:ring-2 focus-visible:ring-primary ${
                  isActive ? "border-ink" : "border-line-strong hover:border-ink"
                }`}
              >
                <p className="text-xs leading-relaxed text-ink">
                  {quoted ? `“${quoted}”` : "No quotation recorded."}
                </p>
                <p className="mt-1 text-[10px] text-ink-muted">{source.label} · open source</p>
              </button>
            );
          })}
        </div>
      )}

      {item.fullTechnicalDefinition && item.fullTechnicalDefinition !== item.shortPlainMeaning && (
        <details className="group border-t border-line/70 pt-3" open={isDefinitionOpen}>
          <summary
            className="flex cursor-pointer list-none items-center justify-between gap-2 text-[11px] font-bold text-ink-muted outline-none marker:hidden focus-visible:ring-2 focus-visible:ring-primary"
            onClick={(event) => {
              event.preventDefault();
              setIsDefinitionOpen((open) => !open);
            }}
          >
            <span>Technical definition</span>
            <Icon name="chevron" className="h-3 w-3 transition-transform group-open:rotate-180" />
          </summary>
          {isDefinitionOpen && (
            <p className="mt-2 border-l-2 border-mitre/30 pl-3 text-xs leading-relaxed text-ink-secondary select-text">
              {item.fullTechnicalDefinition}
            </p>
          )}
        </details>
      )}
    </article>
  );
}

/** How the technique was retrieved, and how closely it matched.
 *
 *  The number is the retriever's similarity between the case text and this
 *  technique's ATT&CK description. It says how strongly the technique was
 *  found, not whether mapping it to this claim is correct — which the analysis
 *  decided afterwards, and which nothing here measures.
 */
function RetrievalNote({
  score,
  retrievedBy,
}: {
  score: number | null;
  retrievedBy: "vector" | "graph";
}) {
  if (retrievedBy === "graph" || score === null) {
    return (
      <p className="text-[11px] leading-relaxed text-ink-muted">
        Reached by graph expansion from a matched technique, so it carries no match score.
      </p>
    );
  }
  const percent = Math.round(score * 100);
  return (
    <div className="space-y-1">
      <div className="flex items-baseline justify-between gap-2">
        <span className="text-[11px] font-semibold text-ink-muted">Retrieval match</span>
        <span className="font-mono text-[11px] font-bold text-ink">{score.toFixed(2)}</span>
      </div>
      <div className="h-1 w-full overflow-hidden rounded-full bg-surface-nested">
        <div className="h-full rounded-full bg-mitre" style={{ width: `${percent}%` }} />
      </div>
      <p className="text-[10px] leading-relaxed text-ink-muted">
        How closely the case text matched this technique&rsquo;s ATT&amp;CK description. It does not
        rate whether the mapping itself is right.
      </p>
    </div>
  );
}

function RetrievedOnlyItem({
  item,
  acceptedFromRag,
}: {
  item: RetrievedTechnicalContextCard;
  acceptedFromRag: boolean;
}) {
  const [isDefinitionOpen, setIsDefinitionOpen] = useState(false);
  return (
    <article className="flex min-w-[17rem] flex-1 basis-[22rem] flex-col gap-3 rounded-lg border border-line bg-surface p-4 shadow-xs">
      <div className="flex flex-wrap items-baseline gap-2.5">
        <span className="font-mono text-[11px] text-mitre">{item.techniqueId}</span>
        <h3 className="text-sm font-extrabold text-ink">{item.techniqueName}</h3>
      </div>
      {item.tactic && <p className="text-xs font-medium text-ink-muted">{item.tactic}</p>}
      <p className="text-[11px] font-semibold text-ink-muted">
        {acceptedFromRag
          ? "RAG-accepted external context · no case source mapping"
          : "Retrieved-only context · no validated Case mapping"}
      </p>
      {item.fullTechnicalDefinition && (
        <details open={isDefinitionOpen} className="border-t border-line/70 pt-3">
          <summary
            className="flex cursor-pointer list-none items-center justify-between gap-2 text-[11px] font-bold text-ink-muted marker:hidden focus-visible:ring-2 focus-visible:ring-primary"
            onClick={(event) => {
              event.preventDefault();
              setIsDefinitionOpen((open) => !open);
            }}
          >
            <span>Technical definition</span>
            <Icon name="chevron" className="h-3 w-3" />
          </summary>
          {isDefinitionOpen && (
            <p className="mt-2 border-l-2 border-mitre/30 pl-3 text-xs leading-relaxed text-ink-secondary select-text">
              {item.fullTechnicalDefinition}
            </p>
          )}
        </details>
      )}
    </article>
  );
}

function statusMessage(data: TechnicalContextData): { title: string; body: string } {
  const stage = data.failureStage ? ` during ${data.failureStage}` : "";
  const messages: Record<TechnicalContextStatus, { title: string; body: string }> = {
    not_applicable: {
      title: "MITRE augmentation was not applicable",
      body: "The Case did not meet the technical-context gate, so no external retrieval was performed.",
    },
    insufficient_context: {
      title: "Technical context was insufficient",
      body: "The augmentation result contains no supported MITRE context. No Case mapping is asserted.",
    },
    retrieved_with_matches: {
      title: `${data.totalCount} validated Case mapping${data.totalCount === 1 ? "" : "s"}`,
      body: "Only associations validated against case sources are shown as mappings. Retrieved-only rows remain separate.",
    },
    retrieved_without_supported_match: {
      title: "MITRE context retrieved without a supported Case match",
      body: "The retrieved rows are external context only. None was validated as a Case association.",
    },
    retrieved_from_rag: {
      title: `${data.retrievedOnlyCount} RAG technical reference${data.retrievedOnlyCount === 1 ? "" : "s"} accepted`,
      body: "All rows returned by the RAG service are shown as external technical context. No case source mapping is asserted.",
    },
    failed: {
      title: `Technical augmentation failed${stage}`,
      body: "No Case mapping is asserted from this augmentation attempt.",
    },
    invalid_trace: {
      title: "Saved technical trace is invalid",
      body: "The persisted trace or its augmentation binding could not be validated. Technical mappings are withheld.",
    },
    unavailable: {
      title: "Technical augmentation outcome is unavailable",
      body: "The saved result does not provide a verifiable augmentation outcome. No association was inferred.",
    },
  };
  return messages[data.status];
}

function ContextStatus({ data }: { data: TechnicalContextData }) {
  const message = statusMessage(data);
  return (
    <div className="rounded-lg border border-line bg-surface-nested px-4 py-3" role="status">
      <p className="text-sm font-extrabold text-ink">{message.title}</p>
      <p className="mt-1 text-xs leading-relaxed text-ink-secondary">{message.body}</p>
      {data.failureCode && (
        <p className="mt-2 font-mono text-[10px] uppercase tracking-wider text-critical">
          Failure code: {data.failureCode}
        </p>
      )}
    </div>
  );
}

export function TechnicalContextView({
  analysisResult,
  sources,
  onOpenSources,
  onNavigateToSource,
}: TechnicalContextViewProps) {
  const contextData = buildTechnicalContext(analysisResult, sources);
  const [activeSource, setActiveSource] = useState<{
    source: SourceMessageRef;
    element: HTMLElement;
  } | null>(null);
  const [activeSourceKey, setActiveSourceKey] = useState<string | null>(null);

  const handleSelectSource = (source: SourceMessageRef, element: HTMLElement, key: string) => {
    if (activeSourceKey === key) {
      setActiveSource(null);
      setActiveSourceKey(null);
      return;
    }
    setActiveSource({ source, element });
    setActiveSourceKey(key);
  };

  const handleCloseSource = () => {
    setActiveSource(null);
    setActiveSourceKey(null);
  };

  return (
    <section
      id="workspace-technical-context-panel"
      aria-label="Technical Context"
      className="flex shrink-0 flex-col bg-surface"
    >
      <div className="mx-auto w-full max-w-5xl space-y-8 px-5 py-7 sm:px-8 sm:py-9 lg:px-10">
        <header className="flex flex-wrap items-start justify-between gap-4 border-b border-line pb-5">
          <div>
            <h2 className="text-xl font-semibold tracking-[-0.02em] text-ink sm:text-2xl">
              Technical context
            </h2>
            <p className="mt-1.5 max-w-2xl text-xs leading-5 text-ink-muted">
              External technical augmentation derived from the Case analysis. It is not a case
              source.
            </p>
          </div>
          <span className="rounded-md border border-mitre/25 bg-mitre/5 px-2.5 py-1.5 text-[10px] font-semibold text-mitre">
            MITRE ATT&amp;CK
          </span>
        </header>

        {!contextData.hasContext ? (
          <div className="border-y border-line p-10 text-center sm:p-12">
            <span className="mx-auto flex h-10 w-10 items-center justify-center rounded-md bg-mitre/10 text-mitre">
              <Icon name="technical" className="h-5 w-5" />
            </span>
            <h2 className="mt-4 text-sm font-extrabold text-ink">
              {statusMessage(contextData).title}
            </h2>
            <p className="mx-auto mt-1 max-w-md text-xs leading-relaxed text-ink-muted">
              {statusMessage(contextData).body}
            </p>
            {contextData.failureCode && (
              <p className="mt-3 font-mono text-[10px] uppercase tracking-wider text-critical">
                Failure code: {contextData.failureCode}
              </p>
            )}
            {onOpenSources && (
              <button
                type="button"
                onClick={onOpenSources}
                className="btn-primary mt-5 inline-flex items-center gap-2 rounded-md"
              >
                <Icon name="sources" className="h-3.5 w-3.5" />
                Go to sources
              </button>
            )}
          </div>
        ) : (
          <section>
            <ContextStatus data={contextData} />
            {contextData.techniques.length > 0 && (
              <div className="pt-5">
                <div className="text-[11px] font-semibold tracking-[0.04em] text-ink-muted">
                  Validated Case mappings
                </div>
                <div className="mt-3 flex flex-wrap items-stretch gap-4 pb-6">
                  {contextData.techniques.map((item) => (
                    <TechnicalItem
                      key={item.associationId}
                      item={item}
                      onSelectSource={handleSelectSource}
                      activeSourceKey={activeSourceKey}
                    />
                  ))}
                </div>
              </div>
            )}
            {contextData.retrievedOnlyTechniques.length > 0 && (
              <div className="mt-2 border-t border-line/70">
                <div className="pt-5 text-[11px] font-semibold tracking-[0.04em] text-ink-muted">
                  {contextData.status === "retrieved_from_rag"
                    ? "RAG-provided technical context"
                    : "Retrieved-only technical context"}
                </div>
                <p className="mt-1 text-xs leading-relaxed text-ink-muted">
                  {contextData.status === "retrieved_from_rag"
                    ? "These rows came directly from the RAG service and are external context, not a case source."
                    : "These rows came from external retrieval and have no validated Case association or source citation."}
                </p>
                <div className="mt-3 flex flex-wrap items-stretch gap-4 pb-6">
                  {contextData.retrievedOnlyTechniques.map((item) => (
                    <RetrievedOnlyItem
                      key={item.techniqueId}
                      item={item}
                      acceptedFromRag={contextData.status === "retrieved_from_rag"}
                    />
                  ))}
                </div>
              </div>
            )}
          </section>
        )}
      </div>

      {activeSource && (
        <SourceDrawer
          sourceRef={activeSource.source}
          anchorElement={activeSource.element}
          onClose={handleCloseSource}
          onNavigateToSource={onNavigateToSource}
        />
      )}
    </section>
  );
}
