import type { FormEvent } from "react";
import type { CaseNarrativeDraft } from "@/lib/case-narrative-document";
import type { IngestedDocumentPreview } from "@/lib/document-ingestion";
import { CaseNarrativeSourceNotice } from "./CaseNarrativeSourceNotice";
import { DocumentIngestionResult } from "./DocumentIngestionResult";
import { ExtractedTextPreview } from "./ExtractedTextPreview";

export function IntakeNarrativeForm({ title, description, draft, result, disabled, sourceLinked, onTitle, onDescription, onUseDocument, onRemoveSource, onSubmit }: {
  title: string;
  description: string;
  draft: CaseNarrativeDraft | null;
  result: IngestedDocumentPreview | null;
  disabled: boolean;
  sourceLinked: boolean;
  onTitle: (value: string) => void;
  onDescription: (value: string) => void;
  onUseDocument: (draft: CaseNarrativeDraft) => void;
  onRemoveSource: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  const needsImport = result && result.document_id !== draft?.source.document_id;
  const narrativeInput = (
    <div className="space-y-2">
      <label htmlFor="case-description-input" className="text-xs font-semibold text-ink">Case narrative</label>
      <textarea id="case-description-input" rows={8} value={description} onChange={(event) => onDescription(event.target.value)} required disabled={disabled}
        placeholder="Describe what happened, who was involved, and any dates or details available in the case material."
        className="block max-h-80 min-h-48 w-full resize-y rounded-lg border border-line bg-canvas p-4 text-sm leading-7 text-ink outline-none placeholder:text-ink-muted focus:border-ink disabled:bg-surface-nested" />
    </div>
  );
  return (
    <form id="intake-narrative-form" onSubmit={onSubmit} className="workspace-card min-w-0 space-y-5 p-5 sm:p-6">
      <div>
        <h2 className="text-base font-bold text-ink">Case information</h2>
        <p className="mt-1 text-xs text-ink-secondary">Review a document or write a narrative before starting analysis.</p>
      </div>
      <div className="space-y-2">
        <label htmlFor="case-title-input" className="text-xs font-semibold text-ink">Case title <span className="font-normal text-ink-muted">· Optional</span></label>
        <input id="case-title-input" value={title} onChange={(event) => onTitle(event.target.value)} disabled={disabled} placeholder="A short name for this case"
          className="w-full rounded-lg border border-line bg-canvas px-3 py-2.5 text-sm outline-none focus:border-ink" />
      </div>
      {needsImport ? (
        <>
          <DocumentIngestionResult result={result} onUseAsNarrative={disabled ? undefined : onUseDocument} />
          <details className="border-t border-line pt-3">
            <summary className="cursor-pointer text-xs text-ink-secondary">Manual narrative draft</summary>
            <div className="mt-3">{narrativeInput}</div>
          </details>
        </>
      ) : draft ? (
        <>
          <ExtractedTextPreview text={description} label="Reviewed narrative" onEdit={disabled ? undefined : onDescription} />
          {sourceLinked && <CaseNarrativeSourceNotice source={draft.source} onRemove={onRemoveSource} />}
        </>
      ) : narrativeInput}
    </form>
  );
}
