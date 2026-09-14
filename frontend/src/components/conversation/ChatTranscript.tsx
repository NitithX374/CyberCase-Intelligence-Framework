"use client";

import { useEffect, useRef } from "react";
import type { CaseAnalysisResultRead, CaseEvidenceSnapshotRead, PersistedChatMessage } from "@/lib/api";
import {
  followUpGapDetailForMessage,
} from "@/lib/chat-followup";
import { mitreCandidatesForMessage } from "@/lib/mitre-candidate";
import { Icon } from "@/components/common/icons";
import { StatusPill } from "@/components/common/StatusPill";
import { ChatMessageMarkdown } from "./ChatMessageMarkdown";
import { AnalysisEvidenceReferences } from "./AnalysisEvidenceReferences";
import { FollowUpActionCard } from "./FollowUpActionCard";
import { MitreCandidatePanel } from "./MitreCandidatePanel";
import { CaseAnalysisLeadCard } from "./CaseAnalysisLeadCard";

interface ChatTranscriptProps {
  messages: PersistedChatMessage[];
  isProcessing: boolean;
  leadResult?: CaseAnalysisResultRead | null;
  leadSnapshot?: CaseEvidenceSnapshotRead | null;
  onOpenOverview?: () => void;
  onNavigateToSource?: (messageId: string) => void;
}

export function ChatTranscript({
  messages,
  isProcessing,
  leadResult,
  leadSnapshot,
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
    (message.message_kind === "followup_answer" || message.message_kind === "clarification_answer") &&
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
    if (!hasNewMessage && !isProcessing) return;
    initialMessageIdsRef.current = new Set(messages.map((message) => message.id));
    bottomRef.current?.scrollIntoView?.({ behavior: "smooth" });
  }, [isProcessing, leadResult?.id, messages]);

  if (displayMessages.length === 0 && !leadResult) {
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
      {leadResult && (
        <CaseAnalysisLeadCard
          result={leadResult}
          snapshot={leadSnapshot}
          isUpdated={hasClarificationUpdate}
          onOpenOverview={onOpenOverview}
        />
      )}
      {displayMessages.length === 0 && leadResult && (
        <div className="rounded-md border border-line bg-surface/40 p-4 text-center text-xs text-ink-muted">
          Ask a question below to explore the case analysis or review details.
        </div>
      )}
      {displayMessages.map((message) => {
        const isUser = message.role === "user";
        const isClarificationQuestion = message.message_kind === "followup_question";
        const isClarificationAnswer = message.message_kind === "followup_answer" || message.message_kind === "clarification_answer";
        const followUpGap = followUpGapDetailForMessage(message);
        const mitreCandidates = isUser ? null : mitreCandidatesForMessage(message);
        return (
          <article key={message.id} className="border-b border-line py-5 first:pt-1 last:border-b-0">
            <header className="flex items-center gap-2 text-[11px] font-semibold text-ink-muted">
              <span className={isUser ? "text-ink" : isClarificationQuestion ? "text-unresolved" : "text-evidence"}>
                {messageLabel(message, isClarificationQuestion, isClarificationAnswer)}
              </span>
            </header>

            <div
              className={`mt-3 ${
                isUser
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
                    messages={messages}
                    onNavigateToSource={onNavigateToSource}
                  />
                  {followUpGap && <FollowUpActionCard detail={followUpGap} />}
                  {mitreCandidates && <MitreCandidatePanel candidates={mitreCandidates} />}
                </>
              )}
            </div>
          </article>
        );
      })}

      {isProcessing && (
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
  message: PersistedChatMessage,
  isClarificationQuestion: boolean,
  isClarificationAnswer: boolean,
): string {
  if (message.role === "user") {
    if (isClarificationAnswer) return "You · Case information";
    if (message.metadata_json.evidence_kind === "initial_case_narrative" || message.metadata_json.evidence_kind === "added_case_information") {
      return "You · Case information";
    }
    return "You";
  }
  return isClarificationQuestion ? "CyberCase · One more detail" : "CyberCase";
}

function isLeadAnalysisPublication(
  message: PersistedChatMessage,
  leadResultId: string,
): boolean {
  if (
    message.message_kind === "followup_question" ||
    message.message_kind === "followup_answer" ||
    message.message_kind === "clarification_answer"
  ) {
    return false;
  }
  const metadata = message.metadata_json;
  const isResponseScopedAnswer = message.message_kind === "conversation" && (
    metadata?.analysis_kind === "question_answer" ||
    metadata?.context_analysis_result_id === leadResultId
  );
  if (isResponseScopedAnswer) return false;
  return message.analysis_result_id === leadResultId ||
    metadata?.analysis_result_id === leadResultId;
}
