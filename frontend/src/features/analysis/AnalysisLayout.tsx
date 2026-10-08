"use client";

import { useEffect, useRef, type ReactNode } from "react";
import { useParams, useRouter, useSelectedLayoutSegment } from "next/navigation";
import { useAnalysisAvailability } from "@/features/analysis/queries";
import { useRunCaseAnalysis } from "@/features/analysis/useRunCaseAnalysis";
import { useIsFollowupPending } from "@/features/chat/useCaseChat";
import { casePath } from "@/lib/casePaths";
import { AnalysisMeta } from "./AnalysisMeta";
import { AnalysisNav } from "./AnalysisNav";
import { AnalysisProgress } from "./AnalysisProgress";
import { AnalysisPipeline } from "./AnalysisPipeline";
import { useCaseOverview } from "./useCaseOverview";
import { Icon } from "@/components/icons";
import { EmptyState } from "@/components/EmptyState";

export function AnalysisLayout({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { caseId } = useParams<{ caseId: string }>();
  const runAnalysis = useRunCaseAnalysis(caseId);
  const { analysisQuery, sourcesQuery, analysisResult, sources, overview } =
    useCaseOverview(caseId);
  const { isUpdating, isWaitingForFollowup, canAnalyze } = useAnalysisAvailability(caseId);
  const isFollowupPending = useIsFollowupPending(caseId);
  const section = useSelectedLayoutSegment();
  const panelRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    const hash = window.location.hash.slice(1);
    const target = hash ? document.getElementById(hash) : null;
    (target ?? panelRef.current)?.scrollIntoView?.({ block: "start" });
  }, [section]);

  const navigateToSources = () => router.push(casePath(caseId, "sources"));

  if ((analysisQuery.isLoading && !analysisResult) || (sourcesQuery.isLoading && analysisResult)) {
    return <AnalysisSkeleton />;
  }

  if (analysisQuery.isLoadingError || sourcesQuery.isLoadingError) {
    return (
      <AnalysisState
        title="Analysis could not be loaded"
        description={
          analysisQuery.isLoadingError
            ? "The saved analysis could not be read. Nothing was changed."
            : "The case sources could not be read, so the findings cannot be shown with their sources."
        }
        actionLabel="Try again"
        onAction={() => {
          if (analysisQuery.isLoadingError) void analysisQuery.refetch();
          if (sourcesQuery.isLoadingError) void sourcesQuery.refetch();
        }}
      />
    );
  }

  if (overview.unavailableReason) {
    return (
      <AnalysisState
        title="Analysis unavailable"
        description={overview.unavailableReason}
        actionLabel="Open sources"
        onAction={navigateToSources}
      />
    );
  }

  if (!overview.hasAnalysis && isUpdating) {
    return (
      <AnalysisState
        processing
        title="Analyzing…"
        description={
          isFollowupPending
            ? "Reading the case sources with your answer. This usually takes a few minutes."
            : "Reading the case sources. This usually takes a few minutes."
        }
      >
        <AnalysisProgress caseId={caseId} className="mt-6" />
      </AnalysisState>
    );
  }

  if (!overview.hasAnalysis && isWaitingForFollowup) {
    return (
      <AnalysisState
        title="Waiting for your answer"
        description="Answer the follow-up question in Ask. Analysis continues automatically when the answers are complete."
        actionLabel="Analyze"
        onAction={runAnalysis}
        actionDisabled
      />
    );
  }

  if (!overview.hasAnalysis) {
    const hasSources = Boolean(sources?.length);
    return (
      <AnalysisState
        title="Not analyzed yet"
        description={
          hasSources
            ? "Analyze the case to get a summary, findings and open questions."
            : "Add a narrative or a file, then analyze the case."
        }
        actionLabel={hasSources ? "Analyze" : "Add sources"}
        onAction={hasSources ? runAnalysis : navigateToSources}
        actionDisabled={hasSources && !canAnalyze}
      />
    );
  }

  const isStale = analysisResult?.freshness === "stale";

  return (
    <section
      ref={panelRef}
      id="workspace-analysis-panel"
      aria-label="Case analysis"
      className="flex shrink-0 flex-col bg-surface pb-16"
    >
      <div className="sticky top-0 z-10 bg-surface">
        <div className="mx-auto w-full max-w-[52rem] px-5 pt-4 sm:px-8 sm:pt-5">
          <div className="flex flex-wrap-reverse items-start justify-between gap-x-6 gap-y-1 border-b border-line">
            <AnalysisNav
              caseId={caseId}
              findingCount={overview.findings.length}
              questionCount={overview.gaps.length}
            />
            <div className="pb-3">
              <AnalysisMeta
                overview={overview}
                result={analysisResult}
                sources={sources ?? []}
                onReanalyze={isStale || !canAnalyze ? undefined : runAnalysis}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto w-full max-w-[52rem] px-5 sm:px-8">
        {isUpdating ? (
          <div className="mt-6">
            <div
              role="status"
              className="flex items-center gap-2.5 rounded-lg bg-accent-soft px-3.5 py-2.5 text-[13px] text-accent-strong"
            >
              <Icon name="spinner" className="h-4 w-4 shrink-0" />
              <span className="font-medium">
                {isFollowupPending
                  ? "Updating the case analysis with your answer…"
                  : "Updating the case analysis…"}
              </span>
            </div>
            <AnalysisProgress caseId={caseId} className="mt-3 px-3.5" />
          </div>
        ) : null}
        {isWaitingForFollowup && !isUpdating && (
          <p
            role="status"
            className="mt-6 rounded-lg bg-surface-nested px-3.5 py-2.5 text-[13px] leading-6 text-ink-secondary"
          >
            Answer the follow-up question in Ask. Analysis continues automatically when the answers
            are complete.
          </p>
        )}
        {isStale && !isUpdating && (
          <div
            role="alert"
            className="mt-6 flex flex-wrap items-center justify-between gap-x-4 gap-y-2 border-y border-line py-2 text-[13px] text-ink"
          >
            <p>
              <span className="font-semibold">Analysis is based on older sources.</span>{" "}
              <span className="text-ink-secondary">New material was added since.</span>
            </p>
            <button
              type="button"
              onClick={runAnalysis}
              disabled={!canAnalyze}
              className="btn-secondary h-8 px-3"
            >
              Analyze latest sources
            </button>
          </div>
        )}
        {!isUpdating && analysisResult?.trace_json && (
          <AnalysisPipeline trace={analysisResult.trace_json} />
        )}
      </div>

      {children}
    </section>
  );
}

