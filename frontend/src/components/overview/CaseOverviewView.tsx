"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import type { CaseGap, SourceMessageRef } from "@/lib/caseOverview/types";
import { buildCaseOverview } from "@/lib/caseOverview";
import { detectResponseLanguage } from "@/lib/api";
import {
  useCase,
  useCaseAnalysis,
  useCaseSources,
  useStartCaseAnalysis,
} from "@/hooks/useCaseQueries";
import { casePath } from "@/lib/workspaceRoutes";
import { CaseFindingsSection } from "./CaseFindingsSection";
import { SourceDrawer } from "@/components/sources/SourceDrawer";
import { OverviewStatusRail } from "./OverviewStatusRail";
import { ChatMessageMarkdown } from "@/components/chat/ChatMessageMarkdown";
import { WorkspaceSectionHeader } from "@/components/common/WorkspaceSectionHeader";
import { Icon } from "@/components/common/icons";
import { useWorkspaceActivity } from "@/components/layout/WorkspaceActivityContext";

interface CaseOverviewViewProps {
  caseId: string | null;
}

export function CaseOverviewView({ caseId }: CaseOverviewViewProps) {
  const router = useRouter();

  const caseQuery = useCase(caseId);
  const activeCase = caseQuery.data ?? null;
  const analysisQuery = useCaseAnalysis(caseId);
  const sourcesQuery = useCaseSources(caseId);

  const startAnalysisMutation = useStartCaseAnalysis(caseId);

  const analysisResult = analysisQuery.data ?? null;
  const { isFollowupPending } = useWorkspaceActivity();
  const sources = useMemo(() => sourcesQuery.data ?? [], [sourcesQuery.data]);
  const caseTitle = activeCase?.title || "New case";

  const [activeSource, setActiveSource] = useState<{
    sourceRef: SourceMessageRef;
    anchorElement: HTMLElement;
    sourceKey: string;
    citationRole?: "supporting" | "conflicting";
  } | null>(null);
  const [overviewTab, setOverviewTab] = useState<"findings" | "questions">("findings");
  const overview = useMemo(
    () => buildCaseOverview(analysisResult, sources, null),
    [analysisResult, sources],
  );

  const navigateToSources = () => {
    if (caseId) router.push(casePath(caseId, "sources"));
  };
  const scrollToReport = () => {
    document
      .getElementById("workspace-report-panel")
      ?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const handleRunAnalysis = async () => {
    if (!caseId || startAnalysisMutation.isPending) return;
    try {
      await startAnalysisMutation.mutateAsync({
        response_language: detectResponseLanguage(
          sources.map((source) => source.exact_text).join("\n"),
        ),
      });
    } catch {
      // Surfaced by the workspace error modal.
    }
  };

  if (!caseId) {
    return (
      <CaseOverviewState
        eyebrow="Case overview"
        title="No Case Material Yet"
        description="Add a case narrative or a file on the sources page to begin."
      />
    );
  }

  if (analysisQuery.isLoading && !analysisResult) {
    return (
      <CaseOverviewState
        title="Loading Case analysis…"
        description="Restoring the saved analysis and the current case sources."
        actionLabel="Open sources"
        onAction={navigateToSources}
        processing
      />
    );
  }

  if (sourcesQuery.isLoading && analysisResult) {
    return (
      <CaseOverviewState
        title="Loading case sources…"
        description="Loading the current case sources."
        actionLabel="Open sources"
        onAction={navigateToSources}
        processing
      />
    );
  }

  if (overview.unavailableReason) {
    return (
      <CaseOverviewState
        title="Analysis unavailable"
        description={`${overview.unavailableReason} Start a new analysis after verifying the Case material.`}
        actionLabel="Open sources"
        onAction={navigateToSources}
        actionIcon="sources"
      />
    );
  }

  if (!overview.hasAnalysis && overview.isProcessing) {
    return (
      <CaseOverviewState
        title="Analyzing Case Material…"
        description="CyberCase is building the case summary, findings, and open questions from the submitted material."
        processing
      />
    );
  }

  if (!overview.hasAnalysis) {
    return (
      <CaseOverviewState
        eyebrow="Case overview"
        title="Analysis Required"
        description="This case has material but no completed case-level analysis yet. Run the analysis from the sources page."
        actionLabel="Open sources"
        onAction={navigateToSources}
        actionIcon="sources"
      />
    );
  }

  const handleSelectSource = (
    sourceRef: SourceMessageRef,
    anchorElement: HTMLElement,
    sourceKey: string,
    citationRole?: "supporting" | "conflicting",
  ) => {
    setActiveSource((current) =>
      current?.sourceKey === sourceKey
        ? null
        : { sourceRef, anchorElement, sourceKey, citationRole },
    );
  };
  const isStale = analysisResult?.freshness === "stale";
  const analysisKey = analysisResult?.id ?? "case-analysis";

  return (
    <section
      id="workspace-overview-panel"
      aria-label="Case Overview"
      className="flex shrink-0 flex-col bg-surface"
    >
      <div className="mx-auto w-full max-w-5xl space-y-8 px-5 py-7 sm:px-8 sm:py-9 lg:px-10">
        <CaseOverviewHeader
          key={caseId}
          caseTitle={caseTitle}
          onOpenReport={scrollToReport}
          onOpenSources={navigateToSources}
        />

        {isFollowupPending ? (
          <div
            role="status"
            className="flex flex-wrap items-center gap-2 rounded-md border border-accent/40 bg-accent-soft px-4 py-3 text-xs text-ink"
          >
            <span className="h-2 w-2 shrink-0 rounded-full bg-accent motion-safe:animate-pulse motion-reduce:animate-none" />
            <div>
              <p className="font-semibold">Updating the case analysis.</p>
              <p className="mt-0.5 text-ink-secondary">
                The follow-up answer was received. The overview will refresh when processing
                finishes.
              </p>
            </div>
          </div>
        ) : isStale ? (
          <div
            role="alert"
            className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-unresolved/40 bg-unresolved/10 px-4 py-3 text-xs text-ink"
          >
            <div className="flex items-start gap-2">
              <span className="h-2 w-2 shrink-0 rounded-full bg-unresolved" />
              <div>
                <p className="font-semibold">Analysis is based on older sources.</p>
                <p className="mt-0.5 text-ink-secondary">
                  New case material was added after this analysis.
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => void handleRunAnalysis()}
              className="btn-primary rounded-md px-3 py-1.5 text-xs font-semibold"
            >
              Analyze latest sources
            </button>
          </div>
        ) : null}

        <OverviewStatusRail overview={overview} result={analysisResult} sources={sources} />

        <OverviewSummarySection summary={overview.incidentSummary} />

        <div className="space-y-4">
          <div
            role="tablist"
            aria-label="Analysis findings and questions"
            className="flex items-center gap-6 border-b border-line text-xs font-semibold"
          >
            <button
              role="tab"
              type="button"
              id="tab-findings"
              aria-controls="panel-findings"
              aria-selected={overviewTab === "findings"}
              onClick={() => setOverviewTab("findings")}
              className={`inline-flex items-center gap-2 border-b-2 pb-2.5 transition-colors outline-none focus-visible:ring-2 focus-visible:ring-accent ${overviewTab === "findings"
                  ? "border-accent text-accent"
                  : "border-transparent text-ink-muted hover:text-ink"
                }`}
            >
              <span>Case Findings</span>
              <span
                className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${overviewTab === "findings"
                    ? "bg-accent text-ivory"
                    : "bg-surface-nested text-ink-secondary"
                  }`}
              >
                {overview.findings.length}
              </span>
            </button>

            <button
              role="tab"
              type="button"
              id="tab-questions"
              aria-controls="panel-questions"
              aria-selected={overviewTab === "questions"}
              onClick={() => setOverviewTab("questions")}
              className={`inline-flex items-center gap-2 border-b-2 pb-2.5 transition-colors outline-none focus-visible:ring-2 focus-visible:ring-accent ${overviewTab === "questions"
                  ? "border-accent text-accent"
                  : "border-transparent text-ink-muted hover:text-ink"
                }`}
            >
              <span>Open Questions</span>
              <span
                className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${overviewTab === "questions"
                    ? "bg-unresolved text-ivory"
                    : "bg-surface-nested text-ink-secondary"
                  }`}
              >
                {overview.gaps.length}
              </span>
            </button>
          </div>

          <div
            id="panel-findings"
            role="tabpanel"
            aria-labelledby="tab-findings"
            className={overviewTab === "findings" ? "block" : "hidden"}
          >
            <CaseFindingsSection
              key={analysisKey}
              findings={overview.findings}
              onNavigateToSource={navigateToSources}
              onSelectSource={handleSelectSource}
              activeSourceKey={activeSource?.sourceKey ?? null}
            />
          </div>

          <div
            id="panel-questions"
            role="tabpanel"
            aria-labelledby="tab-questions"
            className={overviewTab === "questions" ? "block" : "hidden"}
          >
            <OpenQuestionsSection gaps={overview.gaps} />
          </div>
        </div>
      </div>

      {activeSource && (
        <SourceDrawer
          sourceRef={activeSource.sourceRef}
          anchorElement={activeSource.anchorElement}
          onClose={() => setActiveSource(null)}
          onNavigateToSource={navigateToSources}
          citationRole={activeSource.citationRole}
        />
      )}
    </section>
  );
}

