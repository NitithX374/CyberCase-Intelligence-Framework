"use client";

import { useAccountState } from "@/hooks/use-account-state";
import { useMemo, type FormEvent } from "react";
import type {
  CaseAnalysisResultRead,
  CaseDocumentRead,
  CaseIntakeSubmission,
  CaseRunRead,
  EvidenceSourceRead,
} from "@/lib/api";
import { Icon } from "@/components/common/icons";
import { StatusPill } from "@/components/common/StatusPill";

interface CaseFirstIntakeViewProps {
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

export function CaseFirstIntakeView({
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
}: CaseFirstIntakeViewProps) {
  const [title, setTitle] = useAccountState(`case-intake:${caseId}:title`, "");
  const [description, setDescription] = useAccountState(`case-intake:${caseId}:description`, "");
  const admittedExtractionIds = useMemo(
    () => new Set(evidence.flatMap((source) => source.revisions?.map((revision) => revision.extraction_id).filter(Boolean) ?? [])),
    [evidence],
  );
  const hasEvidence = evidence.length > 0;
  const isFailed = run?.status === "failed";
  const isBusy = isSubmitting || isCaseDataLoading;
  const canSubmit = !isBusy && Boolean(description.trim() || hasEvidence);
  const status = isSubmitting
    ? "Analysis in progress"
    : isCaseDataLoading
      ? "Loading case material"
      : isFailed
        ? "Analysis failed"
        : analysisResult
          ? analysisResult.freshness === "stale" ? "New material needs analysis" : "Analysis available"
          : hasEvidence ? "Ready for analysis" : "Add case material";

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!canSubmit) return;
    onSubmitCase({ title: title.trim() || undefined, description: description.trim() });
  };

  return (
    <div id="workspace-intake-panel" role="region" aria-label="Case Intake" className="flex min-h-0 flex-1 flex-col bg-canvas">
      <div className="min-h-0 flex-1 overflow-y-auto">
        <div className="mx-auto w-full max-w-6xl space-y-6 px-4 py-5 sm:px-7 lg:px-9">
          <header className="space-y-4 border-b border-line pb-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="section-eyebrow">CASE INTAKE</p>
                <h1 className="mt-1 text-xl font-bold tracking-tight text-ink sm:text-2xl">Prepare case analysis</h1>
                <p className="mt-1 text-[11px] text-ink-muted">Case {caseId.slice(0, 8)} · Case-owned workflow</p>
              </div>
              <div role="status" aria-live="polite" className="max-w-sm text-xs leading-relaxed text-ink-secondary">
                <p className="font-semibold text-ink">{status}</p>
                <p className="mt-1">Documents and admitted evidence are stored independently of Chat.</p>
              </div>
            </div>
            {error && <p role="alert" className="border-l-2 border-critical pl-3 text-xs text-ink">{error}</p>}
          </header>

          <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_17rem]">
            <form id="case-first-intake-form" onSubmit={handleSubmit} className="workspace-card min-w-0 space-y-5 p-5 sm:p-6">
              <div>
                <h2 className="text-base font-bold text-ink">Case information</h2>
                <p className="mt-1 text-xs text-ink-secondary">Add a narrative, or analyze the evidence already admitted to this Case.</p>
              </div>
              <div className="space-y-2">
                <label htmlFor="case-first-title-input" className="text-xs font-semibold text-ink">Case title <span className="font-normal text-ink-muted">· Optional</span></label>
                <input id="case-first-title-input" value={title} onChange={(event) => setTitle(event.target.value)} disabled={isBusy} placeholder="A short name for this case" className="w-full rounded-lg border border-line bg-canvas px-3 py-2.5 text-sm outline-none focus:border-ink disabled:bg-surface-nested" />
              </div>
              <div className="space-y-2">
                <label htmlFor="case-first-description-input" className="text-xs font-semibold text-ink">Case narrative or additional information</label>
                <textarea id="case-first-description-input" rows={9} value={description} onChange={(event) => setDescription(event.target.value)} disabled={isBusy} placeholder="Describe what happened, who was involved, and any dates or details available in the case material." className="block max-h-96 min-h-52 w-full resize-y rounded-lg border border-line bg-canvas p-4 text-sm leading-7 text-ink outline-none placeholder:text-ink-muted focus:border-ink disabled:bg-surface-nested" />
              </div>
              {evidence.length > 0 && (
                <section className="border-t border-line pt-4" aria-labelledby="admitted-intake-heading">
                  <h3 id="admitted-intake-heading" className="text-xs font-semibold text-ink">Currently admitted</h3>
                  <div className="mt-3 space-y-3">
                    {evidence.map((source) => {
                      const revision = [...(source.revisions ?? [])].sort((left, right) => right.revision - left.revision)[0];
                      return revision ? <div key={source.id} className="border-l-2 border-evidence/35 pl-3 text-xs text-ink-secondary"><p>{sourceLabel(source.source_kind)} · revision {revision.revision}</p><p className="mt-1 line-clamp-3 whitespace-pre-wrap">{revision.exact_text}</p></div> : null;
                    })}
                  </div>
                </section>
              )}
            </form>

            <aside className="min-w-0 space-y-4 lg:sticky lg:top-5">
              <h2 className="text-sm font-bold text-ink">Documents</h2>
              <label className="inline-flex min-h-10 w-full cursor-pointer items-center justify-center gap-2 rounded-lg border border-line bg-surface px-3 text-xs font-bold text-ink hover:border-line-strong hover:bg-surface-hover has-[:disabled]:cursor-wait has-[:disabled]:opacity-60">
                <Icon name="intake" className="h-4 w-4" />
                {isUploadingDocument ? "Saving document…" : "Upload document"}
                <input type="file" accept=".pdf,.docx,.png,.jpg,.jpeg" disabled={isUploadingDocument || isBusy} onChange={(event) => { const file = event.target.files?.[0]; if (file) onUploadDocument(file); event.currentTarget.value = ""; }} className="sr-only" />
              </label>
              {documents.length === 0 ? <p className="border-t border-line pt-4 text-xs leading-relaxed text-ink-muted">No saved documents. You can start with a written narrative.</p> : (
                <ul className="divide-y divide-line border-y border-line">
                  {documents.map((document) => {
                    const extraction = [...(document.extractions ?? [])].sort((left, right) => right.revision - left.revision)[0];
                    const admitted = extraction ? admittedExtractionIds.has(extraction.id) : false;
                    return <li key={document.id} className="space-y-2 py-3"><p className="break-words text-xs font-semibold text-ink">{document.filename}</p><p className="text-[11px] text-ink-secondary">{extraction ? `Extraction ${extraction.revision} · ${extraction.provider}` : "No extraction"}</p>{extraction && !admitted && !document.archived_at && <button type="button" disabled={admittingExtractionId !== null || isBusy} onClick={() => onAdmitExtraction(document.id, extraction.id)} className="min-h-8 text-[11px] font-semibold text-ink underline underline-offset-4 disabled:cursor-wait disabled:opacity-60">{admittingExtractionId === extraction.id ? "Admitting…" : "Admit reviewed text"}</button>}<StatusPill>{document.archived_at ? "Archived" : admitted ? "Admitted" : "Review required"}</StatusPill></li>;
                  })}
                </ul>
              )}
              {onOpenMaterials && <button type="button" onClick={onOpenMaterials} className="min-h-8 text-xs text-ink-secondary underline underline-offset-4 hover:text-ink">Open all case materials →</button>}
            </aside>
          </div>
        </div>
      </div>
      <footer className="shrink-0 border-t border-line bg-surface">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-7 lg:px-9">
          <p className="text-[11px] text-ink-muted">{isCaseDataLoading ? "Loading saved case material…" : hasEvidence ? `${evidence.length} admitted source${evidence.length === 1 ? "" : "s"}` : "No admitted evidence yet — add a narrative or admit reviewed text"}</p>
          <div className="flex flex-wrap gap-2">
            {analysisResult && onOpenOverview && <button type="button" onClick={onOpenOverview} className="btn-secondary min-h-10 rounded-lg">View analysis</button>}
            {onOpenChat && <button type="button" onClick={onOpenChat} className="btn-secondary min-h-10 rounded-lg">Open Chat</button>}
            <button type="submit" form="case-first-intake-form" disabled={!canSubmit} className="btn-primary min-h-10 rounded-lg disabled:cursor-not-allowed">{isSubmitting ? "Analyzing case…" : analysisResult ? "Analyze latest material" : "Analyze case"} →</button>
          </div>
        </div>
      </footer>
    </div>
  );
}

function sourceLabel(kind: string): string {
  if (kind === "reviewed_document") return "Reviewed document";
  if (kind === "clarification_answer") return "Clarification answer";
  if (kind === "explicit_chat_addition") return "Added case information";
  return "Case narrative";
}