function AnalysisSkeleton() {
  return (
    <div
      role="status"
      aria-label="Loading analysis"
      className="mx-auto w-full max-w-[52rem] space-y-12 px-5 pt-8 sm:px-8 sm:pt-12"
    >
      <div className="space-y-4">
        <div className="h-4 w-24 animate-pulse rounded bg-surface-nested" />
        <div className="h-4 w-full animate-pulse rounded bg-surface-nested" />
        <div className="h-4 w-11/12 animate-pulse rounded bg-surface-nested" />
        <div className="h-4 w-4/6 animate-pulse rounded bg-surface-nested" />
      </div>
      <div className="space-y-4">
        <div className="h-4 w-40 animate-pulse rounded bg-surface-nested" />
        <div className="h-14 w-full animate-pulse rounded bg-surface-nested" />
        <div className="h-14 w-full animate-pulse rounded bg-surface-nested" />
      </div>
    </div>
  );
}

function AnalysisState({
  title,
  description,
  actionLabel,
  onAction,
  actionDisabled,
  processing,
  children,
}: {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  actionDisabled?: boolean;
  processing?: boolean;
  children?: ReactNode;
}) {
  return (
    <EmptyState
      busy={processing}
      title={title}
      description={description}
      className="mx-auto min-h-[420px] w-full max-w-[52rem] justify-center px-5 py-16 sm:px-8"
    >
      {actionLabel && onAction && (
        <button
          type="button"
          onClick={onAction}
          disabled={actionDisabled}
          className="btn-primary mt-5"
        >
          {actionLabel}
        </button>
      )}
      {children}
    </EmptyState>
  );
}
