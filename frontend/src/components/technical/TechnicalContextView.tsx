"use client";

import { useState } from "react";
import type { CaseAnalysisResultRead, CaseEvidenceSnapshotRead, PersistedChatMessage } from "@/lib/api";
import { Icon } from "@/components/common/icons";
import { SourceEvidencePopover } from "@/components/overview/SourceEvidencePopover";
import type { SourceMessageRef } from "@/lib/case-overview";
import {
  buildNativeTechnicalContext,
  buildTechnicalContext,
  type RetrievedTechnicalContextCard,
  type TechnicalContextCard,
  type TechnicalContextData,
  type TechnicalContextStatus,
} from "@/lib/technicalContext";

interface TechnicalContextViewProps {
  messages: PersistedChatMessage[];
  nativeAnalysisResult?: CaseAnalysisResultRead | null;
  nativeEvidenceSnapshot?: CaseEvidenceSnapshotRead | null;
  onOpenIntake?: () => void;
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
    <article id={`mitre-${item.techniqueId}`} className="space-y-4 py-6 first:pt-2 last:pb-2">
      <div>
        <div className="flex flex-wrap items-baseline gap-2.5">
          <span className="font-mono text-[11px] text-mitre">
            {item.techniqueId}
          </span>
          <h2 className="text-sm font-extrabold text-ink">{item.techniqueName}</h2>
        </div>
        {item.tactic && <p className="mt-1 text-xs font-medium text-ink-muted">{item.tactic}</p>}
      </div>

      {item.shortPlainMeaning && (
        <div className="space-y-1">
          <h3 className="text-[11px] font-bold uppercase tracking-[0.08em] text-ink-muted">ความหมายโดยย่อ</h3>
          <p className="text-xs leading-relaxed text-ink-secondary">{item.shortPlainMeaning}</p>
        </div>
      )}

      <div className="space-y-1">
        <h3 className="text-[11px] font-bold uppercase tracking-[0.08em] text-ink-muted">เหตุผลการเชื่อมโยงเชิงวิเคราะห์</h3>
        <p className="text-xs leading-relaxed text-ink">{item.whyRelevantHere}</p>
      </div>

