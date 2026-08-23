"use client";

import { useMemo, useState } from "react";
import type { PersistedChatMessage, ThreadStatus } from "@/lib/api";
import { buildCaseOverview, type SourceMessageRef } from "@/lib/case-overview";
import { WhatHappenedCard } from "./WhatHappenedCard";
import { AttackStoryTimeline } from "./AttackStoryTimeline";
import { EstablishedVsUnclearSection } from "./EstablishedVsUnclearSection";
import { MitreExplainedSimply } from "./MitreExplainedSimply";
import { InvestigationPointsSection } from "./InvestigationPointsSection";
import { SourceEvidencePopover } from "./SourceEvidencePopover";
import { Icon } from "@/components/common/icons";

interface CaseOverviewViewProps {
  threadId: string | null;
  threadTitle: string;
  threadStatus: ThreadStatus;
  messages: PersistedChatMessage[];
  onOpenChat: () => void;
  onOpenReport: () => void;
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

  const handleSelectSource = (
    sourceRef: SourceMessageRef,
    anchorEl: HTMLElement,
    sourceKey: string,
  ) => {
    setActiveSourcePopover((prev) =>
      prev?.sourceKey === sourceKey
        ? null
        : { sourceRef, anchorElement: anchorEl, sourceKey },
    );
  };

