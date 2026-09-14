"use client";

import { useMemo, type FormEvent } from "react";
import { Icon } from "@/components/common/icons";
import { StatusPill } from "@/components/common/StatusPill";
import { useAccountState } from "@/hooks/use-account-state";
import type { CaseAnalysisResultRead, CaseDocumentRead, CaseIntakeSubmission, CaseRunRead, EvidenceSourceRead } from "@/lib/api";

interface CaseIntakeViewProps {
  caseId: string;
  documents: CaseDocumentRead[];
  evidence: EvidenceSourceRead[];
  analysisResult: CaseAnalysisResultRead | null;
  run: CaseRunRead | null;
  isSubmitting: boolean;
  isCaseDataLoading: boolean;
  error?: string | null;
  isUploadingDocument: boolean;
  admittingExtractionId: string | null;
  onSubmitCase: (data: CaseIntakeSubmission) => void;
  onUploadDocument: (file: File) => void;
  onAdmitExtraction: (documentId: string, extractionId: string) => void;
  onOpenOverview?: () => void;
  onOpenChat?: () => void;
  onOpenMaterials?: () => void;
}

export function CaseIntakeView({
  caseId,
  documents,
  evidence,
  analysisResult,
  run,
  isSubmitting,
  isCaseDataLoading,
  error,
  isUploadingDocument,
  admittingExtractionId,
  onSubmitCase,
  onUploadDocument,
  onAdmitExtraction,
  onOpenOverview,
  onOpenChat,
  onOpenMaterials,
}: CaseIntakeViewProps) {
  const [title, setTitle] = useAccountState(`case-intake:${caseId}:title`, "");
  const [description, setDescription] = useAccountState(`case-intake:${caseId}:description`, "");
  const admittedExtractionIds = useMemo(
    () =>
      new Set(
        evidence.flatMap((source) => {
          const prov = source.provenance_json as Record<string, unknown> | undefined;
          const extractionId = prov?.extraction_id as string | undefined;
          return [extractionId, source.document_id].filter(Boolean) as string[];
        }),
      ),
    [evidence],
  );
  const hasEvidence = evidence.length > 0;
  const isBusy = isSubmitting || isCaseDataLoading;
  const canSubmit = !isBusy && Boolean(description.trim() || hasEvidence);
  const status = intakeStatus({ isSubmitting, isCaseDataLoading, failed: run?.status === "failed", analysisResult, hasEvidence });

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!canSubmit) return;
    onSubmitCase({ title: title.trim() || undefined, description: description.trim() });
  };

  return (
    <div id="workspace-intake-panel" role="tabpanel" aria-label="Case Intake" className="min-h-0 flex-1 overflow-y-auto bg-surface">
      <form id="case-first-intake-form" onSubmit={handleSubmit} className="mx-auto w-full max-w-5xl space-y-9 px-5 py-7 sm:px-8 sm:py-9 lg:px-10">
        <header className="flex flex-wrap items-start justify-between gap-4 border-b border-line pb-5">
          <div>
            <h2 className="text-xl font-semibold tracking-[-0.02em] text-ink sm:text-2xl">Case preparation</h2>
            <p className="mt-1.5 max-w-2xl text-xs leading-5 text-ink-muted">Add the information and reviewed documents that should be included in the next Case analysis.</p>
          </div>
          <div role="status" aria-live="polite" className="flex items-center gap-2 text-xs font-medium text-ink-secondary">
            <span className={`h-1.5 w-1.5 rounded-full ${run?.status === "failed" ? "bg-critical" : isBusy ? "bg-evidence motion-safe:animate-pulse" : "bg-established"}`} />
            {status}
          </div>
        </header>

        {error && <p role="alert" className="border-l-2 border-critical px-3 py-2 text-xs text-ink">{error}</p>}

        <section aria-labelledby="case-description-heading" className="space-y-4">
          <div>
            <h3 id="case-description-heading" className="text-base font-semibold text-ink">Case description</h3>
            <p className="mt-1 text-xs text-ink-muted">The narrative is admitted as user-provided Case information when analysis begins.</p>
          </div>
          <div className="grid gap-4 sm:grid-cols-[12rem_minmax(0,1fr)]">
            <label htmlFor="case-first-title-input" className="pt-2 text-xs font-medium text-ink-secondary">Case title <span className="text-ink-muted">(optional)</span></label>
            <input id="case-first-title-input" value={title} onChange={(event) => setTitle(event.target.value)} disabled={isBusy} placeholder="A short name for this case" className="w-full border-b border-line bg-transparent px-0 py-2 text-sm text-ink outline-none placeholder:text-ink-muted focus:border-accent disabled:text-ink-disabled" />
          </div>
          <div className="grid gap-4 sm:grid-cols-[12rem_minmax(0,1fr)]">
            <label htmlFor="case-first-description-input" className="pt-2 text-xs font-medium text-ink-secondary">Case information</label>
            <textarea id="case-first-description-input" rows={7} value={description} onChange={(event) => setDescription(event.target.value)} disabled={isBusy} placeholder="Describe what happened, who was involved, and the dates or details available in the case material." className="block min-h-44 w-full resize-y rounded-md border border-line bg-surface p-3.5 text-sm leading-6 text-ink outline-none placeholder:text-ink-muted focus:border-accent focus:ring-1 focus:ring-accent disabled:bg-surface-nested" />
          </div>
        </section>

        <section aria-labelledby="intake-documents-heading" className="space-y-4 border-t border-line pt-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 id="intake-documents-heading" className="text-base font-semibold text-ink">Sources</h3>
              <p className="mt-1 text-xs text-ink-muted">Review extracted text before admitting it to the Case.</p>
            </div>
            <UploadControl disabled={isUploadingDocument || isBusy} isUploading={isUploadingDocument} onUpload={onUploadDocument} />
          </div>

          {documents.length === 0 ? (
            <p className="border-y border-line py-5 text-xs text-ink-muted">No documents have been uploaded. A written narrative is enough to begin.</p>
          ) : (
            <div className="border-y border-line">
              <div className="hidden grid-cols-[minmax(0,1.4fr)_minmax(0,0.8fr)_minmax(0,0.7fr)_auto] gap-4 border-b border-line px-3 py-2 text-[10px] font-medium text-ink-muted sm:grid">
                <span>Source</span><span>Extraction</span><span>Admission</span><span>Action</span>
              </div>
              <div className="divide-y divide-line">
                {documents.map((document) => {
                  const extraction = [...(document.extractions ?? [])].sort(
                    (left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime()
                  )[0];
                  const admitted = extraction
                    ? admittedExtractionIds.has(extraction.id) || admittedExtractionIds.has(document.id)
                    : false;
                  return (
                    <article key={document.id} className="grid gap-3 px-3 py-3.5 sm:grid-cols-[minmax(0,1.4fr)_minmax(0,0.8fr)_minmax(0,0.7fr)_auto] sm:items-center sm:gap-4">
                      <p className="break-words text-xs font-semibold text-ink">{document.filename}</p>
                      <p className="text-[11px] text-ink-secondary">{extraction ? extraction.provider : "Not available"}</p>
                      <StatusPill tone={admitted ? "positive" : "attention"}>{document.archived_at ? "Archived" : admitted ? "Admitted" : "Review required"}</StatusPill>
                      {extraction && !admitted && !document.archived_at ? (
                        <button type="button" disabled={admittingExtractionId !== null || isBusy} onClick={() => onAdmitExtraction(document.id, extraction.id)} className="w-fit text-[11px] font-semibold text-accent underline decoration-accent/30 underline-offset-4 disabled:opacity-50">
                          {admittingExtractionId === extraction.id ? "Admitting…" : "Admit text"}
                        </button>
                      ) : (
                        <span className="text-[11px] text-ink-muted">{document.archived_at ? "Archived" : "Included"}</span>
                      )}
                    </article>
                  );
                })}
              </div>
            </div>
          )}
          {onOpenMaterials && <button type="button" onClick={onOpenMaterials} className="text-xs font-medium text-accent underline decoration-accent/30 underline-offset-4">View all materials</button>}
        </section>

        {evidence.length > 0 && (
          <section aria-labelledby="intake-admitted-heading" className="space-y-3 border-t border-line pt-6">
            <div className="flex items-baseline justify-between gap-3">
              <h3 id="intake-admitted-heading" className="text-base font-semibold text-ink">Admitted case information</h3>
              <span className="text-xs text-ink-muted">{evidence.length} source{evidence.length === 1 ? "" : "s"}</span>
            </div>
            <div className="divide-y divide-line border-y border-line">
              {evidence.map((source) => (
                <article key={source.id} className="grid gap-2 py-3.5 sm:grid-cols-[12rem_minmax(0,1fr)] sm:gap-4">
                  <p className="text-xs font-medium text-ink-secondary">{sourceLabel(source.source_kind)}</p>
                  <p className="line-clamp-3 whitespace-pre-wrap text-xs leading-5 text-ink">{source.exact_text}</p>
                </article>
              ))}
            </div>
          </section>
        )}

        <footer className="flex flex-wrap items-center justify-between gap-3 border-t border-line pt-5">
          <p className="text-[11px] text-ink-muted">{hasEvidence ? `${evidence.length} admitted source${evidence.length === 1 ? "" : "s"}` : "No admitted evidence yet"}</p>
          <div className="flex flex-wrap items-center gap-2">
            {analysisResult && onOpenOverview && <button type="button" onClick={onOpenOverview} className="h-9 px-3 text-xs font-medium text-ink-secondary underline decoration-line-strong underline-offset-4">View analysis</button>}
            {onOpenChat && <button type="button" onClick={onOpenChat} className="h-9 rounded-md border border-line px-3 text-xs font-semibold text-ink hover:bg-surface-hover">Open Ask</button>}
            <button type="submit" disabled={!canSubmit} className="h-9 rounded-md bg-primary px-4 text-xs font-semibold text-ivory hover:bg-charcoal-hover disabled:cursor-not-allowed disabled:bg-control-disabled disabled:text-ink-disabled">{isSubmitting ? "Analyzing…" : analysisResult ? "Analyze latest material" : "Analyze case"}</button>
          </div>
        </footer>
      </form>
    </div>
  );
}

