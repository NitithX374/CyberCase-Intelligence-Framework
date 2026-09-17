import type {
  CaseChatStatus,
  ChatMessageRead,
} from "@/lib/api";

export type ClarificationDisposition = "answered" | "unavailable" | "skipped";

export interface ChatFollowUpEntry {
  question: string;
  answer: string;
}

export interface ChatFollowUpGapDetail {
  gapId: string;
  gapKey: string;
  topic: string;
  status:
    | "NOT_PROVIDED"
    | "EXPLICITLY_UNKNOWN"
    | "AMBIGUOUS"
    | "CONFLICTING";
  description: string;
  affects: string;
  reason: string;
  priority: "high" | "medium" | "low";
  askable: boolean;
  question: string;
}

export interface ChatFollowUpAnswer {
  gapId: string;
  answer: string | null;
  disposition: ClarificationDisposition;
}

export interface ActiveChatFollowUp {
  question: string;
  gap: ChatFollowUpGapDetail;
  entries: ChatFollowUpEntry[];
  rootOrdinal: number;
  round: number;
  questionMessageId: string;
  sourceAnalysisId: string;
  sourceRevision: number;
}

interface FollowUpMetadata {
  rootOrdinal: number;
  round: number;
  sourceAnalysisId: string;
  sourceRevision: number;
  gap: ChatFollowUpGapDetail;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

function isGapStatus(
  value: unknown,
): value is ChatFollowUpGapDetail["status"] {
  return (
    value === "NOT_PROVIDED" ||
    value === "EXPLICITLY_UNKNOWN" ||
    value === "AMBIGUOUS" ||
    value === "CONFLICTING"
  );
}

function isGapPriority(
  value: unknown,
): value is ChatFollowUpGapDetail["priority"] {
  return value === "high" || value === "medium" || value === "low";
}

function parseGap(value: unknown): ChatFollowUpGapDetail | null {
  if (!isRecord(value)) return null;
  if (
    !isNonEmptyString(value.gap_id) ||
    !isNonEmptyString(value.gap_key) ||
    !isNonEmptyString(value.topic) ||
    !isNonEmptyString(value.description) ||
    !isNonEmptyString(value.affects) ||
    !isNonEmptyString(value.reason) ||
    !isNonEmptyString(value.clarification_question) ||
    !isGapStatus(value.status) ||
    !isGapPriority(value.priority) ||
    typeof value.askable !== "boolean"
  ) {
    return null;
  }
  return {
    gapId: value.gap_id,
    gapKey: value.gap_key,
    topic: value.topic,
    status: value.status,
    description: value.description,
    affects: value.affects,
    reason: value.reason,
    priority: value.priority,
    askable: value.askable,
    question: value.clarification_question,
  };
}

function parseFollowUpMetadata(
  message: ChatMessageRead,
): FollowUpMetadata | null {
  const value: unknown = message.metadata_json.chat_followup;
  if (message.metadata_json.action !== "follow_up" || !isRecord(value)) return null;
  if (
    typeof value.root_ordinal !== "number" ||
    !Number.isInteger(value.root_ordinal) ||
    value.root_ordinal < 1 ||
    typeof value.round !== "number" ||
    !Number.isInteger(value.round) ||
    value.round < 1 ||
    !isNonEmptyString(value.source_analysis_id) ||
    typeof value.source_revision !== "number" ||
    !Number.isInteger(value.source_revision) ||
    value.source_revision < 0
  ) {
    return null;
  }
  const gap = parseGap(value.gap);
  if (gap === null) return null;
  return {
    rootOrdinal: value.root_ordinal,
    round: value.round,
    sourceAnalysisId: value.source_analysis_id,
    sourceRevision: value.source_revision,
    gap,
  };
}

export function followUpGapDetailForMessage(
  message: ChatMessageRead,
): ChatFollowUpGapDetail | null {
  return parseFollowUpMetadata(message)?.gap ?? null;
}

function orderedMessages(
  persistedMessages: ChatMessageRead[],
): ChatMessageRead[] {
  return [...persistedMessages].sort(
    (left, right) => left.ordinal - right.ordinal,
  );
}

export function isClarificationAnswer(message: ChatMessageRead): boolean {
  return (
    message.role === "user" &&
    message.message_kind !== "conversation" &&
    (message.message_kind === "followup_answer" || Boolean(message.in_reply_to_message_id))
  );
}

export function latestUserAnswerBetween(
  persistedMessages: ChatMessageRead[],
  questionOrdinal: number,
  nextAssistantOrdinal?: number,
): ChatMessageRead | null {
  const candidates = orderedMessages(persistedMessages).filter(
    (message) =>
      isClarificationAnswer(message) &&
      message.ordinal > questionOrdinal &&
      (nextAssistantOrdinal === undefined || message.ordinal < nextAssistantOrdinal),
  );
  return candidates[candidates.length - 1] ?? null;
}

export function activeCaseChatFollowUp(
  persistedMessages: ChatMessageRead[],
  status: CaseChatStatus | null,
): ActiveChatFollowUp | null {
  if (status !== "awaiting_followup") return null;
  const ordered = orderedMessages(persistedMessages);
  const annotatedQuestions = ordered
    .filter((message) => message.role === "assistant")
    .map((message) => ({ message, metadata: parseFollowUpMetadata(message) }))
    .filter(
      (
        candidate,
      ): candidate is {
        message: ChatMessageRead;
        metadata: FollowUpMetadata;
      } => candidate.metadata !== null,
    );
  const active = annotatedQuestions[annotatedQuestions.length - 1];
  if (!active) return null;
  const priorQuestions = annotatedQuestions.filter(
    (candidate) =>
      candidate.metadata.rootOrdinal === active.metadata.rootOrdinal &&
      candidate.message.ordinal < active.message.ordinal,
  );
  const entries = priorQuestions.flatMap((candidate, index) => {
    const nextQuestionOrdinal = priorQuestions[index + 1]?.message.ordinal ?? active.message.ordinal;
    const answer = latestUserAnswerBetween(
      ordered,
      candidate.message.ordinal,
      nextQuestionOrdinal,
    );
    return answer ? [{ question: candidate.message.content, answer: answer.content }] : [];
  });
  return {
    question: active.message.content,
    gap: active.metadata.gap,
    entries,
    rootOrdinal: active.metadata.rootOrdinal,
    round: active.metadata.round,
    questionMessageId: active.message.id,
    sourceAnalysisId: active.metadata.sourceAnalysisId,
    sourceRevision: active.metadata.sourceRevision,
  };
}

export function filterSupersededClarificationAnswers(
  persistedMessages: ChatMessageRead[],
): ChatMessageRead[] {
  const ordered = orderedMessages(persistedMessages);
  const supersededMessageIds = new Set<string>();
  for (const message of ordered) {
    if (message.role !== "assistant" || parseFollowUpMetadata(message) === null) continue;
    const nextAssistant = ordered.find(
      (candidate) => candidate.role === "assistant" && candidate.ordinal > message.ordinal,
    );
    const latestAnswer = latestUserAnswerBetween(ordered, message.ordinal, nextAssistant?.ordinal);
    for (const candidate of ordered) {
      if (
        isClarificationAnswer(candidate) &&
        candidate.ordinal > message.ordinal &&
        (nextAssistant === undefined || candidate.ordinal < nextAssistant.ordinal) &&
        candidate.id !== latestAnswer?.id
      ) {
        supersededMessageIds.add(candidate.id);
      }
    }
  }
  return ordered.filter((message) => !supersededMessageIds.has(message.id));
}

export function chatTranscriptMessages(
  persistedMessages: ChatMessageRead[],
): ChatMessageRead[] {
  return filterSupersededClarificationAnswers(persistedMessages);
}
