"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { CaseAnalysisResultRead, CaseSourceRead, ChatMessageRead } from "@/lib/api";
import type { SourceMessageRef } from "@/features/sources/types";
import { asArray, asRecord, asStringArray } from "@/lib/parse";
import { parseCaseCitations, parseCaseSources, sourceRefs } from "@/features/sources/sourceRefs";
import { Icon } from "@/components/icons";
import { ChatMessageMarkdown } from "./ChatMessageMarkdown";
import { SourceDrawer } from "@/features/sources/SourceDrawer";
import { SourceCitationChip } from "@/features/sources/SourceCitationChip";

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
  const uniqueSources = useMemo(
    () => [...new Map((sources ?? []).map((source) => [source.id, source])).values()],
    [sources],
  );

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

  if (messages.length === 0) {
    return (
      <div className="flex h-full min-h-[320px] flex-col items-center justify-center px-8 text-center">
        <span className="flex h-10 w-10 items-center justify-center rounded-full bg-surface-nested text-ink-muted">
          <Icon name="chat" className="h-5 w-5" />
        </span>
        <p className="mt-3 max-w-60 text-sm leading-6 text-ink-muted">
          {leadResult
            ? "Ask about the findings, the sources, or what is still missing."
            : "Ask anything about this case."}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6 px-5 py-6">
      {messages.map((message) => {
        const isUser = message.role === "user";
        const isQuestion = Boolean(message.gap_key);

        if (isUser) {
          return (
            <article key={message.id} className="flex justify-end">
              <p className="max-w-[88%] rounded-2xl rounded-br-md bg-surface-nested px-4 py-2.5 text-[15px] leading-7 whitespace-pre-wrap text-ink [overflow-wrap:anywhere]">
                {message.content}
              </p>
            </article>
          );
        }

        if (isQuestion) {
          return (
            <article
              key={message.id}
              className="rounded-xl border border-unresolved/25 bg-unresolved/[0.05] px-4 py-3"
            >
              <p className="mb-1 flex items-center gap-1.5 text-xs font-semibold text-unresolved">
                <Icon name="chat" className="h-3.5 w-3.5" />
                Question
              </p>
              <ChatMessageMarkdown content={message.content} />
            </article>
          );
        }

        return (
          <article key={message.id}>
            <ChatMessageMarkdown content={message.content} />
            <AnalysisSourceReferences
              analysisMessage={message}
              sources={uniqueSources}
              onNavigateToSource={onNavigateToSource}
            />
          </article>
        );
      })}

      {isProcessing && (
        <div role="status" className="flex items-center gap-2.5 text-[13px] text-ink-muted">
          <TypingDots />
          {isAnsweringQuestion ? (
            <span>Updating the analysis with your answer…</span>
          ) : (
            <span className="sr-only">Answering…</span>
          )}
        </div>
      )}

      <div ref={bottomRef} aria-hidden="true" />
    </div>
  );
}

function TypingDots() {
  return (
    <span className="inline-flex items-center gap-1" aria-hidden="true">
      {[0, 150, 300].map((delay) => (
        <span
          key={delay}
          className="h-1.5 w-1.5 rounded-full bg-ink-muted/60 motion-safe:animate-bounce"
          style={{ animationDelay: `${delay}ms` }}
        />
      ))}
    </span>
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
    const key = [reference.role, reference.source.id, reference.source.pageNumbers.join(",")].join(
      ":",
    );
    if (!unique.has(key)) {
      unique.set(key, reference);
    }
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
    <div className="mt-3 flex flex-wrap gap-1.5" aria-label="Source references" role="group">
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
