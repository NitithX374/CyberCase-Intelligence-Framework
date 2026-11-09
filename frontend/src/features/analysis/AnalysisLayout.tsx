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
import { Icon, type IconName } from "@/components/icons";
import { EmptyState } from "@/components/EmptyState";

const SECTION_TARGETS: Record<string, string> = {
  findings: "section-findings",
  details: "section-references",
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
  const onFactPage = section === "timeline" || section === "people" || section === "impact";
  const readCount = analysisResult ? analysisSourceIds(analysisResult).length : 0;

  return (
    <section
      ref={panelRef}
      id="workspace-analysis-panel"
      aria-label="Case analysis"
      className="flex w-full shrink-0 flex-col gap-7 px-3 pt-5 pb-16 sm:px-6 lg:px-8"
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

      <div className="grid grid-cols-2 gap-5 xl:grid-cols-4">
        <StatCard
          icon="findings"
          tone="bg-[#f3ece4] text-[#6b4e2e]"
          value={overview.findings.length}
          label="findings"
        />
        <StatCard
          icon="alert"
          tone="bg-primary-soft text-primary"
          value={flaggedCount}
          label="to check"
          strong={flaggedCount > 0}
        />
        <StatCard
          icon="attention"
          tone="bg-[#efe6df] text-[#3a2a22]"
          value={overview.gaps.length}
          label="open questions"
        />
        <StatCard
          icon="sources"
          tone="bg-linked-soft text-linked"
          value={readCount}
          label={readCount === 1 ? "source read" : "sources read"}
        />
      </div>

      {onFactPage ? (
        children
      ) : (
        <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1fr)_22.5rem]">
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
  icon,
  tone,
  value,
  label,
  strong = false,
}: {
  icon: IconName;
  tone: string;
  value: number;
  label: string;
  strong?: boolean;
}) {
  return (
    <div className="sheet flex items-center gap-4 px-5 py-4">
      <span
        className={`hidden h-12 w-12 shrink-0 items-center justify-center rounded-xl sm:flex ${tone}`}
      >
        <Icon name={icon} className="text-2xl" />
      </span>
      <div>
        <p className={`text-2xl leading-tight font-bold ${strong ? "text-primary" : "text-ink"}`}>
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
