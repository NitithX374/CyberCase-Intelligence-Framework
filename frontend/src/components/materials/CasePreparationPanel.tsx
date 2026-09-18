"use client";

import { useEffect, useState, type FormEvent } from "react";
import { StatusPill } from "@/components/common/StatusPill";
import type {
  CaseAnalysisResultRead,
  CaseIntakeSubmission,
  CaseRead,
  CaseSourceRead,
} from "@/lib/api";
import { readAccountValue, writeAccountValue } from "@/lib/account-storage";

interface CasePreparationPanelProps {
  caseId: string;
  evidence: CaseSourceRead[];
  caseStatus: CaseRead["status"] | null;
  processingStatus: CaseRead["processing_status"] | null;
  analysisResult: CaseAnalysisResultRead | null;
  isSubmitting: boolean;
  isCaseDataLoading: boolean;
  isUploading: boolean;
  error?: string | null;
  onSubmitCase: (data: CaseIntakeSubmission) => void;
}

export function CasePreparationPanel({
  caseId,
  evidence,
  caseStatus,
  processingStatus,
  analysisResult,
  isSubmitting,
  isCaseDataLoading,
  isUploading,
  error,
  onSubmitCase,
}: CasePreparationPanelProps) {
  const [title, setTitle] = useAccountState(`case-intake:${caseId}:title`, "");
  const [description, setDescription] = useAccountState(`case-intake:${caseId}:description`, "");
  const hasEvidence = evidence.length > 0;
  const isBusy = isSubmitting || isCaseDataLoading || isUploading;
  const isRunActive = processingStatus === "queued" || processingStatus === "running";
  const hasFailed = caseStatus === "failed" || processingStatus === "failed";
  const canSubmit = !isBusy && Boolean(description.trim() || hasEvidence);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!canSubmit) return;
    onSubmitCase({ title: title.trim() || undefined, description: description.trim() });
  };

  const status = preparationStatus({
    isSubmitting,
    isCaseDataLoading,
    failed: hasFailed,
    processingStatus,
    analysisResult,
    hasEvidence,
  });

  return (
    <section aria-labelledby="case-materials-heading" className="shrink-0 border-b border-line bg-surface">
      <form id="case-materials-form" onSubmit={handleSubmit} className="mx-auto w-full max-w-6xl px-5 py-5 sm:px-8 sm:py-6 lg:px-10">
        <header className="flex flex-wrap items-start justify-between gap-4">
          <div className="min-w-0">
            <h1 id="case-materials-heading" className="text-xl font-semibold tracking-[-0.02em] text-ink sm:text-2xl">Case materials</h1>
            <p className="mt-1.5 max-w-2xl text-xs leading-5 text-ink-muted">Add case information and source files before running the next analysis.</p>
          </div>
          <div className="flex shrink-0 items-center gap-3">
            <div role="status" aria-live="polite" className="hidden items-center gap-2 text-xs font-medium text-ink-secondary sm:flex">
              <span className={`h-1.5 w-1.5 rounded-full ${hasFailed ? "bg-critical" : isBusy || isRunActive ? "bg-evidence" : "bg-established"}`} />
              {status}
            </div>
            <button type="submit" disabled={!canSubmit} className="inline-flex h-9 items-center gap-2 rounded-md bg-primary px-3.5 text-xs font-semibold text-ivory hover:bg-charcoal-hover focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:bg-control-disabled disabled:text-ink-disabled">
              {isSubmitting && <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-ivory/30 border-t-ivory" />}
              {isSubmitting ? "Analyzing…" : analysisResult ? "Analyze latest material" : "Analyze case"}
            </button>
          </div>
        </header>

        {error && <p role="alert" className="mt-4 border-l-2 border-critical px-3 py-2 text-xs text-ink">{error}</p>}

        <div className="mt-5 grid gap-4 border-t border-line pt-5 md:grid-cols-[12rem_minmax(0,1fr)] md:gap-x-5">
          <label htmlFor="case-materials-title-input" className="pt-2 text-xs font-medium text-ink-secondary">Case title <span className="text-ink-muted">(optional)</span></label>
          <input id="case-materials-title-input" value={title} onChange={(event) => setTitle(event.target.value)} disabled={isBusy} placeholder="A short name for this case" className="w-full border-b border-line bg-transparent px-0 py-2 text-sm text-ink outline-none placeholder:text-ink-muted focus:border-accent disabled:text-ink-disabled" />

          <label htmlFor="case-materials-description-input" className="pt-2 text-xs font-medium text-ink-secondary">Case information</label>
          <textarea id="case-materials-description-input" rows={3} value={description} onChange={(event) => setDescription(event.target.value)} disabled={isBusy} placeholder="Describe what happened, who was involved, and the dates or details available in the case material." className="block min-h-24 w-full resize-y rounded-md border border-line bg-surface p-3 text-sm leading-6 text-ink outline-none placeholder:text-ink-muted focus:border-accent focus:ring-1 focus:ring-accent disabled:bg-surface-nested" />
        </div>

        <div className="mt-5 border-t border-line pt-4">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <div>
              <h2 className="text-xs font-semibold text-ink">Received case information</h2>
              <p className="mt-1 text-[11px] text-ink-muted">Narrative and follow-up answers already admitted as Case evidence.</p>
            </div>
            <span className="text-[11px] text-ink-muted">{evidence.length} source{evidence.length === 1 ? "" : "s"}</span>
          </div>
          {evidence.length > 0 ? (
            <div className="mt-3 max-h-28 divide-y divide-line overflow-y-auto border-y border-line">
              {evidence.map((source) => (
                <article key={source.id} className="grid gap-1 py-2.5 sm:grid-cols-[12rem_minmax(0,1fr)] sm:gap-4">
                  <p className="text-[11px] font-medium text-ink-secondary">{sourceLabel(source.source_kind)}</p>
                  <p className="line-clamp-2 whitespace-pre-wrap text-xs leading-5 text-ink">{source.exact_text}</p>
                </article>
              ))}
            </div>
          ) : (
            <p className="mt-3 border-y border-line py-3 text-xs text-ink-muted">Add a narrative or upload a source file to begin.</p>
          )}
        </div>

        <div className="mt-4 flex items-center justify-between gap-3 text-[11px] text-ink-muted sm:hidden">
          <StatusPill tone={hasFailed ? "critical" : isBusy || isRunActive ? "evidence" : "neutral"}>{status}</StatusPill>
          <span>{isSubmitting || isRunActive ? "Analysis is running" : hasEvidence ? "Ready to analyze" : "Add case material"}</span>
        </div>
      </form>
    </section>
  );
}

