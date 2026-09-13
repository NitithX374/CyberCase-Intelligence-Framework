"use client";

import { useMemo, useState } from "react";
import type { CaseAnalysisResultRead, CaseClarificationRead, CaseEvidenceSnapshotRead, CaseRunRead, ThreadStatus } from "@/lib/api";
import type { SourceMessageRef } from "@/lib/case-overview-contracts";
import { buildCaseOverview } from "@/lib/case-overview-builder";
import { CaseOverviewHeader } from "./CaseOverviewHeader";
import { CaseFindingsSection } from "./CaseFindingsSection";
import { MitreExplainedSimply } from "./MitreExplainedSimply";
import { OpenQuestionsSection } from "./OpenQuestionsSection";
import { SourceEvidenceDrawer } from "@/components/evidence/SourceEvidenceDrawer";
import { OverviewStatusRail } from "./OverviewStatusRail";
import { ChatMessageMarkdown } from "@/components/conversation/ChatMessageMarkdown";
import { WorkspaceSectionHeader } from "@/components/common/WorkspaceSectionHeader";
import { CaseOverviewState } from "./CaseOverviewState";

export function OverviewSummarySection({ summary }: { summary: string }) {
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
interface CaseOverviewViewProps {
  threadId: string | null;
  threadTitle: string;
  threadStatus: ThreadStatus;
  onOpenChat: () => void;
  onOpenReport: () => void;
  onOpenIntake?: () => void;
  onOpenMaterials?: () => void;
  onOpenTechnicalContext?: () => void;
  onNavigateToSource?: (messageId: string) => void;
  analysisResult: CaseAnalysisResultRead | null;
  evidenceSnapshot: CaseEvidenceSnapshotRead | null;
  runStatus: CaseRunRead["status"] | null;
  clarifications: CaseClarificationRead[];
  analysisLoading: boolean;
  snapshotLoading: boolean;
  run: CaseRunRead | null;
  onRunAnalysis?: () => void;
}

export function CaseOverviewView({
  threadId,
  threadTitle,
  threadStatus,
  onOpenChat,
  onOpenReport,
  onOpenIntake,
  onOpenMaterials,
  onOpenTechnicalContext,
  onNavigateToSource,
  analysisResult,
  evidenceSnapshot,
  runStatus,
  clarifications,
  analysisLoading,
  snapshotLoading,
  run,
  onRunAnalysis,
}: CaseOverviewViewProps) {
  const [activeSource, setActiveSource] = useState<{
    sourceRef: SourceMessageRef;
    anchorElement: HTMLElement;
    sourceKey: string;
    citationRole?: "supporting" | "conflicting";
  } | null>(null);
  const overview = useMemo(
    () => buildCaseOverview(analysisResult, evidenceSnapshot, runStatus),
    [analysisResult, evidenceSnapshot, runStatus],
  );

  if (!threadId) {
    return (
      <CaseOverviewState
        eyebrow="CASE OVERVIEW"
        title="No Case Material Yet"
        description="Add a case narrative or document in Intake to begin."
        actionLabel="Open Intake"
        onAction={onOpenIntake ?? onOpenChat}
        actionIcon="intake"
      />
    );
  }

  if (analysisLoading && !analysisResult) {
    return <CaseOverviewState title="Loading Case analysis…" description="Restoring the saved Case analysis and its evidence snapshot." actionLabel="Open Intake" onAction={onOpenIntake ?? onOpenChat} processing />;
  }

  if (snapshotLoading && analysisResult) {
    return <CaseOverviewState title="Loading Case evidence…" description="Restoring the exact evidence snapshot used by this analysis." actionLabel="Open Materials" onAction={onOpenMaterials ?? onOpenChat} processing />;
  }

  if (runStatus === "failed" && !analysisResult) {
    return (
      <CaseOverviewState
        eyebrow="CASE OVERVIEW"
        title="Analysis Failed"
        description={run?.error_message || "The case analysis failed to complete. Return to Intake to verify the admitted material and retry."}
        actionLabel="Open Intake"
        onAction={onOpenIntake ?? onOpenChat}
        actionIcon="intake"
      />
    );
  }

  const pendingClarification = clarifications.find((item) => item.state === "pending");
  const isAwaitingFollowup = threadStatus === "awaiting_followup" || Boolean(pendingClarification);
  if (isAwaitingFollowup) {
    const question = pendingClarification?.question?.trim();
    return (
      <CaseOverviewState
        eyebrow={pendingClarification?.topic ? `CLARIFICATION NEEDED · ${pendingClarification.topic}` : "CLARIFICATION NEEDED"}
        title="Analysis Needs More Information"
        description={question ? `The case analysis requires additional details: "${question}" Please proceed to Chat to follow up.` : "The case analysis requires additional details to proceed. Please proceed to Chat to follow up."}
        actionLabel="Proceed to Chat"
        onAction={onOpenChat}
        actionIcon="chat"
      />
    );
  }

  if (overview.unavailableReason) {
    return <CaseOverviewState title="Analysis unavailable" description={`${overview.unavailableReason} Start a new analysis after verifying the admitted Case material.`} actionLabel="Open Intake" onAction={onOpenIntake ?? onOpenChat} actionIcon="intake" />;
  }

  if (!overview.hasAnalysis && overview.isProcessing) {
    return (
      <CaseOverviewState
        title="Analyzing Case Material…"
        description="CyberCase is building the case summary, findings, and open questions from the submitted material."
        actionLabel="View Progress"
        onAction={onOpenChat}
        processing
      />
    );
  }

  if (!overview.hasAnalysis) {
    return (
      <CaseOverviewState
        eyebrow="CASE OVERVIEW"
        title="Analysis Required"
        description="This case has material but no completed case-level analysis yet. Return to Intake to run the analysis."
        actionLabel="Open Intake"
        onAction={onOpenIntake ?? onOpenChat}
        actionIcon="intake"
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
  const sourceNavigation = onNavigateToSource;
  const isStale = analysisResult?.freshness === "stale";
  const analysisKey = analysisResult?.id ?? "case-analysis";

  return (
    <div
      id="workspace-overview-panel"
      role="tabpanel"
      aria-label="Case Overview"
      className="flex min-h-0 flex-1 flex-col overflow-y-auto bg-canvas"
    >
      <div className="mx-auto w-full max-w-6xl space-y-6 px-4 py-6 sm:px-7 sm:py-8 lg:px-9">
        <CaseOverviewHeader
          key={threadId}
          threadId={threadId}
          threadStatus={threadStatus}
          threadTitle={threadTitle}
          onOpenChat={onOpenChat}
          onOpenReport={onOpenReport}
          onOpenMaterials={onOpenMaterials}
        />

        {isStale && (
          <div
            role="alert"
            className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-unresolved/40 bg-unresolved/10 px-4 py-3 text-xs text-ink"
          >
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 shrink-0 rounded-full bg-unresolved" />
              <span className="font-medium">
                Analysis is based on older evidence. New case material was added after this analysis.
              </span>
            </div>
            {onRunAnalysis && (
              <button
                type="button"
                onClick={onRunAnalysis}
                className="btn-primary rounded-lg px-3 py-1.5 text-xs font-semibold"
              >
                Analyze latest evidence
              </button>
            )}
          </div>
        )}

        <div className="flex flex-col gap-7 lg:grid lg:grid-cols-[minmax(0,1fr)_15rem] lg:items-start lg:gap-9">
          <div className="contents lg:block lg:min-w-0 lg:space-y-8">
            <OverviewSummarySection summary={overview.incidentSummary} />
            <div className="order-3 min-w-0">
              <CaseFindingsSection
                key={analysisKey}
                findings={overview.findings}
                onNavigateToSource={sourceNavigation}
                onSelectSource={handleSelectSource}
                activeSourceKey={activeSource?.sourceKey ?? null}
              />
            </div>
          </div>

          <aside className="contents lg:flex lg:min-w-0 lg:flex-col lg:gap-5 lg:border-l lg:border-line lg:pl-5">
            <OverviewStatusRail
              overview={overview}
              result={analysisResult}
              snapshot={evidenceSnapshot}
              runStatus={runStatus}
            />
            <OpenQuestionsSection gaps={overview.gaps} onOpenChat={onOpenChat} />
            <div className="order-5 min-w-0">
              <MitreExplainedSimply
                techniques={overview.mitreContext}
                status={overview.technicalContextStatus}
                onOpenTechnicalContext={onOpenTechnicalContext}
              />
            </div>
          </aside>
        </div>
      </div>

      {activeSource && (
        <SourceEvidenceDrawer
          sourceRef={activeSource.sourceRef}
          anchorElement={activeSource.anchorElement}
          onClose={() => setActiveSource(null)}
          onNavigateToSource={sourceNavigation}
          citationRole={activeSource.citationRole}
        />
      )}
    </div>
  );
}