function UploadControl({ disabled, isUploading, onUpload }: { disabled: boolean; isUploading: boolean; onUpload: (file: File) => void }) {
  return (
    <label className="inline-flex h-9 cursor-pointer items-center gap-2 rounded-md border border-line bg-surface px-3 text-xs font-semibold text-ink hover:bg-surface-hover has-[:disabled]:cursor-wait has-[:disabled]:opacity-60">
      <Icon name="plus" className="h-3.5 w-3.5" />
      {isUploading ? "Saving…" : "Add files"}
      <input type="file" accept=".pdf,.docx,.png,.jpg,.jpeg" disabled={disabled} onChange={(event) => { const file = event.target.files?.[0]; if (file) onUpload(file); event.currentTarget.value = ""; }} className="sr-only" />
    </label>
  );
}

function intakeStatus({ isSubmitting, isCaseDataLoading, failed, analysisResult, hasEvidence }: { isSubmitting: boolean; isCaseDataLoading: boolean; failed: boolean; analysisResult: CaseAnalysisResultRead | null; hasEvidence: boolean }): string {
  if (isSubmitting) return "Analysis in progress";
  if (isCaseDataLoading) return "Loading case material";
  if (failed) return "Analysis failed";
  if (analysisResult?.freshness === "stale") return "New material needs analysis";
  if (analysisResult) return "Analysis available";
  return hasEvidence ? "Ready for analysis" : "Add case material";
}

function sourceLabel(kind: string): string {
  if (kind === "reviewed_document") return "Reviewed document";
  if (kind === "clarification_answer" || kind === "followup_answer") return "Clarification answer";
  if (kind === "explicit_chat_addition") return "Added case information";
  return "Case narrative";
}
