import type { CaseNarrativeDocumentSource } from "@/lib/api";

function confidenceLabel(source: CaseNarrativeDocumentSource): string {
  if (source.confidence_status === "reported" && source.minimum_confidence !== null) {
    return `Lowest reported OCR confidence: ${Math.round(source.minimum_confidence * 100)}%`;
  }
  if (source.confidence_status === "not_applicable") {
    return "Native digital text; OCR confidence is not applicable.";
  }
  return "The OCR provider did not report confidence. Review names, places, dates, and technical terms carefully.";
}

export function CaseNarrativeSourceNotice({
  source,
  onRemove,
}: {
  source: CaseNarrativeDocumentSource;
  onRemove: () => void;
}) {
  return (
    <div className="space-y-2 rounded border border-amber-300 bg-amber-50 p-3 text-[11px] text-amber-950">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <p className="font-bold">Document-derived narrative draft</p>
          <p>
            {source.filename} · {source.page_count} page(s) · {source.verification_status}
          </p>
        </div>
        <button
          type="button"
          onClick={onRemove}
          className="font-semibold underline underline-offset-2 hover:text-amber-700"
        >
          Remove source link
        </button>
      </div>
      <p>{confidenceLabel(source)}</p>
      {source.warnings.length > 0 && (
        <p>
          {source.warnings.length} recognition warning(s) remain. The narrative is editable
          and is not evidence until you review and submit it.
        </p>
      )}
    </div>
  );
}
