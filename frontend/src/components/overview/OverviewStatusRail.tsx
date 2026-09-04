import type { PersistedChatMessage } from "@/lib/api";
import type { CaseOverviewData } from "@/lib/case-overview-contracts";
import { caseOverviewMetadata } from "@/lib/case-overview";

export function OverviewStatusRail({ messages, overview }: {
  messages: PersistedChatMessage[];
  overview: CaseOverviewData;
}) {
  const metadata = caseOverviewMetadata(messages, overview);
  return (
    <div className="order-2 min-w-0 space-y-5 lg:order-1">
      <section aria-labelledby="overview-analysis-heading" className="space-y-2">
        <h2 id="overview-analysis-heading" className="text-sm font-semibold text-ink">Analysis</h2>
        {metadata.createdAt && (
          <time dateTime={metadata.createdAt} className="block text-xs leading-5 text-ink-secondary">
            {new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" }).format(new Date(metadata.createdAt))}
          </time>
        )}
        {metadata.hasNewMaterial && (
          <p className="border-l-2 border-unresolved/50 pl-3 text-xs leading-5 text-ink-secondary">New case material was added after this analysis.</p>
        )}
        <details className="text-xs text-ink-secondary">
          <summary className="w-fit cursor-pointer py-1 underline decoration-line-strong underline-offset-4 focus-visible:ring-2 focus-visible:ring-primary">Analysis record</summary>
          <dl className="mt-3 space-y-2 border-l border-line pl-3">
            <div className="flex justify-between gap-3"><dt>Analysis kind</dt><dd>Case overview</dd></div>
            {overview.contractVersion && <div className="flex justify-between gap-3"><dt>Format</dt><dd>{overview.contractVersion === "v3" ? "v3" : "Legacy"}</dd></div>}
            <div className="flex justify-between gap-3"><dt>Evidence entries cited</dt><dd>{metadata.citedSourceCount}</dd></div>
          </dl>
        </details>
      </section>
      <section aria-labelledby="overview-materials-heading" className="space-y-3 border-t border-line pt-4">
        <h2 id="overview-materials-heading" className="text-sm font-semibold text-ink">Materials</h2>
        <p className="text-xs text-ink-secondary">{metadata.evidenceCount} evidence {metadata.evidenceCount === 1 ? "entry" : "entries"}{metadata.documents.length > 0 && ` · ${metadata.documents.length} ${metadata.documents.length === 1 ? "document" : "documents"}`}</p>
        {metadata.documents.length > 0 && (
          <ul className="space-y-2 text-xs leading-5 text-ink-secondary">
            {metadata.documents.map((document) => <li key={document.id} className="[overflow-wrap:anywhere]">{document.filename}</li>)}
          </ul>
        )}
      </section>
    </div>
  );
}
