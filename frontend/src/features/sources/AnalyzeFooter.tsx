"use client";

import { Icon } from "@/components/icons";
import type { SourcesAnalysis } from "./CaseSourcesView";

export function AnalyzeFooter({
  analysis,
  isUploading,
}: {
  analysis: SourcesAnalysis;
  isUploading: boolean;
}) {
  const { freshness, isRunning, isWaitingForFollowup, canAnalyze, onAnalyze } = analysis;
  if (freshness === "current" && !isRunning && !isWaitingForFollowup) return null;
  const isStale = freshness === "stale";

  return (
    <div className="shrink-0 border-t border-line p-3">
      {isWaitingForFollowup && !isRunning && (
        <p className="mb-2.5 px-1 text-xs leading-5 text-ink-secondary">
          Answer the follow-up question in Ask to continue automatically.
        </p>
      )}
      {isStale && !isRunning && (
        <p className="mb-2.5 flex items-center gap-2 px-1 text-xs text-ink-secondary">
          Sources changed since the last analysis
        </p>
      )}
      <button
        type="button"
        onClick={onAnalyze}
        disabled={!canAnalyze || isRunning || isUploading}
        className="btn-primary w-full"
      >
        {isRunning && <Icon name="spinner" className="h-4 w-4" />}
        {isRunning ? "Analyzing…" : isStale ? "Analyze latest" : "Analyze"}
      </button>
    </div>
  );
}