function CaseOverviewHeader({
  caseTitle,
  onOpenReport,
  onOpenSources,
}: {
  caseTitle: string;
  onOpenReport: () => void;
  onOpenSources?: () => void;
}) {
  return (
    <header
      aria-label={`${caseTitle} analysis`}
      className="flex flex-wrap items-start justify-between gap-4 border-b border-line pb-5"
    >
      <div>
        <h2 className="text-xl font-semibold tracking-[-0.02em] text-ink sm:text-2xl">Analysis</h2>
        <p className="mt-1.5 max-w-2xl text-xs leading-5 text-ink-muted">
          Grounded findings from the persisted Case Analysis Result and the current case sources.
        </p>
      </div>
      <div className="flex items-center gap-3">
        {onOpenSources && (
          <button
            type="button"
            onClick={onOpenSources}
            className="text-xs font-medium text-ink-secondary underline decoration-line-strong underline-offset-4 hover:text-ink focus-visible:ring-2 focus-visible:ring-accent"
          >
            View sources
          </button>
        )}
        <button
          type="button"
          onClick={onOpenReport}
          className="inline-flex h-9 items-center gap-1.5 rounded-md bg-primary px-3.5 text-xs font-semibold text-ivory hover:bg-charcoal-hover focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
        >
          <Icon name="report" className="h-3.5 w-3.5" />
          Go to report
        </button>
      </div>
    </header>
  );
}

