import type { CaseAnalysisResultRead, CaseSourceRead } from "@/lib/api";
import type { CaseOverviewData } from "@/lib/caseOverview/types";

export function OverviewStatusRail({
  overview,
  result,
  sources,
}: {
  overview: CaseOverviewData;
  result: CaseAnalysisResultRead | null;
  sources: CaseSourceRead[];
}) {
  const documentNames = uniqueDocumentNames(sources);
  const citedSourceCount = new Set(
    overview.findings.flatMap((finding) => [
      ...finding.supportingSources.map((source) => source.id),
      ...finding.contradictingSources.map((source) => source.id),
    ]),
  ).size;

  return (
    <section aria-label="Analysis provenance" className="border-y border-line">
      <dl className="grid grid-cols-2 divide-x divide-y divide-line sm:grid-cols-4 sm:divide-y-0">
        <Metric
          label="Analysis state"
          value={freshnessLabel(result)}
          tone={result?.freshness === "stale" ? "attention" : "positive"}
        />
        <Metric label="Completed" value={formatAnalysisDate(result?.created_at)} />
        <Metric
          label="Source revision"
          value={result ? String(result.source_revision) : "Unavailable"}
        />
        <Metric label="Cited sources" value={String(citedSourceCount)} />
      </dl>

      <StaleNotice isStale={result?.freshness === "stale"} />

      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-line px-3 py-2.5 text-[11px] text-ink-muted sm:px-4">
        <p>
          {sources.length} source {sources.length === 1 ? "entry" : "entries"}
          {documentNames.length > 0
            ? ` across ${documentNames.length} ${documentNames.length === 1 ? "document" : "documents"}`
            : ""}
        </p>
        <details className="relative">
          <summary className="cursor-pointer list-none font-medium text-ink-secondary underline decoration-line-strong underline-offset-4 focus-visible:ring-2 focus-visible:ring-accent">
            Analysis record
          </summary>
          <dl className="absolute right-0 top-7 z-20 w-72 space-y-2 border border-line bg-surface p-3 text-[10px] shadow-lg">
            <RecordRow label="Analysis kind" value="Case overview" />
            <RecordRow label="Format" value="Case native" />
            <RecordRow label="Result" value={result?.id ?? "Unavailable"} mono />
            <RecordRow
              label="Sources"
              value={result ? `revision ${result.source_revision}` : "Unavailable"}
              mono
            />
            {documentNames.length > 0 && (
              <RecordRow label="Documents" value={documentNames.join(", ")} />
            )}
          </dl>
        </details>
      </div>
    </section>
  );
}

function Metric({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone?: "positive" | "attention";
}) {
  return (
    <div className="min-w-0 px-3 py-3 sm:px-4">
      <dt className="text-[10px] text-ink-muted">{label}</dt>
      <dd
        className={`mt-1 truncate text-xs font-semibold ${tone === "positive" ? "text-established" : tone === "attention" ? "text-unresolved" : "text-ink"}`}
        title={value}
      >
        {value}
      </dd>
    </div>
  );
}

function StaleNotice({ isStale }: { isStale: boolean }) {
  if (!isStale) return null;
  return (
    <p className="border-t border-line px-3 py-2.5 text-[11px] text-ink-secondary sm:px-4">
      New Case material was added after this analysis.
    </p>
  );
}

function RecordRow({
  label,
  value,
  mono = false,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div className="grid grid-cols-[5rem_minmax(0,1fr)] gap-2">
      <dt className="text-ink-muted">{label}</dt>
      <dd className={`break-words text-ink ${mono ? "font-mono" : ""}`}>{value}</dd>
    </div>
  );
}

function uniqueDocumentNames(entries: CaseSourceRead[]): string[] {
  const names = new Set<string>();
  for (const entry of entries) {
    const filename = String(entry.source_metadata_json?.filename ?? "").trim();
    if (filename) names.add(filename);
  }
  return [...names];
}

function freshnessLabel(result: CaseAnalysisResultRead | null): string {
  if (!result) return "Unavailable";
  if (result.freshness === "current") return "Current";
  if (result.freshness === "stale") return "Older sources";
  return "Unavailable";
}

function formatAnalysisDate(value: string | undefined): string {
  if (!value) return "Unavailable";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Unavailable";
  return new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" }).format(date);
}
