"use client";

import { Fragment, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import Link from "next/link";
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
import { groupSourceRefs } from "@/features/citations/groupSourceRefs";
import { continuousPassages } from "@/features/citations/continuousPassages";
import { quotedPassage } from "@/features/citations/quotedPassage";
import { SourceText } from "@/features/citations/SourceText";
import {
  checkedSources,
  UNCONFIRMED_NOTES,
  unconfirmedStatuses,
  type UnconfirmedStatus,
} from "@/features/citations/unconfirmed";
import { gapTopic } from "@/features/analysis/overview";
import * as Popover from "@radix-ui/react-popover";
import { Markdown } from "@/components/Markdown";
import { Icon } from "@/components/icons";
import { hasThai } from "@/lib/language";
import { formatDate } from "@/lib/format";
import { analysisPath } from "@/lib/casePaths";

interface ChatTranscriptProps {
  messages: ChatMessageRead[];
  isProcessing: boolean;
  isAnsweringQuestion?: boolean;
  leadResult?: CaseAnalysisResultRead | null;
  sources?: CaseSourceRead[] | null;
  pendingQuestionId?: string | null;
  onSuggest?: (question: string) => void;
}

type CitationRole = "supporting" | "conflicting";

interface Reference {
  role: CitationRole;
  source: SourceMessageRef;
}

interface Mark {
  number: number;
  reference: Reference;
}

interface Statement {
  text: string;
  notes: string[];
  unconfirmed: UnconfirmedStatus[];
  marks: Mark[];
}

interface Answer {
  statements: Statement[];
  entries: Mark[];
}

interface Peek {
  messageId: string;
  position: number;
}

interface Reading {
  messageId: string;
  number: number;
}

const SUGGESTIONS = {
  thai: [
    "สรุปเหตุการณ์ตามลำดับเวลา",
    "ใครเกี่ยวข้องกับเคสนี้บ้าง และมีบทบาทอะไร",
    "เคสนี้ยังขาดข้อมูลอะไรบ้าง",
  ],
  english: [
    "Summarize what happened, in order",
    "Who is involved, and in what role?",
    "What is still missing from this case?",
  ],
};

export function ChatTranscript({
  messages,
  isProcessing,
  isAnsweringQuestion = false,
  leadResult,
  sources,
  pendingQuestionId = null,
  onSuggest,
}: ChatTranscriptProps) {
  const scrollerRef = useRef<HTMLDivElement | null>(null);
  const openerRef = useRef<HTMLElement | null>(null);
  const [peek, setPeek] = useState<Peek | null>(null);
  const [reading, setReading] = useState<Reading | null>(null);

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

  const answers = useMemo(() => {
    const citable = parseCaseSources(sources ?? [], chatFollowups(messages));
    return new Map(
      messages
        .filter((message) => message.role !== "user" && !message.gap_key)
        .map((message) => [message.id, answerOf(message, citable)]),
    );
  }, [messages, sources]);

  const readingAnswer = reading ? answers.get(reading.messageId) : undefined;
  const readingEntry = readingAnswer?.entries.find((entry) => entry.number === reading?.number);

  const openReader = (messageId: string, number: number, opener: HTMLElement) => {
    openerRef.current = opener;
    setReading({ messageId, number });
  };

  const closeReader = () => {
    setReading(null);
    window.requestAnimationFrame(() => {
      if (openerRef.current?.isConnected) openerRef.current.focus();
    });
  };

  const thai = (sources ?? []).some((source) => hasThai(source.exact_text));
  const hasSources = Boolean(sources?.length);

  return (
    <div className="relative flex min-h-0 flex-1 flex-col">
      <div
        ref={scrollerRef}
        aria-hidden={readingEntry ? true : undefined}
        inert={readingEntry ? true : undefined}
        className="min-h-0 flex-1 overflow-y-auto"
      >
        {messages.length === 0 ? (
          <div className="px-5 py-6">
            <p className="text-sm leading-6 text-ink-secondary">
              {leadResult
                ? "Ask about the findings, the sources, or what is still missing."
                : "Ask anything about this case."}
            </p>
            {onSuggest && hasSources && (
              <ul aria-label="Suggested questions" className="mt-4 border-t border-line">
                {(thai ? SUGGESTIONS.thai : SUGGESTIONS.english).map((question) => (
                  <li key={question}>
                    <button
                      type="button"
                      onClick={() => onSuggest(question)}
                      className="group flex w-full items-center justify-between gap-3 border-b border-line px-1 py-2.5 text-left text-sm text-ink transition-colors hover:bg-surface-hover"
                    >
                      {question}
                      <Icon name="chevron" className="h-4 w-4 shrink-0 -rotate-90 text-ink-muted" />
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        ) : (
          <Messages
            messages={messages}
            answers={answers}
            isProcessing={isProcessing}
            isAnsweringQuestion={isAnsweringQuestion}
            pendingQuestionId={pendingQuestionId}
            peek={peek}
            onPeek={setPeek}
            onRead={openReader}
          />
        )}
      </div>
      {readingAnswer && readingEntry && reading && (
        <SourceReader
          entry={readingEntry}
          total={readingAnswer.entries.length}
          onBack={closeReader}
          onStep={(step) => {
            const count = readingAnswer.entries.length;
            setReading({
              messageId: reading.messageId,
              number: ((reading.number - 1 + step + count) % count) + 1,
            });
          }}
        />
      )}
    </div>
  );
}

function Messages({
  messages,
  answers,
  isProcessing,
  isAnsweringQuestion,
  pendingQuestionId,
  peek,
  onPeek,
  onRead,
}: {
  messages: ChatMessageRead[];
  answers: Map<string, Answer>;
  isProcessing: boolean;
  isAnsweringQuestion: boolean;
  pendingQuestionId: string | null;
  peek: Peek | null;
  onPeek: (peek: Peek | null) => void;
  onRead: (messageId: string, number: number, opener: HTMLElement) => void;
}) {
  const questions = messages.filter((message) => message.gap_key);

  const item = (message: ChatMessageRead) => {
    if (message.role === "user") {
      return (
        <article key={message.id} className="rise-in flex justify-end">
          <p className="max-w-[85%] rounded-2xl rounded-br-md bg-espresso px-4 py-2.5 text-base leading-7 whitespace-pre-wrap text-white [overflow-wrap:anywhere]">
            {message.content}
          </p>
        </article>
      );
    }

    if (message.gap_key) {
      const number = questions.filter(
        (question) =>
          question.analysis_result_id === message.analysis_result_id &&
          question.ordinal <= message.ordinal,
      ).length;
      const waiting = message.id === pendingQuestionId;
      return (
        <article
          key={message.id}
          className={`rise-in ${waiting ? "rounded-xl border border-line-strong bg-surface px-4 py-3" : ""}`}
        >
          <Speaker
            name={`Question ${number} · ${gapTopic(message.gap_key, message.gap_key)}`}
            time={message.created_at}
            accent={waiting}
          />
          <Markdown content={message.content} />
          {waiting && (
            <p className="mt-2 text-xs text-ink-muted">Answer below, or press Don&apos;t know.</p>
          )}
        </article>
      );
    }

    const answer = answers.get(message.id);
    if (!answer) return null;
    const fromAnalysis =
      !message.in_reply_to_message_id && Boolean(message.metadata_json.analysis_trace);
    const body = (
      <AnswerBody
        messageId={message.id}
        answer={answer}
        peek={peek?.messageId === message.id ? peek.position : null}
        onPeek={(position) =>
          onPeek(position === null ? null : { messageId: message.id, position })
        }
        onRead={(number, opener) => onRead(message.id, number, opener)}
      />
    );

    if (fromAnalysis) {
      const thai = hasThai(message.content);
      return (
        <article key={message.id} className="rise-in">
          <Speaker
            name={thai ? "จากการวิเคราะห์" : "From the analysis"}
            time={message.created_at}
            accent
          >
            <Link
              href={analysisPath(message.case_id)}
              className="ml-auto inline-flex items-center gap-0.5 font-medium text-ink-secondary hover:text-ink hover:underline"
            >
              {thai ? "เปิดข้อค้นพบ" : "Open findings"}
              <Icon name="chevron" className="h-3.5 w-3.5 -rotate-90" />
            </Link>
          </Speaker>
          <div className="rounded-xl border border-line bg-surface-nested px-4 py-3">{body}</div>
        </article>
      );
    }

    return (
      <article key={message.id} className="rise-in">
        <Speaker name="Answer" time={message.created_at} />
        {body}
        <SuggestionLine suggestion={message.metadata_json.suggestion} />
      </article>
    );
  };

  return (
    <div className="space-y-6 px-5 py-6">
      {messages.flatMap((message, index) => {
        const day = formatDate(message.created_at);
        const newDay = index === 0 || day !== formatDate(messages[index - 1].created_at);
        return [
          newDay ? (
            <p
              key={`${message.id}-day`}
              className="flex items-center gap-3 text-xs text-ink-muted before:h-px before:flex-1 before:bg-line after:h-px after:flex-1 after:bg-line"
            >
              {day}
            </p>
          ) : null,
          item(message),
        ];
      })}

      {isProcessing && (
        <Working
          label={isAnsweringQuestion ? "Updating the analysis with your answer…" : "Answering…"}
        />
      )}
    </div>
  );
}

function Speaker({
  name,
  time,
  accent = false,
  children,
}: {
  name: string;
  time: string;
  accent?: boolean;
  children?: ReactNode;
}) {
  return (
    <p className="mb-1.5 flex items-center gap-1.5 text-xs">
      <span className={`font-semibold ${accent ? "text-primary" : "text-ink"}`}>{name}</span>
      <span className="text-ink-muted">· {formatDate(time, "time")}</span>
      {children}
    </p>
  );
}

function Working({ label }: { label: string }) {
  const [seconds, setSeconds] = useState(0);
  useEffect(() => {
    const timer = window.setInterval(() => setSeconds((value) => value + 1), 1000);
    return () => window.clearInterval(timer);
  }, []);
  return (
    <div role="status" className="flex items-center gap-2.5 text-sm text-ink-secondary">
      <span className="h-4 w-4 shrink-0 animate-spin rounded-full border-2 border-line-strong border-t-primary motion-reduce:animate-none" />
      <span>{label}</span>
      {seconds > 0 && <span className="text-xs text-ink-muted tabular-nums">{seconds}s</span>}
    </div>
  );
}

function AnswerBody({
  messageId,
  answer,
  peek,
  onPeek,
  onRead,
}: {
  messageId: string;
  answer: Answer;
  peek: number | null;
  onPeek: (position: number | null) => void;
  onRead: (number: number, opener: HTMLElement) => void;
}) {
  const flat = answer.statements.flatMap((statement, index) =>
    statement.marks.map((mark) => ({ ...mark, statement: index })),
  );

  return (
    <>
      <div className="space-y-3">
        {answer.statements.map((statement, index) => (
          <div key={index}>
            <div className="[&>div]:inline [&>div>p:last-child]:inline">
              <Markdown content={statement.text} />
              {statement.marks.length > 0 && (
                <sup className="ml-0.5 whitespace-nowrap text-xs">
                  {statement.marks.map((mark, position) => {
                    const flatIndex = flat.findIndex(
                      (item) => item.statement === index && item.number === mark.number,
                    );
                    const isOpen = peek === flatIndex;
                    return (
                      <Fragment key={mark.number}>
                        {position > 0 && ","}
                        <Popover.Root
                          open={isOpen}
                          onOpenChange={(next) => onPeek(next ? flatIndex : null)}
                        >
                          <Popover.Trigger asChild>
                            <button
                              id={`${messageId}-cite-${flatIndex}`}
                              type="button"
                              aria-label={`Source ${mark.number}: ${referenceLabel(mark.reference)}`}
                              className={`rounded-sm px-0.5 font-semibold tabular-nums transition-colors hover:underline ${
                                isOpen
                                  ? "bg-primary text-ivory hover:no-underline"
                                  : mark.reference.role === "conflicting"
                                    ? "text-critical"
                                    : "text-primary"
                              }`}
                            >
                              {mark.number}
                            </button>
                          </Popover.Trigger>
                          <Popover.Portal>
                            <Popover.Content
                              side="bottom"
                              align="start"
                              sideOffset={6}
                              collisionPadding={12}
                              aria-label={`Source ${mark.number}`}
                              className="pop-in z-50 w-[min(24rem,calc(100vw-2rem))] rounded-lg border border-line-strong bg-surface p-3 shadow-lg shadow-black/10 outline-none [--origin:top_left]"
                            >
                              <CitationPeek
                                mark={mark}
                                position={flatIndex}
                                total={flat.length}
                                onStep={(step) =>
                                  onPeek((flatIndex + step + flat.length) % flat.length)
                                }
                                onClose={() => onPeek(null)}
                                onRead={() => {
                                  const trigger = document.getElementById(
                                    `${messageId}-cite-${flatIndex}`,
                                  );
                                  onPeek(null);
                                  if (trigger) onRead(mark.number, trigger);
                                }}
                              />
                            </Popover.Content>
                          </Popover.Portal>
                        </Popover.Root>
                      </Fragment>
                    );
                  })}
                </sup>
              )}
            </div>
            {statement.notes.map((note) => (
              <p key={note} className="mt-1 text-xs text-ink-muted">
                {note}
              </p>
            ))}
            {statement.unconfirmed.map((status) => (
              <p key={status} className="mt-1 text-xs text-ink-muted">
                {UNCONFIRMED_NOTES[status]}
              </p>
            ))}
          </div>
        ))}
      </div>
      {answer.entries.length > 0 && (
        <ol aria-label="Sources" className="mt-4 border-t border-line">
          {answer.entries.map((entry) => (
            <li key={entry.number}>
              <button
                type="button"
                aria-label={referenceLabel(entry.reference)}
                onClick={(event) => onRead(entry.number, event.currentTarget)}
                className="group flex w-full items-baseline gap-2.5 border-b border-line px-1 py-2 text-left text-sm text-ink-secondary transition-colors hover:bg-surface-hover hover:text-ink"
              >
                <span
                  className={`w-4 shrink-0 font-semibold tabular-nums ${
                    entry.reference.role === "conflicting" ? "text-critical" : "text-primary"
                  }`}
                >
                  {entry.number}
                </span>
                <span className="min-w-0 flex-1 truncate">
                  {entry.reference.role === "conflicting" && (
                    <span className="text-critical">Conflicts · </span>
                  )}
                  {entry.reference.source.label}
                </span>
                <Icon
                  name="chevron"
                  className="h-4 w-4 shrink-0 self-center -rotate-90 text-ink-muted"
                />
              </button>
            </li>
          ))}
        </ol>
      )}
    </>
  );
}

function CitationPeek({
  mark,
  position,
  total,
  onStep,
  onClose,
  onRead,
}: {
  mark: Mark;
  position: number;
  total: number;
  onStep: (step: number) => void;
  onClose: () => void;
  onRead: () => void;
}) {
  const passages = continuousPassages(mark.reference.source);
  return (
    <>
      <div className="flex items-center gap-2 text-xs text-ink-secondary">
        <span className="min-w-0 flex-1 truncate">
          {mark.reference.role === "conflicting" && (
            <span className="font-medium text-critical">Conflicts · </span>
          )}
          {mark.reference.source.label}
        </span>
        {total > 1 && (
          <span className="flex shrink-0 items-center tabular-nums">
            <StepButton label="Previous citation" direction="previous" onClick={() => onStep(-1)} />
            {position + 1}/{total}
            <StepButton label="Next citation" direction="next" onClick={() => onStep(1)} />
          </span>
        )}
        <button
          type="button"
          onClick={onClose}
          aria-label="Close citation"
          className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md text-ink-muted transition-colors hover:bg-surface-hover hover:text-ink"
        >
          <Icon name="close" className="h-4 w-4" />
        </button>
      </div>
      {passages.length > 0 ? (
        passages.slice(0, 3).map((cited, index) => {
          const passage = quotedPassage(cited.quote, cited.context);
          return (
            <p
              key={index}
              className="mt-2 line-clamp-5 border-l-2 border-primary pl-2.5 text-sm leading-6 whitespace-pre-wrap text-ink-muted [overflow-wrap:anywhere]"
            >
              {passage.before}
              <span className="text-ink">{passage.quote}</span>
              {passage.after}
            </p>
          );
        })
      ) : (
        <p className="mt-2 text-sm text-ink-muted">Cited as a whole, without a marked passage.</p>
      )}
      {passages.length > 3 && (
        <p className="mt-2 text-xs text-ink-muted">
          {passages.length - 3} more {passages.length - 3 === 1 ? "passage" : "passages"} in the
          source
        </p>
      )}
      <button
        type="button"
        onClick={onRead}
        className="mt-2 inline-flex items-center gap-1 text-sm font-semibold text-ink hover:underline"
      >
        Show in the full source
        <Icon name="chevron" className="h-4 w-4 -rotate-90" />
      </button>
    </>
  );
}

function SourceReader({
  entry,
  total,
  onBack,
  onStep,
}: {
  entry: Mark;
  total: number;
  onBack: () => void;
  onStep: (step: number) => void;
}) {
  const backRef = useRef<HTMLButtonElement>(null);
  const source = entry.reference.source;
  const title = source.filename ?? source.label;

  useEffect(() => {
    backRef.current?.focus();
  }, []);

  return (
    <section
      aria-label={`Source: ${title}`}
      onKeyDown={(event) => {
        if (event.key === "Escape") onBack();
      }}
      className="panel-in absolute inset-0 z-10 flex flex-col bg-surface"
    >
      <div className="flex h-12 shrink-0 items-center justify-between gap-2 border-b border-line px-3">
        <button
          ref={backRef}
          type="button"
          onClick={onBack}
          className="flex items-center gap-1 rounded-md px-2 py-1 text-sm font-medium text-ink-secondary transition-colors hover:bg-surface-hover hover:text-ink"
        >
          <Icon name="chevron" className="h-4 w-4 rotate-90" />
          Back to answer
        </button>
        {total > 1 && (
          <span className="flex items-center text-sm text-ink-secondary tabular-nums">
            <StepButton label="Previous source" direction="previous" onClick={() => onStep(-1)} />
            {entry.number} of {total}
            <StepButton label="Next source" direction="next" onClick={() => onStep(1)} />
          </span>
        )}
      </div>
      <div
        className="min-h-0 flex-1 overflow-y-auto px-5 py-4"
        tabIndex={0}
        aria-label="Source text"
      >
        {entry.reference.role === "conflicting" && (
          <p className="mb-1 text-xs font-medium text-critical">Conflicts with the answer</p>
        )}
        <h3 className="text-base font-semibold leading-6 [overflow-wrap:anywhere]">{title}</h3>
        {source.label !== title && <p className="text-sm text-ink-muted">{source.label}</p>}
        <div className="mt-4">
          <SourceText key={`${source.id}:${entry.number}`} sourceRef={source} />
        </div>
      </div>
    </section>
  );
}

function StepButton({
  label,
  direction,
  onClick,
}: {
  label: string;
  direction: "previous" | "next";
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      aria-label={label}
      onClick={onClick}
      className="flex h-7 w-7 items-center justify-center rounded-md text-ink-muted transition-colors hover:bg-surface-hover hover:text-ink"
    >
      <Icon
        name="chevron"
        className={`h-4 w-4 ${direction === "previous" ? "rotate-90" : "-rotate-90"}`}
      />
    </button>
  );
}

const INLINE_CITATION_RE =
  /\s*\[\s*(?:(?:A|QA|C)-\d+|[A-Z]\d+)(?:\s*[,;]\s*(?:(?:A|QA|C)-\d+|[A-Z]\d+))*\s*\]/gi;

function stripInlineCitations(text: string): string {
  if (!text) return "";
  return text
    .replace(INLINE_CITATION_RE, "")
    .replace(/ +/g, " ")
    .replace(/ ([.,;:!?])/g, "$1")
    .trim();
}

const PRELIMINARY_NOTE = "เป็นการตีความเบื้องต้น ยังไม่ได้ผ่านการวิเคราะห์";
const UNBOUND_UNITS_NOTE = "ข้อความบางส่วนที่อ้างไว้หาไม่พบใน Source";

const SUGGESTION_LINES: Record<string, string> = {
  add_source: "เพิ่มเป็น Source ที่หน้า Sources เพื่อให้การวิเคราะห์ใช้ข้อมูลนี้",
  run_analysis: "กด Analyze เพื่อวิเคราะห์เคสอีกครั้ง",
};

function SuggestionLine({ suggestion }: { suggestion?: string }) {
  const line = suggestion ? SUGGESTION_LINES[suggestion] : undefined;
  if (!line) return null;
  return <p className="mt-3 text-sm text-ink-muted">{line}</p>;
}

function referenceLabel(reference: Reference): string {
  return reference.role === "conflicting"
    ? `Conflicts with ${reference.source.label}`
    : reference.source.label;
}

function referenceKey(reference: Reference): string {
  return [reference.role, reference.source.id, reference.source.pageNumbers.join(",")].join(":");
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

function answerOf(message: ChatMessageRead, sources: CaseSourceRef[]): Answer {
  const units = message.metadata_json.answer_units ?? [];
  const claims = message.metadata_json.analysis_trace?.claims ?? [];
  const statuses = new Map(claims.map((claim) => [claim.claim_id, claim.epistemic_status]));
  const raw = units.length
    ? units.map((unit) => ({
        text: stripInlineCitations(unit.text),
        notes: [
          ...(unit.basis === "interpretation" ? [PRELIMINARY_NOTE] : []),
          ...((unit.invalid_evidence?.length ?? 0) > 0 ? [UNBOUND_UNITS_NOTE] : []),
        ],
        items: [unitItem(unit, statuses)],
      }))
    : [{ text: stripInlineCitations(message.content), notes: [], items: claims.map(claimItem) }];

  const groups = new Map<
    string,
    { number: number; role: CitationRole; refs: SourceMessageRef[] }
  >();
  const statements = raw.map(({ text, notes, items }): Statement => ({
    text,
    notes,
    unconfirmed: unconfirmedStatuses(items.flatMap((item) => item.unconfirmed)),
    marks: citedReferences(items, sources).map((reference) => {
      const key = referenceKey(reference);
      const group = groups.get(key) ?? { number: groups.size + 1, role: reference.role, refs: [] };
      group.refs.push(reference.source);
      groups.set(key, group);
      return { number: group.number, reference };
    }),
  }));
  const entries = [...groups.values()].map((group) => ({
    number: group.number,
    reference: { role: group.role, source: groupSourceRefs(group.refs)[0] },
  }));
  return { statements, entries };
}

function citedReferences(items: CitedItem[], sources: CaseSourceRef[]): Reference[] {
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
  const unique = new Map<string, Reference>();
  for (const reference of references) {
    const key = referenceKey(reference);
    const known = unique.get(key);
    unique.set(
      key,
      known
        ? { role: known.role, source: groupSourceRefs([known.source, reference.source])[0] }
        : reference,
    );
  }
  return [...unique.values()].slice(0, 12);
}
