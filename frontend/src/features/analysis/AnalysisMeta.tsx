"use client";

import { useCallback, useRef, useState } from "react";
import type { CaseAnalysisResultRead, CaseSourceRead } from "@/lib/api/types";
import type { CaseOverviewData } from "@/features/analysis/types";
import { Icon } from "@/components/icons";
import { useDismiss } from "@/lib/useDismiss";
import { formatDate } from "@/lib/format";
import { analysisFollowups, analysisSourceIds } from "./analysisRecord";

export function AnalysisMeta({
  overview,
  result,
  sources,
}: {
  overview: CaseOverviewData;
  result: CaseAnalysisResultRead | null;
  sources: CaseSourceRead[];
}) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLElement | null>(null);
  const close = useCallback(() => setIsOpen(false), []);
  useDismiss(containerRef, isOpen, close);

  const isStale = result?.freshness === "stale";
  const readIds = new Set(result ? analysisSourceIds(result) : []);
  const readCount = readIds.size + (result ? analysisFollowups(result).length : 0);
  const documentNames = [
    ...new Set(
      sources.flatMap((source) =>
        source.filename && readIds.has(source.id) ? [source.filename] : [],
      ),
    ),
  ];
  const citedSourceCount = new Set(
    overview.findings.flatMap((finding) => [
      ...finding.supportingSources.map((source) => source.id),
      ...finding.contradictingSources.map((source) => source.id),
    ]),
  ).size;

  return (
    <section ref={containerRef} aria-labelledby="analysis-record-heading" className="sheet min-w-0">
      <div className="card-head">
        <h2
          id="analysis-record-heading"
          className="flex flex-1 items-center gap-2.5 text-lg font-semibold text-ink"
        >
          <Icon name="timeline" className="text-xl text-primary" />
          Last analysis
        </h2>
        <span className={isStale ? "badge-check" : "badge-linked"}>
          {isStale ? "Out of date" : "Up to date"}
        </span>
      </div>
      <div className="flex flex-col gap-1 px-6 py-4 text-sm text-ink-secondary">
        {result && (
          <span>
            Analyzed{" "}
            <time dateTime={result.created_at}>{formatDate(result.created_at, "dayTime")}</time>
          </span>
        )}
        <button
          type="button"
          aria-expanded={isOpen}
          onClick={() => setIsOpen((open) => !open)}
          className="mt-1 inline-flex min-h-9 items-center gap-1 self-start rounded-lg font-semibold text-primary"
        >
          Analysis record
          <Icon
            name="chevron"
            className={`h-4 w-4 transition-transform ${isOpen ? "rotate-180" : ""}`}
          />
        </button>
        {isOpen && (
          <dl className="mt-1 space-y-2 rounded-lg bg-surface-nested p-4 text-sm text-ink">
            <RecordRow label="Completed" value={formatDate(result?.created_at, "full")} />
            <RecordRow
              label="Source revision"
              value={result ? String(result.source_revision) : "Unavailable"}
            />
            <RecordRow label="Sources" value={`${readCount} · ${citedSourceCount} cited`} />
            {documentNames.length > 0 && (
              <RecordRow label="Documents" value={documentNames.join(", ")} />
            )}
            <RecordRow label="Result" value={result?.id ?? "Unavailable"} mono />
          </dl>
        )}
      </div>
    </section>
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
    <div className="grid gap-0.5">
      <dt className="text-ink-muted">{label}</dt>
      <dd className={`break-words text-ink ${mono ? "font-mono text-xs leading-5" : ""}`}>
        {value}
      </dd>
    </div>
  );
}
