"use client";

import { useEffect, useRef, type ReactNode } from "react";
import { useParams, useRouter, useSelectedLayoutSegment } from "next/navigation";
import { useAnalysisAvailability } from "@/features/analysis/queries";
import { useRunCaseAnalysis } from "@/features/analysis/useRunCaseAnalysis";
import { useIsFollowupPending } from "@/features/chat/useCaseChat";
import { casePath } from "@/lib/casePaths";
import { AnalysisMeta } from "./AnalysisMeta";
import { AnalysisProgress } from "./AnalysisProgress";
import { AnalysisQuestionsCard } from "./AnalysisQuestions";
import { AnalysisSummary } from "./AnalysisSummary";
import { analysisSourceIds } from "./analysisRecord";
import { useCaseOverview } from "./useCaseOverview";
import { Icon } from "@/components/icons";
import { EmptyState } from "@/components/EmptyState";

const SECTION_TARGETS: Record<string, string> = {
  findings: "section-findings",
  questions: "section-attention",
};

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

  const hasAnalysis = overview.hasAnalysis;
  useEffect(() => {
    if (!hasAnalysis) return;
    const hash = window.location.hash.slice(1);
    const id = hash || (section ? SECTION_TARGETS[section] : undefined);
    const target = id ? document.getElementById(id) : null;
    const folded = target?.closest("details");
    if (folded) folded.open = true;
    target?.scrollIntoView?.({ block: "start" });
  }, [section, hasAnalysis]);

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

  const flaggedCount = overview.findings.filter(
    (finding) => finding.traceability.semanticSupport === "not_supported",
  ).length;
  const onFactPage =
    section === "timeline" ||
    section === "people" ||
    section === "impact" ||
    section === "technical" ||
    section === "legal";
  const readCount = analysisResult ? analysisSourceIds(analysisResult).length : 0;

  return (
    <section
      ref={panelRef}
      id="workspace-analysis-panel"
      aria-label="Case analysis"
      className="@container flex w-full shrink-0 flex-col gap-7 px-3 pt-5 pb-16 sm:px-6 lg:px-8"
    >
      {isUpdating ? (
        <div className="sheet px-6 py-4">
          <div role="status" className="flex items-center gap-2.5 text-sm font-medium text-ink">
            <Icon name="spinner" className="text-lg text-primary" />
            {isFollowupPending
              ? "Updating the case analysis with your answer…"
              : "Updating the case analysis…"}
          </div>
          <AnalysisProgress caseId={caseId} className="mt-3" />
        </div>
      ) : null}
      {isWaitingForFollowup && !isUpdating && (
        <p role="status" className="sheet px-6 py-4 text-sm text-ink-secondary">
          Answer the follow-up question in Ask. Analysis continues automatically when the answers
          are complete.
        </p>
      )}

      <div className="grid grid-cols-2 gap-5 @min-[56rem]:grid-cols-4">
        <StatCard value={overview.findings.length} label="findings" />
        <StatCard value={flaggedCount} label="to check" strong={flaggedCount > 0} />
        <StatCard value={overview.gaps.length} label="open questions" />
        <StatCard value={readCount} label={readCount === 1 ? "source read" : "sources read"} />
      </div>

      {onFactPage ? (
        children
      ) : (
        <div className="grid items-start gap-5 @min-[58rem]:grid-cols-[minmax(0,1fr)_22.5rem]">
          <div className="min-w-0">{children}</div>
          <div className="flex min-w-0 flex-col gap-5">
            <AnalysisSummary />
            <AnalysisQuestionsCard />
            <AnalysisMeta overview={overview} result={analysisResult} sources={sources ?? []} />
          </div>
        </div>
      )}
    </section>
  );
}

function StatCard({
  value,
  label,
  strong = false,
}: {
  value: number;
  label: string;
  strong?: boolean;
}) {
  return (
    <div className="sheet px-5 py-4">
      <div>
        <p
          className={`text-2xl leading-tight font-bold tabular-nums ${strong ? "text-primary" : "text-ink"}`}
        >
          {value}
        </p>
        <p className="text-sm text-ink-muted">{label}</p>
      </div>
    </div>
  );
}

function AnalysisSkeleton() {
  return (
    <div
      role="status"
      aria-label="Loading analysis"
      className="@container flex w-full flex-col gap-7 px-3 pt-5 pb-16 sm:px-6 lg:px-8"
    >
      <p className="flex items-center gap-2.5 text-sm text-ink-secondary">
        <Icon name="spinner" className="text-lg text-primary" />
        Loading the saved analysis and its sources…
      </p>
      <div aria-hidden="true" className="grid grid-cols-2 gap-5 @min-[56rem]:grid-cols-4">
        {[0, 1, 2, 3].map((index) => (
          <div key={index} className="sheet space-y-2.5 px-5 py-4">
            <span className="shimmer block h-7 w-12 rounded" />
            <span className="shimmer block h-3.5 w-24 rounded" />
          </div>
        ))}
      </div>
      <div
        aria-hidden="true"
        className="grid items-start gap-5 @min-[58rem]:grid-cols-[minmax(0,1fr)_22.5rem]"
      >
        <div className="sheet">
          <div className="card-head">
            <span className="shimmer block h-5 w-32 rounded" />
          </div>
          {[0, 1, 2].map((row) => (
            <div
              key={row}
              className="grid grid-cols-[2.75rem_minmax(0,1fr)] gap-4 border-t border-line px-6 py-5"
            >
              <span className="shimmer block h-9 w-9 rounded-[9px]" />
              <div className="space-y-2.5">
                <span className="shimmer block h-4 w-11/12 rounded" />
                <span className="shimmer block h-4 w-4/6 rounded" />
              </div>
            </div>
          ))}
        </div>
        <div className="sheet space-y-3 px-6 py-5">
          <span className="shimmer block h-5 w-36 rounded" />
          {[96, 88, 92, 74, 85].map((width, index) => (
            <span
              key={index}
              className="shimmer block h-4 rounded"
              style={{ width: `${width}%` }}
            />
          ))}
        </div>
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
      className="sheet mx-auto mt-8 min-h-[420px] w-[calc(100%-1.5rem)] max-w-[56rem] justify-center px-5 py-16 sm:px-8"
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
