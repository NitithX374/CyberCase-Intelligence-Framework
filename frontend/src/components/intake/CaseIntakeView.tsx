"use client";

import { useMemo, useState, type FormEvent } from "react";
import type { CaseIntakeSubmission, PersistedChatMessage, ThreadStatus } from "@/lib/api";
import { bindCaseNarrativeDocumentSource, type CaseNarrativeDraft } from "@/lib/case-narrative-document";
import { isCaseEvidenceMessage } from "@/lib/case-evidence";
import { buildCaseOverview } from "@/lib/case-overview";
import { intakeMaterials, intakeStatus } from "@/lib/case-intake-model";
import { useDocumentIngestion } from "@/lib/document-ingestion-store";
import { DocumentIngestionPreview } from "./DocumentIngestionPreview";
import { DocumentIngestionResult } from "./DocumentIngestionResult";
import { CaseIntakeFiles } from "./CaseIntakeFiles";
import { ExtractedTextPreview } from "./ExtractedTextPreview";
import { IntakeNarrativeForm } from "./IntakeNarrativeForm";
import { intakeReadableText } from "@/lib/intake-readable-text";
import type { CaseOverviewData } from "@/lib/case-overview";

interface CaseIntakeViewProps {
  caseKey?: string;
  threadId?: string | null;
  threadStatus?: ThreadStatus | null;
  isSubmitting: boolean;
  error?: string | null;
  onSubmitCase: (data: CaseIntakeSubmission) => void;
  messages?: PersistedChatMessage[];
  onOpenOverview?: () => void;
  onOpenChat?: () => void;
  onOpenMaterials?: () => void;
}

export function CaseIntakeView(props: CaseIntakeViewProps) {
  const caseKey = (props.caseKey ?? props.threadId ?? props.messages?.[0]?.thread_id ?? "draft").trim() || "draft";
  return <CaseIntakeContent key={caseKey} {...props} caseKey={caseKey} />;
}

function CaseIntakeContent({
  caseKey, threadId, threadStatus, isSubmitting, error, onSubmitCase, messages = [],
  onOpenOverview, onOpenChat, onOpenMaterials,
}: CaseIntakeViewProps & { caseKey: string }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [documentDraft, setDocumentDraft] = useState<CaseNarrativeDraft | null>(null);
  const [includeSource, setIncludeSource] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const ingestion = useDocumentIngestion(caseKey);
  const evidence = messages.filter(isCaseEvidenceMessage);
  const hasEvidence = evidence.length > 0;
  const overview = useMemo(() => buildCaseOverview(messages, threadStatus), [messages, threadStatus]);
  const materials = intakeMaterials(messages, ingestion, hasEvidence ? undefined : documentDraft?.source);
  const selected = materials.find((item) => item.id === selectedId);
  const unreviewed = materials.some((item) => item.pending);
  const status = intakeStatus({
    ingestion, hasEvidence, hasAnalysis: overview.hasAnalysis, isSubmitting,
    hasNarrative: Boolean(description.trim()), hasUnreviewedMaterial: unreviewed,
    failed: Boolean(error) || threadStatus === "failed",
  });
  const canSubmit = Boolean(description.trim()) && !isSubmitting && !ingestion.isProcessing && !unreviewed;
  const showSavedPreview = hasEvidence && ingestion.result && (!selected || selected.pending);
  const nextAction = isSubmitting ? onOpenChat : overview.hasAnalysis ? onOpenOverview : onOpenChat;
  const nextLabel = isSubmitting ? "View analysis progress"
    : overview.hasAnalysis ? "Continue to Analysis" : "Open analysis in Chat";

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!canSubmit) return;
    const narrative = description.trim();
    onSubmitCase({
      title: title.trim() || undefined,
      description: narrative,
      documentSources: documentDraft && includeSource ? [bindCaseNarrativeDocumentSource(documentDraft, narrative)] : undefined,
    });
  };
  const useDocument = (draft: CaseNarrativeDraft) => {
    setDescription(draft.text);
    setDocumentDraft(draft);
    setIncludeSource(true);
  };

  return (
    <div id="workspace-intake-panel" role="region" aria-label="Case Intake" className="flex min-h-0 flex-1 flex-col bg-canvas">
      <div className="min-h-0 flex-1 overflow-y-auto">
        <div className="mx-auto w-full max-w-6xl space-y-6 px-4 py-5 sm:px-7 lg:px-9">
          <header className="space-y-4 border-b border-line pb-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="section-eyebrow">CASE INTAKE</p>
                <h1 className="mt-1 text-xl font-bold tracking-tight text-ink sm:text-2xl">Case preparation</h1>
                {threadId && <p className="mt-1 text-[11px] text-ink-muted">Case {threadId.slice(0, 8)}</p>}
              </div>
              <div role="status" aria-live="polite" className="max-w-sm text-xs leading-relaxed text-ink-secondary">
                <p className="font-semibold text-ink">{status.label}</p>
                <p className="mt-1">{status.detail}</p>
              </div>
            </div>
            <p aria-label="Preparation progress" className="text-[11px] leading-relaxed text-ink-secondary">
              {materials.length ? `${materials.length} ${materials.length === 1 ? "document" : "documents"}` : "Written narrative"}
              {" · "}
              {ingestion.isProcessing ? "Text extraction in progress"
                : ingestion.error ? "Text extraction failed"
                  : ingestion.result ? "Text extraction complete"
                    : ingestion.fileName ? "Awaiting extraction"
                      : materials.some((item) => item.pageCount !== null) ? "Document text submitted" : "No extraction needed"}
              {" · "}
              {unreviewed ? "Review pending" : hasEvidence ? "Narrative submitted" : documentDraft ? "Text reviewed" : "Review before submitting"}
            </p>
          </header>
          <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_17rem]">
            <div className="min-w-0 space-y-5">
              {hasEvidence ? showSavedPreview ? (
                <section className="workspace-card min-w-0 space-y-4 p-5 sm:p-6">
                  <DocumentIngestionResult result={ingestion.result!} />
                  <div className="border-t border-line pt-4 text-xs leading-relaxed text-ink-secondary">
                    <p>This document is a preview and has not been added to the saved case. Use Add case information in Chat to submit additional material.</p>
                    {onOpenChat && <button type="button" onClick={onOpenChat} className="mt-2 min-h-9 underline underline-offset-4">Add information in Chat →</button>}
                  </div>
                </section>
              ) : (
                <ExistingCaseRecord message={selected?.messageId ? evidence.find((message) => message.id === selected.messageId) : evidence[0]} text={selected?.text ?? undefined} filename={selected?.filename} />
              ) : (
                <IntakeNarrativeForm title={title} description={description} draft={documentDraft}
                  result={ingestion.result} disabled={isSubmitting} sourceLinked={includeSource}
                  onTitle={setTitle} onDescription={setDescription} onUseDocument={useDocument}
                  onRemoveSource={() => setIncludeSource(false)} onSubmit={handleSubmit} />
              )}
              <ExtractedCaseSummary overview={overview} sourceCount={evidence.length} onReview={onOpenOverview} />
            </div>
            <CaseIntakeFiles materials={materials} selectedId={selected?.id ?? (showSavedPreview ? ingestion.result?.document_id ?? null : null)}
              onSelect={(material) => setSelectedId(material.id)} onOpenMaterials={hasEvidence ? onOpenMaterials : undefined}>
              <DocumentIngestionPreview caseKey={caseKey} disabled={isSubmitting} showResult={false} />
            </CaseIntakeFiles>
          </div>
        </div>
      </div>
      <footer className="shrink-0 border-t border-line bg-surface">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-7 lg:px-9">
          <p className="text-[11px] text-ink-muted">{hasEvidence ? "Submitted narrative saved" : "Draft · Not yet submitted"}</p>
          {hasEvidence ? (
            nextAction && <button type="button" onClick={nextAction} className="btn-primary min-h-10 rounded-lg">{nextLabel} →</button>
          ) : (
            <button type="submit" form="intake-narrative-form" disabled={!canSubmit} className="btn-primary min-h-10 rounded-lg">
              {isSubmitting ? "Analyzing case…" : "Analyze case"} →
            </button>
          )}
        </div>
      </footer>
    </div>
  );
}

