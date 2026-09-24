"use client";

import { useCallback, useRef, useState } from "react";
import type { CaseAnalysisResultRead, CaseSourceRead } from "@/lib/api";
import type { CaseOverviewData } from "@/features/analysis/types";
import { Icon } from "@/components/icons";
import { useDismiss } from "@/lib/useDismiss";
import { formatDate } from "@/lib/format";

export function AnalysisMeta({
  overview,
  result,
  sources,
  onReanalyze,
}: {
  overview: CaseOverviewData;
  result: CaseAnalysisResultRead | null;
  sources: CaseSourceRead[];
  onReanalyze?: () => void;
}) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const close = useCallback(() => setIsOpen(false), []);
  useDismiss(containerRef, isOpen, close);

  const isStale = result?.freshness === "stale";
  const documentNames = [
    ...new Set(sources.flatMap((source) => (source.filename ? [source.filename] : []))),
  ];
  const citedSourceCount = new Set(
    overview.findings.flatMap((finding) => [
      ...finding.supportingSources.map((source) => source.id),
      ...finding.contradictingSources.map((source) => source.id),
    ]),
  ).size;

  return (
    <div ref={containerRef} className="relative flex items-center gap-2 text-[13px] text-ink-muted">
      <span className={isStale ? "text-unresolved" : undefined}>
        {isStale ? "Out of date" : "Up to date"}
      </span>
      {result && (
        <>
          <span aria-hidden="true">·</span>
          <time dateTime={result.created_at}>{formatDate(result.created_at, "dayTime")}</time>
        </>
      )}
      {onReanalyze && (
        <button
          type="button"
          aria-label="Analyze again"
          title="Analyze again"
          onClick={onReanalyze}
          className="icon-btn h-7 w-7"
        >
          <Icon name="refresh" className="h-4 w-4" />
        </button>
      )}
      <button
        type="button"
        aria-label="Analysis record"
        aria-expanded={isOpen}
        title="Analysis record"
        onClick={() => setIsOpen((open) => !open)}
        className="icon-btn h-7 w-7"
      >
        <Icon name="info" className="h-4 w-4" />
      </button>
      {isOpen && (
        <dl className="absolute right-0 top-9 z-20 w-72 space-y-2 rounded-xl border border-line bg-surface p-4 text-[13px] shadow-lg shadow-black/5">
          <RecordRow label="Completed" value={formatDate(result?.created_at, "full")} />
          <RecordRow
            label="Source revision"
            value={result ? String(result.source_revision) : "Unavailable"}
          />
          <RecordRow label="Sources" value={`${sources.length} · ${citedSourceCount} cited`} />
          {documentNames.length > 0 && (
            <RecordRow label="Documents" value={documentNames.join(", ")} />
          )}
          <RecordRow label="Result" value={result?.id ?? "Unavailable"} mono />
        </dl>
      )}
    </div>
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
    <div className="grid grid-cols-[6.5rem_minmax(0,1fr)] gap-2">
      <dt className="text-ink-muted">{label}</dt>
      <dd className={`break-words text-ink ${mono ? "font-mono text-xs leading-5" : ""}`}>
        {value}
      </dd>
    </div>
  );
}
