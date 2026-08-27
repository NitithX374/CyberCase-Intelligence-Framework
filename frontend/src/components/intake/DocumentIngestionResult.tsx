import type {
  DocumentBoundingBox,
  DocumentPagePreview,
  DocumentRegionPreview,
  IngestedDocumentPreview,
} from "@/lib/document-ingestion";

function formatBox(box: DocumentBoundingBox | null): string {
  if (!box) return "No bounding box";
  return [box.x0, box.y0, box.x1, box.y1]
    .map((value) => Math.round(value))
    .join(", ");
}

function RegionResult({ region }: { region: DocumentRegionPreview }) {
  return (
    <article className="space-y-2 rounded border border-line bg-surface p-3">
      <div className="flex flex-wrap items-center gap-1.5 font-mono text-[10px] uppercase tracking-wide">
        <span className="font-bold text-ink">{region.region_id}</span>
        <span className="rounded bg-surface-nested px-1.5 py-0.5 text-ink-secondary">
          {region.region_type}
        </span>
        <span className="rounded bg-surface-nested px-1.5 py-0.5 text-ink-secondary">
          {region.recognition_method} · {region.recognizer}
        </span>
        <span className="rounded border border-line px-1.5 py-0.5 text-ink-muted">
          {region.verification_status}
        </span>
      </div>
      <p className="font-mono text-[10px] text-ink-muted">
        bbox [{formatBox(region.bbox)}]
      </p>
      {region.text ? (
        <p className="whitespace-pre-wrap text-xs leading-relaxed text-ink">
          {region.text}
        </p>
      ) : (
        <p className="text-xs italic text-ink-muted">No transcription produced.</p>
      )}
      {region.warning && (
        <p className="rounded border border-amber-300 bg-amber-50 p-2 text-[11px] text-amber-900">
          {region.warning}
        </p>
      )}
      {region.generated_contents.map((content, index) => (
        <div
          key={`${region.region_id}-generated-${index}`}
          className="rounded border border-dashed border-line p-2 text-[11px] text-ink-muted"
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
    <section className="space-y-3 rounded-lg border border-line bg-canvas p-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-xs font-bold text-ink">Page {page.page_number}</h3>
        <p className="font-mono text-[10px] text-ink-muted">
          Native {summary.native} · OCR {summary.ocr} · HTR {summary.htr} (off) · Unified{" "}
          {summary.unified} · Mixed {summary.mixed} · Unknown {summary.unknown}
        </p>
      </div>
      <div className="space-y-2">
        {page.regions.map((region) => (
          <RegionResult key={region.region_id} region={region} />
        ))}
      </div>
    </section>
  );
}

export function DocumentIngestionResult({
  result,
}: {
  result: IngestedDocumentPreview;
}) {
  return (
    <div className="space-y-4 border-t border-line pt-4" aria-live="polite">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <p className="text-xs font-bold text-ink">{result.filename}</p>
          <p className="font-mono text-[10px] text-ink-muted">
            {result.extraction_method} · {result.mode} · {result.pages.length} page(s)
          </p>
        </div>
        <span className="rounded border border-line px-2 py-1 font-mono text-[10px] text-ink-secondary">
          PREVIEW ONLY
        </span>
      </div>
      {result.warnings.length > 0 && (
        <div className="rounded border border-amber-300 bg-amber-50 p-3 text-[11px] text-amber-900">
          <p className="font-bold">Review warnings</p>
          <ul className="mt-1 list-disc space-y-1 pl-4">
            {result.warnings.map((warning, index) => (
              <li key={`${index}-${warning}`}>{warning}</li>
            ))}
          </ul>
        </div>
      )}
      <div className="space-y-3">
        {result.pages.map((page) => (
          <PageResult key={page.page_number} page={page} />
        ))}
      </div>
      <details className="rounded border border-line bg-surface p-3">
        <summary className="cursor-pointer text-xs font-bold text-ink">
          Merged document text
        </summary>
        <pre className="mt-3 max-h-72 overflow-auto whitespace-pre-wrap font-sans text-xs leading-relaxed text-ink">
          {result.full_text || "No authoritative transcription was produced."}
        </pre>
      </details>
    </div>
  );
}
