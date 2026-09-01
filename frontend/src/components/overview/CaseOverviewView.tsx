"use client";

import { useMemo, useState } from "react";
import { Icon } from "@/components/common/icons";
import type { PersistedChatMessage, ThreadStatus } from "@/lib/api";
import { buildCaseMaterials } from "@/lib/case-materials";
import { buildCaseOverview, type SourceMessageRef } from "@/lib/case-overview";
import { CaseOverviewHeader } from "./CaseOverviewHeader";
import { CaseFindingsSection } from "./CaseFindingsSection";
import { CasePulse } from "./CasePulse";
import { MitreExplainedSimply } from "./MitreExplainedSimply";
import { OpenQuestionsSection } from "./OpenQuestionsSection";
import { OverviewSummarySection } from "./OverviewSummarySection";
import { SourceEvidencePopover } from "./SourceEvidencePopover";

interface CaseOverviewViewProps {
  threadId: string | null;
  threadTitle: string;
  threadStatus: ThreadStatus;
  messages: PersistedChatMessage[];
  onOpenChat: () => void;
  onOpenReport: () => void;
  onOpenIntake?: () => void;
  onOpenMaterials?: () => void;
  onOpenTechnicalContext?: () => void;
  onNavigateToSource?: (messageId: string) => void;
}

export function CaseOverviewView({
  threadId,
  threadTitle,
  threadStatus,
  messages,
  onOpenChat,
  onOpenReport,
  onOpenIntake,
  onOpenMaterials,
  onOpenTechnicalContext,
  onNavigateToSource,
}: CaseOverviewViewProps) {
  const [activeSourcePopover, setActiveSourcePopover] = useState<{
    sourceRef: SourceMessageRef;
    anchorElement: HTMLElement;
    sourceKey: string;
  } | null>(null);
  const overview = useMemo(
    () => buildCaseOverview(messages, threadStatus),
    [messages, threadStatus],
  );
  const materialCount = useMemo(
    () => buildCaseMaterials(messages).totalCount,
    [messages],
  );

  if (!threadId || messages.length === 0) {
    return (
      <OverviewState
        eyebrow="CASE OVERVIEW"
        title="No Case Material Yet"
        description="Add the first case narrative or document in Intake. CyberCase will create an evidence-bound summary before any optional technical enrichment."
        actionLabel="Open Intake"
        onAction={onOpenIntake ?? onOpenChat}
        actionIcon="intake"
      />
    );
  }

  if (!overview.hasAnalysis && overview.isProcessing) {
    return (
      <OverviewState
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
      <OverviewState
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
  ) => {
    setActiveSourcePopover((current) =>
      current?.sourceKey === sourceKey
        ? null
        : { sourceRef, anchorElement, sourceKey },
    );
  };

  return (
    <div
      id="workspace-overview-panel"
      role="tabpanel"
      aria-label="Case Overview"
      className="flex min-h-0 flex-1 flex-col overflow-y-auto bg-canvas"
    >
      <div className="mx-auto w-full max-w-5xl space-y-8 px-4 py-6 sm:px-7 sm:py-8 lg:px-9">
        <CaseOverviewHeader
          threadTitle={threadTitle}
          threadStatus={threadStatus}
          onOpenChat={onOpenChat}
          onOpenReport={onOpenReport}
          onOpenMaterials={onOpenMaterials}
        />

        <CasePulse
          messages={messages}
          findingCount={overview.findings.length}
          openQuestionCount={overview.gaps.length}
          hasAnalysis={overview.hasAnalysis}
        />

        <div className="grid items-start gap-10 xl:grid-cols-[minmax(0,1fr)_19rem]">
          <div className="min-w-0 space-y-10">
            <OverviewSummarySection summary={overview.incidentSummary} />
            <CaseFindingsSection
              findings={overview.findings}
              onNavigateToSource={onNavigateToSource}
              onSelectSource={handleSelectSource}
              activeSourceKey={activeSourcePopover?.sourceKey ?? null}
            />
          </div>

          <aside className="min-w-0 space-y-5 xl:sticky xl:top-5">
            <OpenQuestionsSection gaps={overview.gaps} onOpenChat={onOpenChat} />
            <TraceabilityCard
              materialCount={materialCount}
              onOpenMaterials={onOpenMaterials}
            />
            <MitreExplainedSimply
              techniques={overview.mitreContext}
              status={overview.technicalContextStatus}
              onOpenTechnicalContext={onOpenTechnicalContext}
            />
          </aside>
        </div>

        <footer className="flex flex-wrap items-center justify-between gap-3 border-t border-line pt-4 text-xs text-ink-muted">
          <span>Case sources and analytical inferences remain visibly separated.</span>
          <button
            type="button"
            onClick={onOpenReport}
            className="font-bold text-ink transition-colors hover:text-accent hover:underline"
          >
            Generate / View Report ↗
          </button>
        </footer>
      </div>

      {activeSourcePopover && (
        <SourceEvidencePopover
          sourceRef={activeSourcePopover.sourceRef}
          anchorElement={activeSourcePopover.anchorElement}
          onClose={() => setActiveSourcePopover(null)}
          onNavigateToSource={onNavigateToSource}
        />
      )}
    </div>
  );
}

function TraceabilityCard({
  materialCount,
  onOpenMaterials,
}: {
  materialCount: number;
  onOpenMaterials?: () => void;
}) {
  return (
    <section className="workspace-card p-4 sm:p-5">
      <p className="section-eyebrow">TRACEABILITY</p>
      <h2 className="mt-1 text-sm font-extrabold tracking-tight text-ink">
        Sources stay inspectable
      </h2>
      <p className="mt-2 text-xs leading-relaxed text-ink-secondary">
        Findings link back to the submitted case material. External technical context is kept separate from the case record.
      </p>
      <div className="mt-4 flex items-center justify-between border-t border-line pt-3">
        <span className="text-[11px] text-ink-muted">
          {materialCount} submitted source{materialCount === 1 ? "" : "s"}
        </span>
        {onOpenMaterials && (
          <button
            type="button"
            onClick={onOpenMaterials}
            className="text-[11px] font-bold text-ink transition-colors hover:text-accent hover:underline"
          >
            View sources →
          </button>
        )}
      </div>
    </section>
  );
}

interface OverviewStateProps {
  eyebrow?: string;
  title: string;
  description: string;
  actionLabel: string;
  onAction: () => void;
  actionIcon?: "chat" | "intake";
  processing?: boolean;
}

function OverviewState({
  eyebrow,
  title,
  description,
  actionLabel,
  onAction,
  actionIcon,
  processing,
}: OverviewStateProps) {
  return (
    <div className="flex h-full min-h-[400px] flex-col items-center justify-center p-6 text-center sm:p-10">
      <div className="workspace-card max-w-md space-y-3 p-8">
        {processing ? (
          <div className="mx-auto flex h-9 w-9 items-center justify-center rounded-xl bg-evidence/10 text-evidence">
            <span className="h-2.5 w-2.5 rounded-full bg-evidence motion-safe:animate-ping motion-reduce:animate-none" />
          </div>
        ) : eyebrow ? (
          <p className="section-eyebrow">{eyebrow}</p>
        ) : null}
        <h2 className="text-base font-extrabold tracking-tight text-ink sm:text-lg">
          {title}
        </h2>
        <p className="text-xs leading-relaxed text-ink-secondary">{description}</p>
        <div className="pt-3">
          <button
            type="button"
            onClick={onAction}
            className="btn-primary inline-flex items-center gap-2 rounded-lg"
          >
            {actionIcon && <Icon name={actionIcon} className="h-3.5 w-3.5" />}
            {actionLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
