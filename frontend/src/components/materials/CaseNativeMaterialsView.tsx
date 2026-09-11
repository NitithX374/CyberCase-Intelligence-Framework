"use client";

import { useMemo } from "react";
import { Icon } from "@/components/common/icons";
import { StatusPill } from "@/components/common/StatusPill";
import type { CaseDocumentRead, EvidenceSourceRead } from "@/lib/api";

interface CaseNativeMaterialsViewProps {
  documents: CaseDocumentRead[];
  evidence: EvidenceSourceRead[];
  isUploading: boolean;
  admittingExtractionId: string | null;
  onUploadDocument: (file: File) => void;
  onAdmitExtraction: (documentId: string, extractionId: string) => void;
  onOpenChat?: () => void;
  onOpenIntake?: () => void;
}

export function CaseNativeMaterialsView({
  documents,
  evidence,
  isUploading,
  admittingExtractionId,
  onUploadDocument,
  onAdmitExtraction,
  onOpenChat,
  onOpenIntake,
}: CaseNativeMaterialsViewProps) {
  const admittedExtractionIds = useMemo(
    () => new Set(evidence.flatMap((source) => source.revisions?.map((revision) => revision.extraction_id).filter(Boolean) ?? [])),
    [evidence],
  );
  const hasMaterials = documents.length > 0 || evidence.length > 0;

  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-y-auto bg-canvas">
      <div className="mx-auto w-full max-w-4xl space-y-7 px-4 py-6 sm:px-7 sm:py-8 lg:px-9">
        <header className="border-b border-line pb-5">
          <p className="section-eyebrow">CASE MATERIALS · ข้อมูลสำนวนคดี</p>
          <div className="mt-1 flex flex-wrap items-center justify-between gap-3">
            <h1 className="text-2xl font-extrabold tracking-[-0.035em] text-ink sm:text-3xl">Saved case material</h1>
            {hasMaterials && <StatusPill>{documents.length + evidence.length} records</StatusPill>}
          </div>
          <p className="mt-2 max-w-2xl text-xs leading-relaxed text-ink-secondary sm:text-sm">
            Documents are stored first, reviewed explicitly, and admitted as immutable evidence revisions before analysis.
          </p>
          <label className="mt-4 inline-flex min-h-10 cursor-pointer items-center gap-2 rounded-lg border border-line bg-surface px-3 text-xs font-bold text-ink hover:border-line-strong hover:bg-surface-hover has-[:disabled]:cursor-wait has-[:disabled]:opacity-60">
            <Icon name="intake" className="h-4 w-4" />
            {isUploading ? "Saving document…" : "Upload document"}
            <input
              type="file"
              accept=".pdf,.docx,.png,.jpg,.jpeg"
              disabled={isUploading}
              onChange={(event) => {
                const file = event.target.files?.[0];
                if (file) onUploadDocument(file);
                event.currentTarget.value = "";
              }}
              className="sr-only"
            />
          </label>
        </header>

        {!hasMaterials ? (
          <EmptyMaterials onOpenIntake={onOpenIntake} />
        ) : (
          <div className="space-y-8">
            {documents.length > 0 && (
              <section aria-labelledby="saved-documents-heading" className="space-y-4">
                <h2 id="saved-documents-heading" className="text-sm font-bold text-ink">Documents and review status</h2>
                <div className="divide-y divide-line border-y border-line">
                  {documents.map((document) => {
                    const extraction = [...(document.extractions ?? [])].sort((left, right) => right.revision - left.revision)[0];
                    const admitted = extraction ? admittedExtractionIds.has(extraction.id) : false;
                    return (
                      <article key={document.id} className="space-y-3 py-4">
                        <div className="flex flex-wrap items-start justify-between gap-3">
                          <div className="min-w-0">
                            <h3 className="break-words text-sm font-semibold text-ink">{document.filename}</h3>
                            <p className="mt-1 text-[11px] text-ink-muted">{formatBytes(document.size_bytes)} · saved {formatDate(document.created_at)}</p>
                          </div>
                          <StatusPill>{document.archived_at ? "Archived" : admitted ? "Admitted" : "Review required"}</StatusPill>
                        </div>
                        {extraction ? (
                          <div className="rounded-lg border border-line bg-surface p-3 text-xs text-ink-secondary">
                            <p>Extraction revision {extraction.revision} · {extraction.provider}</p>
                            {extraction.warnings_json.length > 0 && <p className="mt-1 text-unresolved">Review warnings recorded: {extraction.warnings_json.length}</p>}
                            {!admitted && !document.archived_at && (
                              <button
                                type="button"
                                disabled={admittingExtractionId !== null}
                                onClick={() => onAdmitExtraction(document.id, extraction.id)}
                                className="btn-secondary mt-3 min-h-9 rounded-md disabled:cursor-wait disabled:opacity-60"
                              >
                                {admittingExtractionId === extraction.id ? "Admitting…" : "Admit reviewed text"}
                              </button>
                            )}
                          </div>
                        ) : <p className="text-xs text-critical">No extraction revision is available.</p>}
                      </article>
                    );
                  })}
                </div>
              </section>
            )}

            <section aria-labelledby="admitted-evidence-heading" className="space-y-4">
              <div className="flex flex-wrap items-baseline justify-between gap-3">
                <h2 id="admitted-evidence-heading" className="text-sm font-bold text-ink">Admitted evidence revisions</h2>
                {evidence.length > 0 && <span className="text-xs text-ink-muted">{evidence.length} source{evidence.length === 1 ? "" : "s"}</span>}
              </div>
              {evidence.length === 0 ? (
                <p className="rounded-lg border border-dashed border-line p-5 text-xs leading-relaxed text-ink-muted">No document or narrative has been admitted yet. Review an extraction or add a narrative from Intake.</p>
              ) : (
                <div className="divide-y divide-line border-y border-line">
                  {evidence.map((source) => <EvidenceSourceRow key={source.id} source={source} onOpenChat={onOpenChat} />)}
                </div>
              )}
            </section>
          </div>
        )}
      </div>
    </div>
  );
}