export function ExistingCaseRecord({ message, text, filename }: {
  message?: PersistedChatMessage;
  text?: string;
  filename?: string;
}) {
  return (
    <section className="workspace-card min-w-0 space-y-4 p-5 sm:p-6">
      <div>
        <h2 className="text-base font-bold text-ink">Case information</h2>
        <p className="mt-1 break-words text-xs text-ink-secondary">{filename ?? "Submitted case narrative"}</p>
        {message && <p className="mt-1 text-[11px] text-ink-muted">Submitted {new Date(message.created_at).toLocaleString("en-GB")}</p>}
      </div>
      <ExtractedTextPreview key={filename ?? message?.id} text={text ?? message?.content ?? ""} label="Case narrative" />
    </section>
  );
}

export function ExtractedCaseSummary({ overview, sourceCount, onReview }: {
  overview: CaseOverviewData;
  sourceCount: number;
  onReview?: () => void;
}) {
  return (
    <section aria-labelledby="extracted-case-heading" className="border-t border-line pt-5">
      <h2 id="extracted-case-heading" className="text-sm font-bold text-ink">Extracted case information</h2>
      {overview.hasAnalysis ? (
        <>
          <p className="mt-1 text-[11px] text-ink-muted">From the latest completed case analysis.</p>
          <p className="mt-3 line-clamp-3 text-xs leading-relaxed text-ink-secondary">{intakeReadableText(overview.incidentSummary)}</p>
          <dl className="mt-4 grid grid-cols-3 gap-3 text-xs">
            <div><dt className="text-ink-muted">Findings</dt><dd className="mt-1 font-semibold">{overview.findings.length}</dd></div>
            <div><dt className="text-ink-muted">Evidence messages</dt><dd className="mt-1 font-semibold">{sourceCount}</dd></div>
            <div><dt className="text-ink-muted">Open questions</dt><dd className="mt-1 font-semibold">{overview.gaps.length}</dd></div>
          </dl>
          {onReview && <button type="button" onClick={onReview} className="mt-3 min-h-9 text-xs text-ink-secondary underline underline-offset-4 hover:text-ink">Review extracted information →</button>}
        </>
      ) : <p className="mt-2 text-xs leading-relaxed text-ink-muted">Findings and open questions become available after case analysis. Document extraction prepares the text only.</p>}
    </section>
  );
}