function preparationStatus({
  isSubmitting,
  isCaseDataLoading,
  failed,
  processingStatus,
  analysisResult,
  hasEvidence,
}: {
  isSubmitting: boolean;
  isCaseDataLoading: boolean;
  failed: boolean;
  processingStatus: CaseRead["processing_status"] | null;
  analysisResult: CaseAnalysisResultRead | null;
  hasEvidence: boolean;
}): string {
  if (isSubmitting) return "Analysis in progress";
  if (isCaseDataLoading) return "Loading case material";
  if (failed) return "Analysis failed";
  if (processingStatus === "queued" || processingStatus === "running") return "Analysis in progress";
  if (analysisResult?.freshness === "stale") return "New material needs analysis";
  if (analysisResult) return "Analysis available";
  return hasEvidence ? "Ready for analysis" : "Add case material";
}

function sourceLabel(kind: string): string {
  if (kind === "document") return "Document";
  if (kind === "followup_answer") return "Follow-up answer";
  return "Case narrative";
}

function useAccountState<T>(key: string, initial: T) {
  const [value, setValue] = useState<T>(() => {
    const saved = readAccountValue(key);
    return saved === null ? initial : JSON.parse(saved) as T;
  });

  useEffect(() => {
    writeAccountValue(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue] as const;
}