function EvidenceSourceRow({ source, onOpenChat }: { source: EvidenceSourceRead; onOpenChat?: () => void }) {
  const revisions = [...(source.revisions ?? [])].sort((left, right) => right.revision - left.revision);
  return (
    <article className="space-y-3 py-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="break-words text-sm font-semibold text-ink">{sourceLabel(source.source_kind)}</h3>
          <p className="mt-1 break-all text-[10px] font-mono text-ink-muted">Source {source.id}</p>
        </div>
        {source.archived_at && <StatusPill>Archived</StatusPill>}
      </div>
      {revisions.map((revision) => (
        <div key={revision.id} className="border-l-2 border-evidence/35 pl-3 text-xs leading-relaxed text-ink-secondary">
          <p>Revision {revision.revision} · {revision.archived_at ? "archived" : "active"}</p>
          <p className="mt-2 whitespace-pre-wrap break-words">{revision.exact_text}</p>
        </div>
      ))}
      {onOpenChat && <button type="button" onClick={onOpenChat} className="min-h-8 text-[11px] font-semibold text-ink-secondary underline underline-offset-4 hover:text-ink">Ask about this material →</button>}
    </article>
  );
}

function EmptyMaterials({ onOpenIntake }: { onOpenIntake?: () => void }) {
  return (
    <div className="workspace-card p-10 text-center sm:p-12">
      <Icon name="materials" className="mx-auto h-5 w-5 text-ink-secondary" />
      <h2 className="mt-4 text-sm font-extrabold text-ink">No case material has been saved yet.</h2>
      {onOpenIntake && <button type="button" onClick={onOpenIntake} className="btn-primary mt-5 rounded-lg">Go to Case Intake</button>}
    </div>
  );
}

function sourceLabel(kind: string): string {
  if (kind === "reviewed_document") return "Reviewed document";
  if (kind === "clarification_answer") return "Clarification answer";
  if (kind === "explicit_chat_addition") return "Added case information";
  return "Case narrative";
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(value: string): string {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "unknown date" : date.toLocaleDateString("en-GB");
}