function OverviewSummarySection({ summary }: { summary: string }) {
  if (!summary) return null;
  return (
    <section aria-labelledby="overview-summary-heading" className="order-1 min-w-0 space-y-4">
      <WorkspaceSectionHeader headingId="overview-summary-heading" title="Executive Summary" />
      <div className="max-w-prose text-sm leading-relaxed text-ink [overflow-wrap:anywhere] sm:text-[15px]">
        <ChatMessageMarkdown content={summary} />
      </div>
    </section>
  );
}

function CaseOverviewState({
  eyebrow,
  title,
  description,
  actionLabel,
  onAction,
  actionIcon,
  processing,
}: {
  eyebrow?: string;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  actionIcon?: "sources";
  processing?: boolean;
}) {
  return (
    <div className="mx-auto flex h-full min-h-[360px] w-full max-w-5xl flex-col justify-center px-5 py-10 sm:px-8 lg:px-10">
      <div className="max-w-xl border-y border-line py-8">
        {processing ? (
          <div className="mb-4 flex items-center gap-2 text-source">
            <span className="h-2 w-2 rounded-full bg-source motion-safe:animate-pulse motion-reduce:animate-none" />
            <span className="text-[11px] font-semibold">Analysis in progress</span>
          </div>
        ) : eyebrow ? (
          <p className="section-eyebrow">{eyebrow}</p>
        ) : null}
        <h2 className="text-lg font-semibold tracking-tight text-ink sm:text-xl">{title}</h2>
        <p className="mt-2 max-w-lg text-xs leading-6 text-ink-secondary">{description}</p>
        {actionLabel && onAction && (
          <div className="pt-5">
            <button
              type="button"
              onClick={onAction}
              className="btn-primary inline-flex items-center gap-2 rounded-md"
            >
              {actionIcon && <Icon name={actionIcon} className="h-3.5 w-3.5" />}
              {actionLabel}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

const gapLabels: Record<CaseGap["status"], string> = {
  NOT_PROVIDED: "Not provided",
  EXPLICITLY_UNKNOWN: "Explicitly unknown",
  AMBIGUOUS: "Ambiguous",
  CONFLICTING: "Conflicting information",
};

function OpenQuestionsSection({ gaps }: { gaps: CaseGap[] }) {
  const getStatusBadgeStyle = (status: CaseGap["status"]) => {
    switch (status) {
      case "CONFLICTING":
        return "bg-critical/10 text-critical border border-critical/20";
      case "AMBIGUOUS":
        return "bg-unresolved/15 text-unresolved border border-unresolved/25";
      case "EXPLICITLY_UNKNOWN":
        return "bg-surface-nested text-ink-secondary border border-line";
      case "NOT_PROVIDED":
      default:
        return "bg-amber-500/10 text-amber-700 border border-amber-500/20";
    }
  };

  return (
    <section aria-labelledby="overview-open-questions-heading" className="space-y-4">
      <WorkspaceSectionHeader
        headingId="overview-open-questions-heading"
        title="Open Questions"
        aside={<span className="text-xs text-ink-muted">{gaps.length} total</span>}
      />
      {gaps.length === 0 ? (
        <p className="text-sm text-ink-muted">No open questions recorded.</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-line bg-surface shadow-xs">
          <div className="grid min-w-[640px] grid-cols-[10rem_minmax(0,1fr)_minmax(14rem,0.8fr)] gap-4 border-b border-line bg-surface-nested px-4 py-2.5 text-[11px] font-semibold uppercase tracking-wider text-ink-muted">
            <span>Status</span>
            <span>Topic &amp; Description</span>
            <span>Why It Matters</span>
          </div>
          <div className="divide-y divide-line/60">
            {gaps.map((gap) => (
              <article
                key={gap.id}
                className="grid min-w-[640px] grid-cols-[10rem_minmax(0,1fr)_minmax(14rem,0.8fr)] gap-4 px-4 py-3.5 items-start hover:bg-surface-hover/30 transition-colors"
              >
                <div className="min-w-0 space-y-1">
                  <span
                    className={`inline-flex rounded px-2 py-0.5 text-[10px] font-bold tracking-tight ${getStatusBadgeStyle(
                      gap.status,
                    )}`}
                  >
                    {gapLabels[gap.status]}
                  </span>
                  {gap.askable && (
                    <div>
                      <span className="inline-flex items-center gap-1 rounded bg-unresolved/10 px-1.5 py-0.5 text-[10px] font-medium text-unresolved">
                        <span className="h-1.5 w-1.5 rounded-full bg-unresolved" />
                        Needs clarification
                      </span>
                    </div>
                  )}
                </div>
                <div className="min-w-0 space-y-1">
                  <h3 className="text-xs sm:text-sm font-semibold leading-snug text-ink">
                    {gap.topic}
                  </h3>
                  <p className="text-xs leading-relaxed text-ink-secondary">{gap.description}</p>
                </div>
                <div className="min-w-0">
                  {gap.reason ? (
                    <div className="rounded border border-line/60 bg-surface-nested/40 p-2 text-xs">
                      <span className="font-semibold text-ink-muted">Why it matters: </span>
                      <span className="leading-relaxed text-ink-secondary">{gap.reason}</span>
                    </div>
                  ) : (
                    <span className="text-xs text-ink-muted">—</span>
                  )}
                </div>
              </article>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
