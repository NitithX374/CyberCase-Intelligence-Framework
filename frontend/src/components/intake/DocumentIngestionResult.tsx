import type { IngestedDocumentPreview } from "@/lib/document-ingestion";
import { buildCaseNarrativeDraft, type CaseNarrativeDraft } from "@/lib/case-narrative-document";
import { ExtractedTextPreview } from "./ExtractedTextPreview";

export function DocumentIngestionResult({ result, onUseAsNarrative }: {
  result: IngestedDocumentPreview;
  onUseAsNarrative?: (draft: CaseNarrativeDraft) => void;
}) {
  const warnings = [...new Set([
    ...result.warnings,
    ...result.pages.flatMap((page) => page.regions.flatMap((region) => region.warning ? [region.warning] : [])),
  ])];
  return (
    <div className="min-w-0 space-y-4">
      <div>
        <h2 className="text-base font-bold text-ink">Review extracted content</h2>
        <p className="mt-1 break-words text-xs text-ink-secondary">{result.filename} · {result.pages.length} pages</p>
      </div>
      {warnings.length > 0 && (
        <details className="border-l-2 border-line-strong pl-3 text-xs text-ink-secondary">
          <summary className="cursor-pointer py-1 font-semibold">{warnings.length} extraction {warnings.length === 1 ? "warning" : "warnings"} · Review required</summary>
          <ul className="mt-2 max-h-40 list-disc space-y-2 overflow-y-auto pl-4">
            {warnings.map((warning) => <li key={warning}>{warning}</li>)}
          </ul>
        </details>
      )}
      <ExtractedTextPreview text={result.full_text} label="Document extraction" />
      {onUseAsNarrative && result.full_text.trim() && (
        <div className="flex flex-wrap items-center justify-between gap-3 border-t border-line pt-4">
          <p className="max-w-sm text-xs text-ink-secondary">Check the text against the document. Using it replaces the current narrative draft.</p>
          <button type="button" onClick={() => onUseAsNarrative(buildCaseNarrativeDraft(result))} className="btn-secondary min-h-10 rounded-lg">
            Use reviewed text
          </button>
        </div>
      )}
      <details className="border-t border-line pt-3 text-xs text-ink-muted">
        <summary className="cursor-pointer py-1">Raw extraction details</summary>
        <pre className="mt-3 max-h-64 overflow-auto whitespace-pre-wrap break-words rounded border border-line p-3 text-[11px]">{JSON.stringify(result, null, 2)}</pre>
      </details>
    </div>
  );
}
