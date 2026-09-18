"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { CaseAnalysisResultRead, CaseSourceRead, ChatMessageRead } from "@/lib/api";
import {
  followUpGapDetailForMessage,
} from "@/lib/chat-followup";
import type { SourceMessageRef } from "@/lib/caseOverviewTypes";
import { buildCaseOverview } from "@/lib/caseOverview";
import { asArray, asRecord, asStringArray, parseCaseCitations, parseCaseEvidence, sourceRefs } from "@/lib/caseOverviewSource";
import { Icon } from "@/components/common/icons";
import { StatusPill } from "@/components/common/StatusPill";
import { ChatMessageMarkdown } from "./ChatMessageMarkdown";
import { SourceEvidenceDrawer } from "@/components/evidence/SourceEvidenceDrawer";
import { EvidenceCitationChip } from "@/components/evidence/EvidenceCitationChip";

interface ChatTranscriptProps {
  messages: ChatMessageRead[];
  isProcessing: boolean;
  isResponding?: boolean;
  leadResult?: CaseAnalysisResultRead | null;
  evidenceSources?: CaseSourceRead[] | null;
  onOpenOverview?: () => void;
  onNavigateToSource?: (messageId: string) => void;
}

export function ChatTranscript({
  messages,
  isProcessing,
  isResponding = false,
  leadResult,
  evidenceSources,
  onOpenOverview,
  onNavigateToSource,
}: ChatTranscriptProps) {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  const displayMessages = leadResult
    ? messages.filter((message) => !isLeadAnalysisPublication(message, leadResult.id))
    : messages;
  const initialMessageIdsRef = useRef<Set<string> | null>(null);
  const leadResultIdRef = useRef<string | null>(leadResult?.id ?? null);
  const hasClarificationUpdate = messages.some((message) =>
    message.role === "user" &&
    message.message_kind === "followup_answer" &&
    messageCreatedBeforeResult(message.created_at, leadResult?.created_at),
  );

  useEffect(() => {
    if (leadResultIdRef.current !== (leadResult?.id ?? null)) {
      leadResultIdRef.current = leadResult?.id ?? null;
      initialMessageIdsRef.current = messages.length > 0 ? new Set(messages.map((message) => message.id)) : null;
      return;
    }
    if (!initialMessageIdsRef.current) {
      if (messages.length === 0) return;
      initialMessageIdsRef.current = new Set(messages.map((message) => message.id));
      return;
    }
    const hasNewMessage = messages.some((message) => !initialMessageIdsRef.current?.has(message.id));
    if (!hasNewMessage && !isProcessing && !isResponding) return;
    initialMessageIdsRef.current = new Set(messages.map((message) => message.id));
    bottomRef.current?.scrollIntoView?.({ behavior: "smooth" });
  }, [isProcessing, isResponding, leadResult?.id, messages]);

  if (displayMessages.length === 0 && !leadResult && !isResponding) {
    return (
      <div className="flex h-full min-h-[400px] flex-col items-center justify-center p-8 text-center">
        <div className="max-w-md space-y-3 border-l-2 border-evidence/50 px-5 py-2 text-left">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-evidence/10 text-evidence">
            <Icon name="chat" className="h-5 w-5" />
          </div>
          <h3 className="text-base font-bold tracking-tight text-ink">Ask about this case</h3>
          <p className="text-xs leading-relaxed text-ink-secondary">
            Ask about the current Case Analysis Result or add information that should become part of the case material.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-4xl space-y-1 px-4 py-4 md:px-5 md:py-6">
      {displayMessages.length === 0 && leadResult && (
        <div className="rounded-md border border-line bg-surface/40 p-4 text-center text-xs text-ink-muted">
          Ask a question below to explore the case analysis or review details.
        </div>
      )}
      {displayMessages.map((message) => {
        const isUser = message.role === "user";
        const isClarificationQuestion = message.message_kind === "followup_question";
        const isClarificationAnswer = message.message_kind === "followup_answer";
        const followUpGap = followUpGapDetailForMessage(message);
        return (
          <article key={message.id} className="border-b border-line py-5 first:pt-1 last:border-b-0">
            <header className="flex items-center gap-2 text-[11px] font-semibold text-ink-muted">
              <span className={isUser ? "text-ink" : isClarificationQuestion ? "text-unresolved" : "text-evidence"}>
                {messageLabel(message, isClarificationQuestion, isClarificationAnswer)}
              </span>
            </header>

            <div
              className={`mt-3 ${isUser
                ? "ml-auto max-w-[90%] rounded-md bg-primary px-4 py-3 text-ivory sm:max-w-[82%] sm:px-5"
                : isClarificationQuestion
                  ? "border-l-2 border-unresolved bg-unresolved/5 pl-4 pr-3 sm:pl-5"
                  : "border-l-2 border-evidence/50 pl-4 pr-1 sm:pl-5"
                }`}
            >
              {isUser ? (
                <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</p>
              ) : (
                <>
                  <ChatMessageMarkdown content={message.content} />
                  <AnalysisEvidenceReferences
                    analysisMessage={message}
                    evidenceSources={evidenceSources ?? []}
                    onNavigateToSource={onNavigateToSource}
                  />
                  {followUpGap && <FollowUpActionCard detail={followUpGap} />}
                </>
              )}
            </div>
          </article>
        );
      })}

      {isResponding && (
        <div
          role="status"
          aria-live="polite"
          aria-label="CyberCase is responding"
          className="flex items-center gap-2 px-1 py-5 text-xs font-semibold text-ink-secondary"
        >
          <span className="text-evidence">CyberCase</span>
          <span aria-hidden="true" className="tracking-[0.2em]">...</span>
        </div>
      )}

      {isProcessing && !isResponding && (
        <div className="flex items-center gap-2 px-1 py-5 text-xs font-semibold text-ink-secondary">
          <StatusPill tone="evidence">Analysis in progress</StatusPill>
          <span>Reviewing the current case material…</span>
        </div>
      )}

      <div ref={bottomRef} aria-hidden="true" />
    </div>
  );
}

function messageCreatedBeforeResult(messageCreatedAt: string, resultCreatedAt: string | undefined): boolean {
  if (!resultCreatedAt) return false;
  const messageTime = Date.parse(messageCreatedAt);
  const resultTime = Date.parse(resultCreatedAt);
  return Number.isFinite(messageTime) && Number.isFinite(resultTime) && messageTime <= resultTime;
}

function messageLabel(
  message: ChatMessageRead,
  isClarificationQuestion: boolean,
  isClarificationAnswer: boolean,
): string {
  if (message.role === "user") {
    if (isClarificationAnswer) return "You · Case information";
    return "You";
  }
  return isClarificationQuestion ? "CyberCase · One more detail" : "CyberCase";
}

function isLeadAnalysisPublication(
  message: ChatMessageRead,
  leadResultId: string,
): boolean {
  if (
    message.message_kind === "followup_question" ||
    message.message_kind === "followup_answer"
  ) {
    return false;
  }
  if (message.message_kind === "conversation" && message.metadata_json.action === "conversation") {
    return false;
  }
  return message.analysis_result_id === leadResultId;
}



function Metric({ label, value, emphasis }: { label: string; value: string; emphasis?: "positive" | "attention" }) {
  return (
    <div className="min-w-0">
      <dt className="text-[10px] font-medium text-ink-muted">{label}</dt>
      <dd className={`mt-1 truncate text-xs font-bold ${emphasis === "attention" ? "text-unresolved" : emphasis === "positive" ? "text-established" : "text-ink"}`}>{value}</dd>
    </div>
  );
}

interface AnalysisSourceReference {
  role: "supporting" | "conflicting";
  source: SourceMessageRef;
}

function sourceReferencesForAnalysisMessage(
  analysisMessage: ChatMessageRead,
  evidenceSources: CaseSourceRead[],
): AnalysisSourceReference[] {
  if (analysisMessage.role !== "assistant") return [];
  const trace = asRecord(analysisMessage.metadata_json.analysis_trace);
  if (trace?.version !== "case_analysis_trace_v1" || trace.validation_status !== "validated") return [];
  const sources = parseCaseEvidence(evidenceSources);
  const references = asArray(trace.claims).flatMap((value) => {
    const claim = asRecord(value);
    if (!claim) return [];
    const supportingIds = asStringArray(claim.supporting_source_ids);
    const contradictingIds = asStringArray(claim.contradicting_source_ids);
    return [
      ...sourceRefs(supportingIds, parseCaseCitations(claim.supporting_citations, supportingIds, sources), sources).map((source) => ({ role: "supporting" as const, source })),
      ...sourceRefs(contradictingIds, parseCaseCitations(claim.contradicting_citations, contradictingIds, sources), sources).map((source) => ({ role: "conflicting" as const, source })),
    ];
  });
  const unique = new Map<string, AnalysisSourceReference>();
  for (const reference of references) {
    const key = [reference.role, reference.source.id, reference.source.exactQuote ?? "", reference.source.pageNumbers.join(",")].join(":");
    if (!unique.has(key)) unique.set(key, reference);
  }
  return [...unique.values()].slice(0, 12);
}

function AnalysisEvidenceReferences({
  analysisMessage,
  evidenceSources,
  onNavigateToSource,
}: {
  analysisMessage: ChatMessageRead;
  evidenceSources: CaseSourceRead[];
  onNavigateToSource?: (messageId: string) => void;
}) {
  const references = sourceReferencesForAnalysisMessage(analysisMessage, evidenceSources);
  const [active, setActive] = useState<{
    key: string;
    source: SourceMessageRef;
    anchor: HTMLElement;
    role: "supporting" | "conflicting";
  } | null>(null);
  if (references.length === 0) return null;

  return (
    <div className="mt-4 border-t border-line/70 pt-3">
      <p className="text-[10px] font-semibold tracking-[0.04em] text-ink-muted">Evidence references</p>
      <div className="mt-2 flex flex-wrap gap-1.5">
        {references.map((reference, index) => {
          const key = `${reference.role}-${reference.source.id}-${index}`;
          return (
            <EvidenceCitationChip
              key={key}
              sourceRef={reference.source}
              sourceKey={key}
              isActive={active?.key === key}
              citationRole={reference.role}
              onSelect={(source, anchor, sourceKey) => setActive((current) => current?.key === sourceKey ? null : { key: sourceKey, source, anchor, role: reference.role })}
            />
          );
        })}
      </div>
      {active && <SourceEvidenceDrawer sourceRef={active.source} anchorElement={active.anchor} onClose={() => setActive(null)} citationRole={active.role} onNavigateToSource={onNavigateToSource} />}
    </div>
  );
}

function FollowUpActionCard({ detail }: { detail: NonNullable<ReturnType<typeof followUpGapDetailForMessage>> }) {
  return (
    <aside className="mt-4 overflow-hidden rounded-lg border border-unresolved/30 bg-unresolved/5">
      <div className="border-l-2 border-unresolved px-4 py-3.5 sm:px-5">
        <div className="flex flex-wrap items-center gap-2"><StatusPill tone="attention">Needs clarification</StatusPill><span className="text-[11px] font-medium text-ink-secondary">Your answer can improve the current analysis.</span></div>
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <div><p className="text-[10px] font-semibold tracking-[0.04em] text-ink-muted">What remains unclear</p><p className="mt-1 text-xs leading-relaxed text-ink"><strong className="font-bold">{detail.topic}</strong><span>:</span> {detail.description}</p></div>
          <div><p className="text-[10px] font-semibold tracking-[0.04em] text-ink-muted">Why this matters</p><p className="mt-1 text-xs leading-relaxed text-ink-secondary">{detail.reason}</p></div>
        </div>
      </div>
    </aside>
  );
}
