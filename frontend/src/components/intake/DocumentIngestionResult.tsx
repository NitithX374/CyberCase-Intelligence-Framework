import type {
  DocumentBoundingBox,
  DocumentPagePreview,
  DocumentRegionPreview,
  IngestedDocumentPreview,
} from "@/lib/document-ingestion";
import { StatusPill } from "@/components/common/StatusPill";
import {
  buildCaseNarrativeDraft,
  type CaseNarrativeDraft,
} from "@/lib/case-narrative-document";

function formatBox(box: DocumentBoundingBox | null): string {
  if (!box) return "No bounding box";
  return [box.x0, box.y0, box.x1, box.y1]
    .map((value) => Math.round(value))
    .join(", ");
}

function RegionResult({ region }: { region: DocumentRegionPreview }) {
  return (
    <article className="space-y-3 rounded-xl border border-line bg-canvas/55 p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <span className="section-eyebrow">Document region</span>
          <StatusPill tone={region.warning ? "attention" : "neutral"}>
            {region.region_type}
          </StatusPill>
        </div>
        <span className="text-[10px] text-ink-muted">
          {region.text ? "Text available" : "No text produced"}
        </span>
      </div>

      {region.text ? (
        <p className="whitespace-pre-wrap border-l-2 border-evidence/35 pl-3 text-xs leading-relaxed text-ink">
          {region.text}
        </p>
      ) : (
        <p className="text-xs italic text-ink-muted">No transcription produced.</p>
      )}

      {region.warning && (
        <p className="rounded-lg border border-unresolved/30 bg-unresolved/5 p-2.5 text-[11px] leading-relaxed text-unresolved">
          {region.warning}
        </p>
      )}

      <details className="group border-t border-line/70 pt-2.5">
        <summary className="flex cursor-pointer list-none items-center justify-between gap-2 text-[11px] font-bold text-ink outline-none marker:hidden focus-visible:ring-2 focus-visible:ring-primary">
          <span>Technical recognition details</span>
          <span className="text-ink-muted transition-transform duration-150 group-open:rotate-180">⌄</span>
        </summary>
        <dl className="mt-2 grid gap-1.5 text-[10px] leading-relaxed text-ink-secondary sm:grid-cols-2">
          <div>
            <dt className="font-bold text-ink">Region</dt>
            <dd className="font-mono">{region.region_id}</dd>
          </div>
          <div>
            <dt className="font-bold text-ink">Recognition</dt>
            <dd>{region.recognition_method} · {region.recognizer}</dd>
          </div>
          <div>
            <dt className="font-bold text-ink">Verification</dt>
            <dd>{region.verification_status}</dd>
          </div>
          <div>
            <dt className="font-bold text-ink">Confidence</dt>
            <dd>{region.confidence === null ? "not reported" : `${Math.round(region.confidence * 100)}%`}</dd>
          </div>
          <div className="sm:col-span-2">
            <dt className="font-bold text-ink">Bounding box</dt>
            <dd className="font-mono">[{formatBox(region.bbox)}]</dd>
          </div>
        </dl>
      </details>

      {region.generated_contents.map((content, index) => (
        <div
          key={`${region.region_id}-generated-${index}`}
          className="rounded-lg border border-dashed border-line p-2 text-[11px] leading-relaxed text-ink-muted"
        >
          Non-authoritative visual description: {content.text}
        </div>
      ))}
    </article>
  );
}

function PageResult({ page }: { page: DocumentPagePreview }) {
  const summary = page.routing_summary;
  return (
    <section className="space-y-3 rounded-xl border border-line bg-surface p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-xs font-extrabold text-ink">Page {page.page_number}</h3>
        <details className="group">
          <summary className="cursor-pointer list-none text-[10px] font-bold text-ink-muted outline-none marker:hidden focus-visible:ring-2 focus-visible:ring-primary">
            Routing details <span className="transition-transform group-open:rotate-180">⌄</span>
          </summary>
          <p className="mt-2 text-right font-mono text-[10px] leading-relaxed text-ink-muted">
            Native {summary.native} · OCR {summary.ocr} · HTR {summary.htr} (off) · Unified {summary.unified} · Mixed {summary.mixed} · Unknown {summary.unknown}
          </p>
        </details>
      </div>
      <div className="space-y-2">{page.regions.map((region) => <RegionResult key={region.region_id} region={region} />)}</div>
    </section>
  );
}

export function DocumentIngestionResult({
  result,
  onUseAsNarrative,
}: {
  result: IngestedDocumentPreview;
  onUseAsNarrative?: (draft: CaseNarrativeDraft) => void;
}) {
  return (
    <div className="space-y-4 border-t border-line pt-5" aria-live="polite">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-sm font-extrabold text-ink">{result.filename}</p>
          <p className="mt-1 text-[10px] text-ink-muted">{result.pages.length} page(s) · Review before use</p>
        </div>
      </div>

      {result.warnings.length > 0 && (
        <div className="rounded-xl border border-unresolved/30 bg-unresolved/5 p-3 text-[11px] leading-relaxed text-unresolved">
          <p className="font-bold">Review warnings</p>
          <ul className="mt-1 list-disc space-y-1 pl-4">
            {result.warnings.map((warning, index) => <li key={`${index}-${warning}`}>{warning}</li>)}
          </ul>
        </div>
      )}

      {onUseAsNarrative && result.full_text.trim() && (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-evidence/25 bg-evidence/5 p-3.5">
          <p className="max-w-xl text-[11px] leading-relaxed text-ink-secondary">
            Review the merged text against the source document. Using it fills the editable narrative; analysis starts only after you submit the case.
          </p>
          <button
            type="button"
            onClick={() => onUseAsNarrative(buildCaseNarrativeDraft(result))}
            className="btn-primary inline-flex min-h-9 items-center rounded-lg"
          >
            Use merged text as case narrative
          </button>
        </div>
      )}

      <div className="space-y-3">{result.pages.map((page) => <PageResult key={page.page_number} page={page} />)}</div>
      <details className="rounded-xl border border-line bg-surface p-3.5">
        <summary className="cursor-pointer text-xs font-bold text-ink outline-none focus-visible:ring-2 focus-visible:ring-primary">
          Merged document text
        </summary>
        <pre className="mt-3 max-h-72 overflow-auto whitespace-pre-wrap border-t border-line pt-3 font-sans text-xs leading-relaxed text-ink">
          {result.full_text || "No authoritative transcription was produced."}
        </pre>
      </details>
    </div>
  );
}
