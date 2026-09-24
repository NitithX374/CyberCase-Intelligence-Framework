"use client";

import { useMemo, useState, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import type { CaseGap } from "@/features/analysis/types";
import type { SourceMessageRef } from "@/features/sources/types";
import { buildCaseOverview } from "./overview";
import { useCaseAnalysis, useIsCaseAnalysisRunning } from "@/features/analysis/queries";
import { useCaseSourceRows } from "@/features/sources/useCaseSourceRows";
import { useSourceDrawer } from "@/features/sources/useSourceDrawer";
import { casePath } from "@/features/workspace/routes";
import { CaseFindingsSection } from "./CaseFindingsSection";
import { CaseDetails } from "./CaseDetails";
import { SourceDrawer } from "@/features/sources/SourceDrawer";
import { AnalysisMeta } from "./AnalysisMeta";
import { ChatMessageMarkdown } from "@/features/chat/ChatMessageMarkdown";
import { Icon } from "@/components/icons";
import { DisclosurePanel, DisclosureToggle } from "@/components/Disclosure";
import { EmptyState } from "@/components/EmptyState";
import { useWorkspaceActivity } from "@/features/workspace/WorkspaceActivityContext";

interface CaseOverviewViewProps {
  caseId: string | null;
}

export function CaseOverviewView({ caseId }: CaseOverviewViewProps) {
  const router = useRouter();

  const analysisQuery = useCaseAnalysis(caseId);
  const { caseSources, rows: sources, isLoading: sourcesLoading } = useCaseSourceRows(caseId);
  const drawer = useSourceDrawer();

  const isAnalysisRunning = useIsCaseAnalysisRunning(caseId);

  const analysisResult = analysisQuery.data ?? null;
  const { isFollowupPending, runAnalysis } = useWorkspaceActivity();
  const [overviewTab, setOverviewTab] = useState<"findings" | "questions">("findings");
  const overview = useMemo(
    () => buildCaseOverview(analysisResult, sources),
    [analysisResult, sources],
  );

  const navigateToSources = () => {
    if (caseId) router.push(casePath(caseId, "sources"));
  };

  if (!caseId) {
    return (
      <CaseOverviewState
        title="No case material yet"
        description="Add a narrative or a file to begin."
      />
    );
  }

  if ((analysisQuery.isLoading && !analysisResult) || (sourcesLoading && analysisResult)) {
    return <CaseOverviewSkeleton />;
  }

  if (overview.unavailableReason) {
    return (
      <CaseOverviewState
        title="Analysis unavailable"
        description={overview.unavailableReason}
        actionLabel="Open sources"
        onAction={navigateToSources}
      />
    );
  }

  if (!overview.hasAnalysis && isAnalysisRunning) {
    return (
      <CaseOverviewState
        processing
        title="Analyzing…"
        description="Reading the case sources. This can take a minute."
      />
    );
  }

  if (!overview.hasAnalysis) {
    const hasSources = caseSources.length > 0;
    return (
      <CaseOverviewState
        title="Not analyzed yet"
        description={
          hasSources
            ? "Analyze the case to get a summary, findings and open questions."
            : "Add a narrative or a file, then analyze the case."
        }
        actionLabel={hasSources ? "Analyze" : "Add sources"}
        onAction={hasSources ? runAnalysis : navigateToSources}
      />
    );
  }

  const handleSelectSource = (
    sourceRef: SourceMessageRef,
    anchorElement: HTMLElement,
    key: string,
    citationRole?: "supporting" | "conflicting",
  ) => drawer.toggle({ sourceRef, anchorElement, key, citationRole });
  const isStale = analysisResult?.freshness === "stale";
  const isUpdating = isFollowupPending || isAnalysisRunning;
  const analysisKey = analysisResult?.id ?? "case-analysis";

  return (
    <section
      id="workspace-overview-panel"
      aria-label="Case Overview"
      className="flex shrink-0 flex-col bg-surface"
    >
      <div className="mx-auto w-full max-w-[52rem] px-5 pt-8 sm:px-8 sm:pt-12">
        {isUpdating ? (
          <div
            role="status"
            className="mb-8 flex items-center gap-2.5 rounded-lg bg-accent-soft px-3.5 py-2.5 text-[13px] text-accent-strong"
          >
            <Icon name="spinner" className="h-4 w-4 shrink-0" />
            <span className="font-medium">
              {isFollowupPending
                ? "Updating the case analysis with your answer…"
                : "Updating the case analysis…"}
            </span>
          </div>
        ) : isStale ? (
          <div
            role="alert"
            className="mb-8 flex flex-wrap items-center justify-between gap-x-4 gap-y-2 border-y border-line py-2 text-[13px] text-ink"
          >
            <p>
              <span className="font-semibold">Analysis is based on older sources.</span>{" "}
              <span className="text-ink-secondary">New material was added since.</span>
            </p>
            <button type="button" onClick={runAnalysis} className="btn-secondary h-8 px-3">
              Analyze latest sources
            </button>
          </div>
        ) : null}

        <OverviewSummarySection
          summary={overview.incidentSummary}
          meta={
            <AnalysisMeta
              overview={overview}
              result={analysisResult}
              sources={sources}
              onReanalyze={isStale || isUpdating ? undefined : runAnalysis}
            />
          }
        />

        <CaseDetails
          timeline={overview.timeline}
          parties={overview.parties}
          impacts={overview.impacts}
          onSelectSource={handleSelectSource}
          activeSourceKey={drawer.openKey}
        />

        <div className="mt-12">
          <div
            role="tablist"
            aria-label="Analysis findings and questions"
            className="flex items-center gap-6 border-b border-line"
          >
            <OverviewTab
              id="findings"
              label="Findings"
              count={overview.findings.length}
              selected={overviewTab === "findings"}
              onSelect={() => setOverviewTab("findings")}
            />
            <OverviewTab
              id="questions"
              label="Open questions"
              count={overview.gaps.length}
              selected={overviewTab === "questions"}
              onSelect={() => setOverviewTab("questions")}
              attention={overview.gaps.length > 0}
            />
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
              activeSourceKey={drawer.openKey}
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

      {drawer.open && (
        <SourceDrawer
          sourceRef={drawer.open.sourceRef}
          anchorElement={drawer.open.anchorElement}
          onClose={drawer.close}
          onNavigateToSource={navigateToSources}
          citationRole={drawer.open.citationRole}
        />
      )}
    </section>
  );
}

function OverviewTab({
  id,
  label,
  count,
  selected,
  onSelect,
  attention = false,
}: {
  id: string;
  label: string;
  count: number;
  selected: boolean;
  onSelect: () => void;
  attention?: boolean;
}) {
  return (
    <button
      role="tab"
      type="button"
      id={`tab-${id}`}
      aria-controls={`panel-${id}`}
      aria-selected={selected}
      onClick={onSelect}
      className={`-mb-px inline-flex items-center gap-2 border-b-2 pb-3 text-[15px] font-semibold transition-colors ${
        selected ? "border-ink text-ink" : "border-transparent text-ink-muted hover:text-ink"
      }`}
    >
      {label}
      <span
        className={`text-[13px] font-medium ${attention && !selected ? "text-unresolved" : "text-ink-muted"}`}
      >
        {count}
      </span>
    </button>
  );
}

function OverviewSummarySection({ summary, meta }: { summary: string; meta: ReactNode }) {
  if (!summary) return null;
  return (
    <section aria-labelledby="overview-summary-heading" className="min-w-0">
      <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1">
        <h2 id="overview-summary-heading" className="text-base font-semibold text-ink">
          Summary
        </h2>
        {meta}
      </div>
      <div className="mt-3 max-w-[68ch] text-ink [overflow-wrap:anywhere] [&_p]:mb-4 [&_p]:text-base [&_p]:leading-8 sm:[&_p]:text-[17px]">
        <ChatMessageMarkdown content={summary} />
      </div>
    </section>
  );
}

function CaseOverviewSkeleton() {
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

function CaseOverviewState({
  title,
  description,
  actionLabel,
  onAction,
  processing,
}: {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  processing?: boolean;
}) {
  return (
    <EmptyState
      busy={processing}
      title={title}
      description={description}
      className="mx-auto min-h-[420px] w-full max-w-[52rem] justify-center px-5 py-16 sm:px-8"
    >
      {actionLabel && onAction && (
        <button type="button" onClick={onAction} className="btn-primary mt-5">
          {actionLabel}
        </button>
      )}
    </EmptyState>
  );
}

const gapLabels: Record<CaseGap["status"], string> = {
  NOT_PROVIDED: "Missing",
  EXPLICITLY_UNKNOWN: "Unknown",
  AMBIGUOUS: "Ambiguous",
  CONFLICTING: "Conflicting",
};

const gapTextClass: Record<CaseGap["status"], string> = {
  CONFLICTING: "text-critical",
  AMBIGUOUS: "text-unresolved",
  NOT_PROVIDED: "text-unresolved",
  EXPLICITLY_UNKNOWN: "text-ink-secondary",
};

function OpenQuestionsSection({ gaps }: { gaps: CaseGap[] }) {
  if (gaps.length === 0) {
    return <p className="py-6 text-sm text-ink-muted">Nothing is missing from this analysis.</p>;
  }
  return (
    <ul aria-label="Open questions" className="divide-y divide-line pt-2">
      {gaps.map((gap) => (
        <OpenQuestionRow key={gap.id} gap={gap} />
      ))}
    </ul>
  );
}

function OpenQuestionRow({ gap }: { gap: CaseGap }) {
  const [isOpen, setIsOpen] = useState(false);
  const reasonId = `gap-${gap.id}-reason`;
  return (
    <li className="grid gap-x-4 gap-y-1.5 py-4 sm:grid-cols-[6.5rem_minmax(0,1fr)]">
      <div className="flex flex-wrap items-start gap-1.5 sm:pt-0.5">
        <span className={`text-[13px] font-medium ${gapTextClass[gap.status]}`}>
          {gapLabels[gap.status]}
        </span>
      </div>
      <div className="min-w-0">
        <h3 className="text-[15px] font-semibold leading-6 text-ink">{gap.topic}</h3>
        <p className="mt-0.5 text-sm leading-6 text-ink-secondary">{gap.description}</p>
        {(gap.askable || gap.reason) && (
          <div className="mt-1.5 flex flex-wrap items-center gap-1.5">
            {gap.askable && (
              <span className="text-xs font-medium text-ink-secondary">Needs an answer</span>
            )}
            {gap.reason && (
              <DisclosureToggle
                label="Why it matters"
                isOpen={isOpen}
                onToggle={() => setIsOpen((open) => !open)}
                controls={reasonId}
              />
            )}
          </div>
        )}
        {gap.reason && isOpen && (
          <DisclosurePanel id={reasonId} className="mt-2">
            {gap.reason}
          </DisclosurePanel>
        )}
      </div>
    </li>
  );
}
