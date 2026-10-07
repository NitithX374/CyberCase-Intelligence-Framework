"use client";

import { useEffect, useRef, useState } from "react";
import type {
  CaseAnalysisClaim,
  CaseAnalysisResultRead,
  CaseSourceRead,
  ChatAnswerUnit,
  ChatMessageRead,
} from "@/lib/api/types";
import type { CaseSourceRef, SourceMessageRef } from "@/features/citations/types";
import { claimRefs, parseCaseSources } from "@/features/citations/sourceRefs";
import { chatFollowups } from "@/features/citations/followupSources";
import {
  checkedSources,
  UNCONFIRMED_NOTES,
  unconfirmedStatuses,
  type UnconfirmedStatus,
} from "@/features/citations/unconfirmed";
import { Markdown } from "@/components/Markdown";
import { SourceDrawer } from "@/features/citations/SourceDrawer";
import { SourceCitationChip } from "@/features/citations/SourceCitationChip";

interface ChatTranscriptProps {
  messages: ChatMessageRead[];
  isProcessing: boolean;
  isAnsweringQuestion?: boolean;
  leadResult?: CaseAnalysisResultRead | null;
  sources?: CaseSourceRead[] | null;
}

export function ChatTranscript({
  messages,
  isProcessing,
  isAnsweringQuestion = false,
  leadResult,
  sources,
}: ChatTranscriptProps) {
  const scrollerRef = useRef<HTMLDivElement | null>(null);

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
    const scroller = scrollerRef.current;
    scroller?.scrollTo?.({ top: scroller.scrollHeight, behavior: "smooth" });
  }, [isProcessing, leadResult?.id, messages]);

  return (
    <div ref={scrollerRef} className="relative min-h-0 flex-1 overflow-y-auto">
      {messages.length === 0 ? (
        <div className="flex h-full min-h-[320px] flex-col items-center justify-center px-8 text-center">
          <p className="max-w-60 text-sm leading-6 text-ink-muted">
            {leadResult
              ? "Ask about the findings, the sources, or what is still missing."
              : "Ask anything about this case."}
          </p>
        </div>
      ) : (
        <Messages
          messages={messages}
          isProcessing={isProcessing}
          isAnsweringQuestion={isAnsweringQuestion}
          sources={sources ?? []}
        />
      )}
    </div>
  );
}

function Messages({
  messages,
  isProcessing,
  isAnsweringQuestion,
  sources,
}: {
  messages: ChatMessageRead[];
  isProcessing: boolean;
  isAnsweringQuestion: boolean;
  sources: CaseSourceRead[];
}) {
  const citable = parseCaseSources(sources, chatFollowups(messages));
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
            <article key={message.id}>
              <p className="mb-1 text-xs font-semibold text-unresolved">Question</p>
              <Markdown content={message.content} />
            </article>
          );
        }

        const units = message.metadata_json.answer_units ?? [];
        const claims = message.metadata_json.analysis_trace?.claims ?? [];
        return (
          <article key={message.id}>
            {units.length > 0 ? (
              <AnswerUnits units={units} claims={claims} sources={citable} />
            ) : (
              <>
                <Markdown content={stripInlineCitations(message.content)} />
                <AnswerReferences {...sourceReferences(claims.map(claimItem), citable)} />
              </>
            )}
            <SuggestionLine suggestion={message.metadata_json.suggestion} />
          </article>
        );
      })}

      {isProcessing && (
        <p role="status" className="text-[13px] text-ink-muted">
          {isAnsweringQuestion ? "Updating the analysis with your answer…" : "Answering…"}
        </p>
      )}
    </div>
  );
}

const INLINE_CITATION_RE =
  /\s*\[\s*(?:(?:A|QA|C)-\d+|[A-Z]\d+)(?:\s*[,;]\s*(?:(?:A|QA|C)-\d+|[A-Z]\d+))*\s*\]/gi;

export function stripInlineCitations(text: string): string {
  if (!text) return "";
  return text
    .replace(INLINE_CITATION_RE, "")
    .replace(/ +/g, " ")
    .replace(/ ([.,;:!?])/g, "$1")
    .trim();
}

const PRELIMINARY_NOTE = "เป็นการตีความเบื้องต้น ยังไม่ได้ผ่านการวิเคราะห์";

const SUGGESTION_LINES: Record<string, string> = {
  add_source: "ถ้าต้องการให้ข้อมูลนี้ถูกนำไปวิเคราะห์ ให้เพิ่มเป็น source ที่หน้า Sources",
  run_analysis: "กด Analyze เพื่อวิเคราะห์เคสอีกครั้ง",
};

function AnswerUnits({
  units,
  claims,
  sources,
}: {
  units: ChatAnswerUnit[];
  claims: CaseAnalysisClaim[];
  sources: CaseSourceRef[];
}) {
  const statuses = new Map(claims.map((claim) => [claim.claim_id, claim.epistemic_status]));
  return (
    <div className="space-y-3">
      {units.map((unit, index) => (
        <div key={index}>
          <Markdown content={stripInlineCitations(unit.text)} />
          {unit.basis === "interpretation" && (
            <p className="mt-1 text-xs text-ink-muted">{PRELIMINARY_NOTE}</p>
          )}
          <AnswerReferences {...sourceReferences([unitItem(unit, statuses)], sources)} />
        </div>
      ))}
    </div>
  );
}

function SuggestionLine({ suggestion }: { suggestion?: string }) {
  const line = suggestion ? SUGGESTION_LINES[suggestion] : undefined;
  if (!line) return null;
  return <p className="mt-3 text-[13px] text-ink-muted">{line}</p>;
}

interface AnalysisSourceReference {
  role: "supporting" | "conflicting";
  source: SourceMessageRef;
}

interface ReferenceList {
  references: AnalysisSourceReference[];
  unconfirmed: UnconfirmedStatus[];
}

type CitedItem = Parameters<typeof claimRefs>[0] & { unconfirmed: UnconfirmedStatus[] };

function claimItem(claim: CaseAnalysisClaim): CitedItem {
  return { ...claim, unconfirmed: unconfirmedStatuses([claim.epistemic_status]) };
}

function unitItem(unit: ChatAnswerUnit, statuses: Map<string, string>): CitedItem {
  return {
    ...unit,
    unconfirmed: unconfirmedStatuses((unit.claim_ids ?? []).map((id) => statuses.get(id))),
  };
}

function sourceReferences(items: CitedItem[], sources: CaseSourceRef[]): ReferenceList {
  const references = items.flatMap((item) => {
    const cited = claimRefs(item, sources);
    return [
      ...checkedSources(cited.supporting, item.unconfirmed.length > 0).map((source) => ({
        role: "supporting" as const,
        source,
      })),
      ...cited.contradicting.map((source) => ({ role: "conflicting" as const, source })),
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
  return {
    references: [...unique.values()].slice(0, 12),
    unconfirmed: unconfirmedStatuses(items.flatMap((item) => item.unconfirmed)),
  };
}

function AnswerReferences({ references, unconfirmed }: ReferenceList) {
  return (
    <>
      {unconfirmed.map((status) => (
        <p key={status} className="mt-1 text-xs text-ink-muted">
          {UNCONFIRMED_NOTES[status]}
        </p>
      ))}
      <SourceReferences references={references} />
    </>
  );
}

function SourceReferences({ references }: { references: AnalysisSourceReference[] }) {
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
        />
      )}
    </div>
  );
}
