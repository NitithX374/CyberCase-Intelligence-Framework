"use client";

import { useEffect, useRef, useState } from "react";
import type { CaseAnalysisResultRead, CaseSourceRead, ChatMessageRead } from "@/lib/api";
import type { SourceMessageRef } from "@/lib/caseOverview/types";
import {
  asArray,
  asRecord,
  asStringArray,
  parseCaseCitations,
  parseCaseSources,
  sourceRefs,
} from "@/lib/caseOverview/source";
import { Icon } from "@/components/common/icons";
import { StatusPill } from "@/components/common/StatusPill";
import { ChatMessageMarkdown } from "./ChatMessageMarkdown";
import { SourceDrawer } from "@/components/sources/SourceDrawer";
import { SourceCitationChip } from "@/components/sources/SourceCitationChip";

interface ChatTranscriptProps {
  messages: ChatMessageRead[];
  isProcessing: boolean;
  /** The send in flight answers a question, so an analysis follows it. */
  isAnsweringQuestion?: boolean;
  leadResult?: CaseAnalysisResultRead | null;
  sources?: CaseSourceRead[] | null;
  onNavigateToSource?: (messageId: string) => void;
}

export function ChatTranscript({
  messages,
  isProcessing,
  isAnsweringQuestion = false,
  leadResult,
  sources,
  onNavigateToSource,
}: ChatTranscriptProps) {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  const initialMessageIdsRef = useRef<Set<string> | null>(null);
  const leadResultIdRef = useRef<string | null>(leadResult?.id ?? null);

  useEffect(() => {
    if (leadResultIdRef.current !== (leadResult?.id ?? null)) {
      leadResultIdRef.current = leadResult?.id ?? null;
      initialMessageIdsRef.current =
        messages.length > 0 ? new Set(messages.map((message) => message.id)) : null;
      return;
    }
    if (!initialMessageIdsRef.current) {
      if (messages.length === 0) return;
      initialMessageIdsRef.current = new Set(messages.map((message) => message.id));
      return;
    }
    const hasNewMessage = messages.some(
      (message) => !initialMessageIdsRef.current?.has(message.id),
    );
    if (!hasNewMessage && !isProcessing) return;
    initialMessageIdsRef.current = new Set(messages.map((message) => message.id));
    bottomRef.current?.scrollIntoView?.({ behavior: "smooth" });
  }, [isProcessing, leadResult?.id, messages]);

  if (messages.length === 0 && !leadResult) {
    return (
      <div className="flex h-full min-h-[400px] flex-col items-center justify-center p-8 text-center">
        <div className="max-w-md space-y-3 border-l-2 border-source/50 px-5 py-2 text-left">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-source/10 text-source">
            <Icon name="chat" className="h-5 w-5" />
          </div>
          <h3 className="text-base font-bold tracking-tight text-ink">Ask about this case</h3>
          <p className="text-xs leading-relaxed text-ink-secondary">
            Ask about the current Case Analysis Result or add information that should become part of
            the case material.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-4xl space-y-1 px-4 py-4 md:px-5 md:py-6">
      {messages.length === 0 && leadResult && (
        <div className="rounded-md border border-line bg-surface/40 p-4 text-center text-xs text-ink-muted">
          Ask a question below to explore the case analysis or review details.
        </div>
      )}
      {messages.map((message) => {
        const isUser = message.role === "user";
        // A message that names a gap is the analysis asking about it, and the
        // reply becomes case material — which the reader has to be told.
        const isQuestion = Boolean(message.gap_key);
        return (
          <article
            key={message.id}
            className="border-b border-line py-5 first:pt-1 last:border-b-0"
          >
            <header className="flex items-center gap-2 text-[11px] font-semibold text-ink-muted">
              <span
                className={isUser ? "text-ink" : isQuestion ? "text-unresolved" : "text-source"}
              >
                {isUser ? "You" : isQuestion ? "CyberCase · One more detail" : "CyberCase"}
              </span>
            </header>

            <div
              className={`mt-3 ${
                isUser
                  ? "ml-auto max-w-[90%] rounded-md bg-primary px-4 py-3 text-ivory sm:max-w-[82%] sm:px-5"
                  : isQuestion
                    ? "border-l-2 border-unresolved bg-unresolved/5 py-3 pl-4 pr-3 sm:pl-5"
                    : "border-l-2 border-source/50 pl-4 pr-1 sm:pl-5"
              }`}
            >
              {isUser ? (
                <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</p>
              ) : (
                <>
                  <ChatMessageMarkdown content={message.content} />
                  {isQuestion && (
                    <p className="mt-2 text-[11px] leading-relaxed text-ink-secondary">
                      ตอบในช่องข้างล่างได้เลย คำตอบจะถูกเพิ่มเป็นข้อมูลของคดีแล้ววิเคราะห์ใหม่
                    </p>
                  )}
                  <AnalysisSourceReferences
                    analysisMessage={message}
                    sources={sources ?? []}
                    onNavigateToSource={onNavigateToSource}
                  />
                </>
              )}
            </div>
          </article>
        );
      })}

      {isProcessing && (
        <div className="flex items-center gap-2 px-1 py-5 text-xs font-semibold text-ink-secondary">
          {isAnsweringQuestion ? (
            <>
              <StatusPill tone="attention">Analysing</StatusPill>
              <span>
                Adding your answer to the case and analysing it again — this takes a moment.
              </span>
            </>
          ) : (
            <>
              <StatusPill tone="source">Answering</StatusPill>
              <span>Reading the current analysis…</span>
            </>
          )}
        </div>
      )}

      <div ref={bottomRef} aria-hidden="true" />
    </div>
  );
}

interface AnalysisSourceReference {
  role: "supporting" | "conflicting";
  source: SourceMessageRef;
}

function sourceReferencesForAnalysisMessage(
  analysisMessage: ChatMessageRead,
  rows: CaseSourceRead[],
): AnalysisSourceReference[] {
  if (analysisMessage.role !== "assistant") return [];
  const trace = asRecord(analysisMessage.metadata_json.analysis_trace);
  if (trace?.version !== "case_analysis_trace_v1" || trace.validation_status !== "validated")
    return [];
  const sources = parseCaseSources(rows);
  const references = asArray(trace.claims).flatMap((value) => {
    const claim = asRecord(value);
    if (!claim) return [];
    const supportingIds = asStringArray(claim.supporting_source_ids);
    const contradictingIds = asStringArray(claim.contradicting_source_ids);
    return [
      ...sourceRefs(
        supportingIds,
        parseCaseCitations(claim.supporting_citations, supportingIds, sources),
        sources,
      ).map((source) => ({ role: "supporting" as const, source })),
      ...sourceRefs(
        contradictingIds,
        parseCaseCitations(claim.contradicting_citations, contradictingIds, sources),
        sources,
      ).map((source) => ({ role: "conflicting" as const, source })),
    ];
  });
  const unique = new Map<string, AnalysisSourceReference>();
  for (const reference of references) {
    const key = [
      reference.role,
      reference.source.id,
      reference.source.exactQuote ?? "",
      reference.source.pageNumbers.join(","),
    ].join(":");
    if (!unique.has(key)) unique.set(key, reference);
  }
  return [...unique.values()].slice(0, 12);
}

function AnalysisSourceReferences({
  analysisMessage,
  sources,
  onNavigateToSource,
}: {
  analysisMessage: ChatMessageRead;
  sources: CaseSourceRead[];
  onNavigateToSource?: (messageId: string) => void;
}) {
  const references = sourceReferencesForAnalysisMessage(analysisMessage, sources);
  const [active, setActive] = useState<{
    key: string;
    source: SourceMessageRef;
    anchor: HTMLElement;
    role: "supporting" | "conflicting";
  } | null>(null);
  if (references.length === 0) return null;

  return (
    <div className="mt-4 border-t border-line/70 pt-3">
      <p className="text-[10px] font-semibold tracking-[0.04em] text-ink-muted">
        Source references
      </p>
      <div className="mt-2 flex flex-wrap gap-1.5">
        {references.map((reference, index) => {
          const key = `${reference.role}-${reference.source.id}-${index}`;
          return (
            <SourceCitationChip
              key={key}
              sourceRef={reference.source}
              sourceKey={key}
              isActive={active?.key === key}
              citationRole={reference.role}
              onSelect={(source, anchor, sourceKey) =>
                setActive((current) =>
                  current?.key === sourceKey
                    ? null
                    : { key: sourceKey, source, anchor, role: reference.role },
                )
              }
            />
          );
        })}
      </div>
      {active && (
        <SourceDrawer
          sourceRef={active.source}
          anchorElement={active.anchor}
          onClose={() => setActive(null)}
          citationRole={active.role}
          onNavigateToSource={onNavigateToSource}
        />
      )}
    </div>
  );
}
