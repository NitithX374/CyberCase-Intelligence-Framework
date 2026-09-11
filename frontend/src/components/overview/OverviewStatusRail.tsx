import type { CaseAnalysisResultRead, CaseEvidenceSnapshotRead, CaseRunRead, PersistedChatMessage } from "@/lib/api";
import type { CaseOverviewData } from "@/lib/case-overview-contracts";
import { caseOverviewMetadata } from "@/lib/case-overview";

export function OverviewStatusRail({
  messages,
  overview,
  nativeAnalysisResult,
  nativeEvidenceSnapshot,
  nativeRunStatus,
}: {
  messages: PersistedChatMessage[];
  overview: CaseOverviewData;
  nativeAnalysisResult?: CaseAnalysisResultRead | null;
  nativeEvidenceSnapshot?: CaseEvidenceSnapshotRead | null;
  nativeRunStatus?: CaseRunRead["status"] | null;
}) {
  const nativeMode = nativeAnalysisResult !== undefined || nativeEvidenceSnapshot !== undefined || nativeRunStatus !== undefined;
  if (nativeMode) {
    return <NativeOverviewStatusRail overview={overview} result={nativeAnalysisResult ?? null} snapshot={nativeEvidenceSnapshot ?? null} runStatus={nativeRunStatus ?? null} />;
  }
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

function NativeOverviewStatusRail({
  overview,
  result,
  snapshot,
  runStatus,
}: {
  overview: CaseOverviewData;
  result: CaseAnalysisResultRead | null;
  snapshot: CaseEvidenceSnapshotRead | null;
  runStatus: CaseRunRead["status"] | null;
}) {
  const sourceEntries = snapshot?.manifest_json.filter((entry): entry is Record<string, unknown> => Boolean(entry) && typeof entry === "object" && !Array.isArray(entry)) ?? [];
  const documentMap = new Map<string, string>();
  for (const entry of sourceEntries) {
    const id = String(entry.document_id ?? "");
    const filename = String(entry.filename ?? "");
    if (id && filename) documentMap.set(id, filename);
  }
  const documents = [...documentMap.entries()];
  const citedSourceCount = new Set(overview.findings.flatMap((finding) => [...finding.supportingSources, ...finding.contradictingSources].map((source) => source.id))).size;
  return (
    <div className="order-2 min-w-0 space-y-5 lg:order-1">
      <section aria-labelledby="overview-analysis-heading" className="space-y-2">
        <h2 id="overview-analysis-heading" className="text-sm font-semibold text-ink">Analysis</h2>
        {result?.created_at && <time dateTime={result.created_at} className="block text-xs leading-5 text-ink-secondary">{new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" }).format(new Date(result.created_at))}</time>}
        {runStatus === "queued" || runStatus === "running" ? <p className="border-l-2 border-evidence/50 pl-3 text-xs leading-5 text-ink-secondary">A new Case analysis is running. The saved result below remains available.</p> : null}
        {runStatus === "failed" && result ? <p className="border-l-2 border-critical/50 pl-3 text-xs leading-5 text-ink-secondary">The latest Case run failed. The last successful result remains displayed.</p> : null}
        {result?.freshness === "stale" && <p className="border-l-2 border-unresolved/50 pl-3 text-xs leading-5 text-ink-secondary">New case material was added after this analysis.</p>}
        <details className="text-xs text-ink-secondary">
          <summary className="w-fit cursor-pointer py-1 underline decoration-line-strong underline-offset-4 focus-visible:ring-2 focus-visible:ring-primary">Analysis record</summary>
          <dl className="mt-3 space-y-2 border-l border-line pl-3">
            <div className="flex justify-between gap-3"><dt>Analysis kind</dt><dd>Case overview</dd></div>
            <div className="flex justify-between gap-3"><dt>Format</dt><dd>Case native</dd></div>
            {result && <div className="flex justify-between gap-3"><dt>Result</dt><dd className="max-w-[9rem] truncate font-mono">{result.id}</dd></div>}
            {snapshot && <div className="flex justify-between gap-3"><dt>Snapshot</dt><dd className="max-w-[9rem] truncate font-mono">{snapshot.id}</dd></div>}
            <div className="flex justify-between gap-3"><dt>Evidence entries cited</dt><dd>{citedSourceCount}</dd></div>
          </dl>
        </details>
      </section>
      <section aria-labelledby="overview-materials-heading" className="space-y-3 border-t border-line pt-4">
        <h2 id="overview-materials-heading" className="text-sm font-semibold text-ink">Materials</h2>
        <p className="text-xs text-ink-secondary">{sourceEntries.length} evidence {sourceEntries.length === 1 ? "entry" : "entries"}{documents.length > 0 && ` · ${documents.length} ${documents.length === 1 ? "document" : "documents"}`}</p>
        {documents.length > 0 && <ul className="space-y-2 text-xs leading-5 text-ink-secondary">{documents.map(([id, filename]) => <li key={id} className="[overflow-wrap:anywhere]">{filename}</li>)}</ul>}
      </section>
    </div>
  );
}
