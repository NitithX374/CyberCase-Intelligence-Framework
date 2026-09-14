import { Icon } from "@/components/common/icons";
import type { CaseDocumentRead } from "@/lib/api";

interface MaterialSourceRailProps {
  documents: CaseDocumentRead[];
  selectedDocumentId: string | null;
  admittedExtractionIds: Set<string>;
  isUploading: boolean;
  onSelectDocument: (documentId: string) => void;
  onUploadDocument: (file: File) => void;
}

export function MaterialSourceRail({
  documents,
  selectedDocumentId,
  admittedExtractionIds,
  isUploading,
  onSelectDocument,
  onUploadDocument,
}: MaterialSourceRailProps) {
  return (
    <aside className="flex max-h-48 w-full shrink-0 flex-col border-b border-line bg-sidebar md:max-h-none md:w-60 md:border-r md:border-b-0">
      <header className="flex min-h-12 items-center justify-between border-b border-line px-3">
        <div>
          <h2 className="text-xs font-semibold text-ink">Sources</h2>
          <p className="text-[10px] text-ink-muted">{documents.length} file{documents.length === 1 ? "" : "s"}</p>
        </div>
        <label className="flex h-8 w-8 cursor-pointer items-center justify-center rounded-md text-ink-secondary hover:bg-surface-hover hover:text-ink focus-within:ring-2 focus-within:ring-accent has-[:disabled]:cursor-wait has-[:disabled]:opacity-50">
          <Icon name="plus" className="h-4 w-4" />
          <span className="sr-only">{isUploading ? "Saving file" : "Add files"}</span>
          <input
            type="file"
            accept=".pdf,.docx,.png,.jpg,.jpeg"
            disabled={isUploading}
            aria-label="Add files"
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) onUploadDocument(file);
              event.currentTarget.value = "";
            }}
            className="sr-only"
          />
        </label>
      </header>

      <div className="min-h-0 overflow-auto p-2">
        {documents.length === 0 ? (
          <p className="px-2 py-4 text-[11px] leading-5 text-ink-muted">No source files yet.</p>
        ) : (
          <ul className="space-y-1">
            {documents.map((document) => {
              const extraction = [...(document.extractions ?? [])].sort((left, right) => right.revision - left.revision)[0];
              const admitted = extraction ? admittedExtractionIds.has(extraction.id) : false;
              const selected = document.id === selectedDocumentId;
              return (
                <li key={document.id}>
                  <button
                    type="button"
                    aria-pressed={selected}
                    onClick={() => onSelectDocument(document.id)}
                    className={`w-full rounded-md px-2.5 py-2.5 text-left outline-none focus-visible:ring-2 focus-visible:ring-accent ${
                      selected ? "bg-accent-soft text-ink" : "text-ink-secondary hover:bg-surface-hover hover:text-ink"
                    }`}
                  >
                    <span className="flex items-start gap-2">
                      <Icon name="materials" className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                      <span className="min-w-0 flex-1">
                        <span className="block truncate text-xs font-semibold">{document.filename}</span>
                        <span className="mt-1 flex items-center gap-1.5 text-[10px] text-ink-muted">
                          <span>{formatBytes(document.size_bytes)}</span>
                          <span aria-hidden="true">·</span>
                          <span className={admitted ? "text-established" : ""}>{admitted ? "Admitted" : "Review"}</span>
                        </span>
                      </span>
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </aside>
  );
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
