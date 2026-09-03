"use client";

import { useMemo, useState } from "react";
import { Icon } from "@/components/common/icons";
import type { PersistedChatMessage, ThreadStatus } from "@/lib/api";
import { buildCaseOverview, type SourceMessageRef } from "@/lib/case-overview";
import { CaseOverviewHeader } from "./CaseOverviewHeader";
import { CaseFindingsSection } from "./CaseFindingsSection";
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
    citationRole?: "supporting" | "conflicting";
  } | null>(null);
  const overview = useMemo(
    () => buildCaseOverview(messages, threadStatus),
    [messages, threadStatus],
  );

  if (!threadId || messages.length === 0) {
    return (
      <OverviewState
        eyebrow="CASE OVERVIEW"
        title="No Case Material Yet"
        description="Add a case narrative or document in Intake to begin."
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
    citationRole?: "supporting" | "conflicting",
  ) => {
    setActiveSourcePopover((current) =>
      current?.sourceKey === sourceKey
        ? null
        : { sourceRef, anchorElement, sourceKey, citationRole },
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
          onOpenChat={onOpenChat}
          onOpenReport={onOpenReport}
          onOpenMaterials={onOpenMaterials}
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
            <MitreExplainedSimply
              techniques={overview.mitreContext}
              status={overview.technicalContextStatus}
              onOpenTechnicalContext={onOpenTechnicalContext}
            />
          </aside>
        </div>
      </div>

      {activeSourcePopover && (
        <SourceEvidencePopover
          sourceRef={activeSourcePopover.sourceRef}
          anchorElement={activeSourcePopover.anchorElement}
          onClose={() => setActiveSourcePopover(null)}
          onNavigateToSource={onNavigateToSource}
          citationRole={activeSourcePopover.citationRole}
        />
      )}
    </div>
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