  // 1. Empty Thread / No case selected
  if (!threadId || messages.length === 0) {
    return (
      <div className="flex h-full min-h-[400px] flex-col items-center justify-center p-6 text-center sm:p-10">
        <div className="mx-auto max-w-md space-y-3">
          <p className="font-mono text-xs font-bold tracking-wider text-ink-muted uppercase">
            PROSECUTOR CASE OVERVIEW
          </p>
          <h2 className="text-base font-bold text-ink sm:text-lg">
            No Case Activity Yet
          </h2>
          <p className="text-xs leading-relaxed text-ink-secondary">
            Provide incident details, timeline notes, or system logs in the Chat workspace. CyberCase will generate a prosecutor-oriented case overview and attack story.
          </p>
          <div className="pt-3">
            <button
              type="button"
              onClick={onOpenChat}
              className="inline-flex items-center gap-2 rounded bg-primary px-4 py-2 text-xs font-bold text-ivory transition-colors hover:bg-charcoal-hover active:bg-charcoal-pressed"
            >
              <Icon name="chat" className="h-3.5 w-3.5" />
              <span>Go to Chat Workspace</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // 2. Processing State
  if (!overview.hasAnalysis && overview.isProcessing) {
    return (
      <div className="flex h-full min-h-[400px] flex-col items-center justify-center p-6 text-center sm:p-10">
        <div className="mx-auto max-w-md space-y-3">
          <div className="mx-auto flex h-8 w-8 items-center justify-center rounded-full bg-line text-ink">
            <span className="h-2.5 w-2.5 rounded-full bg-ink motion-safe:animate-ping" />
          </div>
          <h2 className="text-base font-bold text-ink sm:text-lg">
            Analyzing Case Evidence…
          </h2>
          <p className="text-xs leading-relaxed text-ink-secondary">
            Grounded case analysis and MITRE ATT&amp;CK intelligence correlation are currently running.
          </p>
          <div className="pt-3">
            <button
              type="button"
              onClick={onOpenChat}
              className="inline-flex items-center gap-2 rounded border border-line bg-surface px-4 py-1.5 text-xs font-bold text-ink transition-colors hover:bg-surface-hover"
            >
              <Icon name="chat" className="h-3.5 w-3.5" />
              <span>View Chat Progress</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // 3. Unanalysed Thread State
  if (!overview.hasAnalysis) {
    return (
      <div className="flex h-full min-h-[400px] flex-col items-center justify-center p-6 text-center sm:p-10">
        <div className="mx-auto max-w-md space-y-3">
          <p className="font-mono text-xs font-bold tracking-wider text-ink-muted uppercase">
            PROSECUTOR CASE OVERVIEW
          </p>
          <h2 className="text-base font-bold text-ink sm:text-lg">
            Analysis Required
          </h2>
          <p className="text-xs leading-relaxed text-ink-secondary">
            No completed analysis is available for this chat yet. Open the Chat workspace to analyze the incident evidence and produce the Case Overview.
          </p>
          <div className="pt-3">
            <button
              type="button"
              onClick={onOpenChat}
              className="inline-flex items-center gap-2 rounded bg-primary px-4 py-2 text-xs font-bold text-ivory transition-colors hover:bg-charcoal-hover active:bg-charcoal-pressed"
            >
              <Icon name="chat" className="h-3.5 w-3.5" />
              <span>Open Chat</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // 4. Full Analyzed Dossier Overview
  return (
    <div
      id="workspace-overview-panel"
      role="tabpanel"
      aria-label="Case Overview"
      className="flex min-h-0 flex-1 flex-col overflow-y-auto bg-canvas"
    >
      <div className="mx-auto w-full max-w-4xl space-y-8 px-4 py-6 sm:px-8 lg:px-10">
        {/* Executive Dossier Header */}
        <header className="border-b border-line pb-4">
          <div className="flex flex-wrap items-baseline justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-[10px] font-bold tracking-widest text-ink-muted uppercase">
                  Prosecutor Case Overview · Case Brief
                </span>
                <span className="font-mono text-[11px] text-ink-muted">
                  #{threadId.slice(0, 8)}
                </span>
              </div>
              <h1 className="mt-1 text-xl font-bold tracking-tight text-ink sm:text-2xl">
                {threadTitle}
              </h1>
            </div>

            {/* Restrained Action Links */}
            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                onClick={onOpenChat}
                className="inline-flex items-center gap-1.5 rounded border border-line bg-surface px-3 py-1.5 text-xs font-bold text-ink transition-colors hover:border-ink hover:bg-surface-hover focus-visible:ring-2 focus-visible:ring-primary"
              >
                <Icon name="chat" className="h-3.5 w-3.5" />
                <span>Ask about this case</span>
              </button>
              <button
                type="button"
                onClick={onOpenReport}
                className="inline-flex items-center gap-1.5 rounded bg-primary px-3 py-1.5 text-xs font-bold text-ivory transition-colors hover:bg-charcoal-hover active:bg-charcoal-pressed focus-visible:ring-2 focus-visible:ring-primary"
              >
                <Icon name="report" className="h-3.5 w-3.5" />
                <span>View Report</span>
              </button>
            </div>
          </div>
        </header>

        {/* Section 1: What Happened? */}
        <WhatHappenedCard
          summary={overview.incidentSummary}
          totalMessagesCount={overview.totalMessagesCount}
        />

        {/* Section 2: Attack Story & Progression */}
        <AttackStoryTimeline
          steps={overview.attackStory}
          onNavigateToSource={onNavigateToSource}
          onSelectSource={handleSelectSource}
          activeSourceKey={activeSourcePopover?.sourceKey ?? null}
        />

        {/* Sections 3 & 4: What is Established? & What Remains Unclear? */}
        <EstablishedVsUnclearSection
          establishedFacts={overview.establishedFacts}
          unclearItems={overview.unclearItems}
          onNavigateToSource={onNavigateToSource}
          onSelectSource={handleSelectSource}
          activeSourceKey={activeSourcePopover?.sourceKey ?? null}
          onOpenMaterials={onOpenMaterials}
        />

        {/* Section 5: MITRE ATT&CK Context */}
        <MitreExplainedSimply
          techniques={overview.mitreContext}
          onOpenTechnicalContext={onOpenTechnicalContext}
        />

        {/* Section 6: Points for Further Investigation */}
        <InvestigationPointsSection
          points={overview.investigationPoints}
        />

        {/* Quiet Dossier Footer */}
        <footer className="border-t border-line pt-4 text-xs text-ink-muted">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <span>
              CyberCase Intelligence Framework · Analytical Dossier
            </span>
            <div className="flex flex-wrap items-center gap-3">
              <button
                type="button"
                onClick={onOpenChat}
                className="font-bold text-ink hover:underline"
              >
                Ask about this case in Chat ↗
              </button>
              <span>·</span>
              <button
                type="button"
                onClick={onOpenReport}
                className="font-bold text-ink hover:underline"
              >
                Generate / View Report ↗
              </button>
            </div>
          </div>
        </footer>
      </div>

      {/* Lightweight Anchored Source Evidence Popover */}
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
