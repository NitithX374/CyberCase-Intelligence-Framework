"use client";

import { useEffect, useRef } from "react";
import type { PersistedChatMessage } from "@/lib/api";
import { caseUpdateForMessage } from "@/lib/case-update";
import { followUpGapDetailForMessage } from "@/lib/chat-followup";
import { mitreCandidatesForMessage } from "@/lib/mitre-candidate";
import { ChatMessageMarkdown } from "./ChatMessageMarkdown";
import { FollowUpExplanation } from "./FollowUpExplanation";
import { MitreCandidatePanel } from "./MitreCandidatePanel";

interface ChatTranscriptProps {
  messages: PersistedChatMessage[];
  isProcessing: boolean;
  onSelectMessageOrdinal?: (ordinal: number) => void;
}

export function ChatTranscript({
  messages,
  isProcessing,
  onSelectMessageOrdinal,
}: ChatTranscriptProps) {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length, isProcessing]);

  if (messages.length === 0) {
    return (
      <div className="flex h-full min-h-[400px] flex-col items-center justify-center p-8 text-center">
        <div className="mx-auto max-w-md">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-surface-hover text-lg font-black text-ink">
            CC
          </div>
          <h3 className="mt-4 text-base font-extrabold text-ink">
            Investigation Console
          </h3>
          <p className="mt-2 text-xs leading-relaxed text-ink-secondary">
            Describe an incident, paste security logs, or ask about threat techniques.
            CyberCase will analyze the details and identify relevant MITRE ATT&amp;CK tactics.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-3xl space-y-6 px-4 py-6 sm:px-6">
      {messages.map((message) => {
        const isUser = message.role === "user";
        const followUpGap = followUpGapDetailForMessage(message);
        const caseUpdate = isUser ? null : caseUpdateForMessage(message, messages);
        const mitreCandidates = isUser ? null : mitreCandidatesForMessage(message);
        return (
          <div
            key={message.id}
            className={`flex flex-col ${isUser ? "items-end" : "items-start w-full"}`}
          >
            <div className="flex items-center gap-2 mb-1.5 px-1">
              <span className="text-[10px] font-extrabold uppercase tracking-wider text-ink-secondary">
                {isUser ? "Analyst" : "CyberCase AI"}
              </span>
              <span className="text-[10px] text-ink-secondary">
                #{message.ordinal}
              </span>
            </div>

            <div
              className={`rounded-2xl px-4 py-3.5 shadow-[0_1px_3px_rgba(39,39,39,0.04)] sm:px-5 sm:py-4 ${
                isUser
                  ? "max-w-[85%] bg-primary text-ivory"
                  : "w-full border border-line bg-surface text-ink"
              }`}
            >
              {isUser ? (
                <p className="whitespace-pre-wrap text-sm leading-relaxed">
                  {message.content}
                </p>
              ) : (
                <>
                  <ChatMessageMarkdown content={message.content} />
                  {caseUpdate && (
                    <div className="mt-3.5 flex flex-wrap items-center justify-between gap-2 rounded-xl border border-[#D8E2DA] bg-[#F7F9F7] px-3 py-2 text-xs">
                      <div className="flex items-center gap-2">
                        <span className="inline-flex items-center gap-1.5 rounded-md bg-[#E2EAE4] px-2 py-0.5 text-[11px] font-bold text-[#3E5244]">
                          <span className="h-1.5 w-1.5 rounded-full bg-[#3E5244]" />
                          {caseUpdate.status === "updated" && caseUpdate.childVersion !== null
                            ? `Case State V${caseUpdate.parentVersion} → V${caseUpdate.childVersion}`
                            : `Case State V${caseUpdate.parentVersion} · Unchanged`}
                        </span>
                        <span className="text-[10px] font-medium text-ink-muted">
                          {caseUpdate.added.length} added · {caseUpdate.changed.length} changed
                        </span>
                      </div>
                      {onSelectMessageOrdinal && (
                        <button
                          type="button"
                          onClick={() => onSelectMessageOrdinal(message.ordinal)}
                          className="inline-flex items-center gap-1 text-[11px] font-bold text-primary hover:underline cursor-pointer"
                        >
                          <span>View in panel</span>
                          <span aria-hidden="true">→</span>
                        </button>
                      )}
                    </div>
                  )}
                  {followUpGap && <FollowUpExplanation detail={followUpGap} />}
                  {mitreCandidates && (
                    <MitreCandidatePanel candidates={mitreCandidates} />
                  )}
                </>
              )}
            </div>
          </div>
        );
      })}

      {isProcessing && (
        <div className="flex items-center gap-3 px-2 text-xs font-semibold text-ink-secondary">
          <span className="flex h-2 w-2 rounded-full bg-primary animate-ping" />
          <span>Analyzing incident details &amp; mapping MITRE intelligence...</span>
        </div>
      )}

      <div ref={bottomRef} aria-hidden="true" />
    </div>
  );
}