      {item.caseBasisSources.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="text-[11px] text-ink-muted">แหล่งข้อมูล:</span>
          {item.caseBasisSources.map((source) => {
            const buttonKey = `${item.techniqueId}-source-${source.id}`;
            const isActive = activeSourceKey === buttonKey;
            return (
              <button
                key={source.id}
                type="button"
                onClick={(event) => onSelectSource(source, event.currentTarget, buttonKey)}
                aria-haspopup="dialog"
                className={`inline-flex max-w-full items-center gap-1 rounded-sm py-1 text-[11px] font-medium underline decoration-current/40 underline-offset-4 transition-colors focus-visible:ring-2 focus-visible:ring-primary ${
                  isActive
                    ? "text-ink decoration-current"
                    : "text-ink-secondary hover:text-ink hover:decoration-current"
                }`}
              >
                Source — {source.label} <span aria-hidden="true">↗</span>
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
            <span>คำอธิบายทางเทคนิค</span>
            <Icon name="chevron" className="h-3 w-3 transition-transform group-open:rotate-180" />
          </summary>
          {isDefinitionOpen && (
            <p className="mt-2 rounded-lg border border-line bg-canvas/60 p-3 text-xs leading-relaxed text-ink-secondary select-text">
              {item.fullTechnicalDefinition}
            </p>
          )}
        </details>
      )}
    </article>
  );
}

function RetrievedOnlyItem({ item }: { item: RetrievedTechnicalContextCard }) {
  const [isDefinitionOpen, setIsDefinitionOpen] = useState(false);
  return (
    <article className="space-y-3 py-4 first:pt-2 last:pb-2">
      <div className="flex flex-wrap items-baseline gap-2.5">
        <span className="font-mono text-[11px] text-mitre">{item.techniqueId}</span>
        <h3 className="text-sm font-extrabold text-ink">{item.techniqueName}</h3>
      </div>
      {item.tactic && <p className="text-xs font-medium text-ink-muted">{item.tactic}</p>}
      <p className="text-[11px] font-semibold text-ink-muted">Retrieved-only context · no validated Case mapping</p>
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
          {isDefinitionOpen && <p className="mt-2 rounded-lg border border-line bg-canvas/60 p-3 text-xs leading-relaxed text-ink-secondary select-text">{item.fullTechnicalDefinition}</p>}
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
      body: "Only associations validated against Case evidence are shown as mappings. Retrieved-only rows remain separate.",
    },
    retrieved_without_supported_match: {
      title: "MITRE context retrieved without a supported Case match",
      body: "The retrieved rows are external context only. None was validated as a Case association.",
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
    <div className="border-b border-line/70 px-4 py-4 sm:px-6" role="status">
      <p className="text-sm font-extrabold text-ink">{message.title}</p>
      <p className="mt-1 text-xs leading-relaxed text-ink-secondary">{message.body}</p>
      {data.failureCode && <p className="mt-2 font-mono text-[10px] uppercase tracking-wider text-critical">Failure code: {data.failureCode}</p>}
    </div>
  );
}

export function TechnicalContextView({
  messages,
  nativeAnalysisResult,
  nativeEvidenceSnapshot,
  onOpenIntake,
  onNavigateToSource,
}: TechnicalContextViewProps) {
  const isNativeContext = nativeAnalysisResult !== undefined || nativeEvidenceSnapshot !== undefined;
  const contextData =
    isNativeContext
      ? buildNativeTechnicalContext(nativeAnalysisResult ?? null, nativeEvidenceSnapshot ?? null)
      : buildTechnicalContext(messages);
  const [activePopover, setActivePopover] = useState<{
    source: SourceMessageRef;
    element: HTMLElement;
  } | null>(null);
  const [activeSourceKey, setActiveSourceKey] = useState<string | null>(null);

  const handleSelectSource = (source: SourceMessageRef, element: HTMLElement, key: string) => {
    if (activeSourceKey === key) {
      setActivePopover(null);
      setActiveSourceKey(null);
      return;
    }
    setActivePopover({ source, element });
    setActiveSourceKey(key);
  };

  const handleClosePopover = () => {
    setActivePopover(null);
    setActiveSourceKey(null);
  };

  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-y-auto bg-canvas">
      <div className="mx-auto w-full max-w-4xl space-y-7 px-4 py-6 sm:px-7 sm:py-8 lg:px-9">
        <header className="border-b border-line pb-5">
          <p className="section-eyebrow">OPTIONAL TECHNICAL CONTEXT</p>
          <div className="mt-1 flex flex-wrap items-center justify-between gap-3">
            <h1 className="text-2xl font-extrabold tracking-[-0.035em] text-ink sm:text-3xl">MITRE ATT&amp;CK Context</h1>
          </div>
          <p className="mt-2 text-xs font-bold text-ink-secondary">External technical reference · not case evidence</p>
          <p className="mt-1 max-w-2xl text-xs leading-relaxed text-ink-muted">
            MITRE ATT&amp;CK is used here to help explain technical behavior described in the case. การเชื่อมโยงเป็นข้อเสนอเชิงวิเคราะห์ ไม่ใช่ข้อเท็จจริงจากคดี
          </p>
        </header>

        {!contextData.hasContext ? (
          <div className="workspace-card p-10 text-center sm:p-12">
            <span className="mx-auto flex h-11 w-11 items-center justify-center rounded-xl bg-mitre/10 text-mitre">
              <Icon name="technical" className="h-5 w-5" />
            </span>
            <h2 className="mt-4 text-sm font-extrabold text-ink">{isNativeContext ? statusMessage(contextData).title : contextData.status === "invalid_trace" ? "Technical context cannot be validated." : "No relevant MITRE ATT&CK context is currently available."}</h2>
            <p className="mx-auto mt-1 max-w-md text-xs leading-relaxed text-ink-muted">{statusMessage(contextData).body}</p>
            {contextData.failureCode && <p className="mt-3 font-mono text-[10px] uppercase tracking-wider text-critical">Failure code: {contextData.failureCode}</p>}
            {onOpenIntake && (
              <button type="button" onClick={onOpenIntake} className="btn-primary mt-5 inline-flex items-center gap-2 rounded-lg">
                <Icon name="intake" className="h-3.5 w-3.5" />
                Go to Case Intake · เปิดสำนวนคดี
              </button>
            )}
          </div>
        ) : (
          <section className="workspace-card px-4 sm:px-6">
            <ContextStatus data={contextData} />
            {contextData.techniques.length > 0 && (
              <div className="divide-y divide-line/70">
                <div className="px-0 pt-5 text-[11px] font-bold uppercase tracking-[0.08em] text-ink-muted">Validated Case mappings</div>
                {contextData.techniques.map((item) => (
                  <TechnicalItem
                    key={item.associationId}
                    item={item}
                    onSelectSource={handleSelectSource}
                    activeSourceKey={activeSourceKey}
                  />
                ))}
              </div>
            )}
            {contextData.retrievedOnlyTechniques.length > 0 && (
              <div className="mt-2 border-t border-line/70">
                <div className="pt-5 text-[11px] font-bold uppercase tracking-[0.08em] text-ink-muted">Retrieved-only technical context</div>
                <p className="mt-1 text-xs leading-relaxed text-ink-muted">These rows came from external retrieval and have no validated Case association or evidence citation.</p>
                <div className="divide-y divide-line/70 pt-2">
                  {contextData.retrievedOnlyTechniques.map((item) => <RetrievedOnlyItem key={item.techniqueId} item={item} />)}
                </div>
              </div>
            )}
          </section>
        )}
      </div>

      {activePopover && (
        <SourceEvidencePopover
          sourceRef={activePopover.source}
          anchorElement={activePopover.element}
          onClose={handleClosePopover}
          onNavigateToSource={onNavigateToSource}
        />
      )}
    </div>
  );
}
