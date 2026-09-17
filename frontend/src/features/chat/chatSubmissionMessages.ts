import type {
  CaseChatDetail,
  CaseChatMessageResult,
  ChatMessageRead,
} from "@/lib/api";

const optimisticMessagePrefix = "optimistic:";

export function addOptimisticChatMessage(
  current: CaseChatDetail | undefined,
  caseId: string,
  content: string,
  requestKey: string,
  lastKnownMessageOrdinal: number,
): CaseChatDetail {
  const base = current ?? { case_id: caseId, status: "idle" as const, messages: [] };
  if (base.messages.some((message) => message.client_request_id === requestKey)) return base;
  const nextOrdinal = Math.max(
    lastKnownMessageOrdinal,
    ...base.messages.map((message) => message.ordinal),
  ) + 1;
  const optimisticMessage: ChatMessageRead = {
    id: optimisticMessageId(requestKey),
    case_id: caseId,
    client_request_id: requestKey,
    ordinal: nextOrdinal,
    role: "user",
    content,
    retrieval_context_id: null,
    message_kind: "conversation",
    analysis_result_id: null,
    in_reply_to_message_id: null,
    metadata_json: { action: "conversation" },
    created_at: new Date().toISOString(),
  };
  return {
    ...base,
    messages: [...base.messages, optimisticMessage].sort((a, b) => a.ordinal - b.ordinal),
  };
}

export function mergeChatMessageResult(
  current: CaseChatDetail | undefined,
  result: CaseChatMessageResult,
  requestKey: string,
  status: CaseChatDetail["status"] = "answered",
): CaseChatDetail {
  const base = current ?? { case_id: result.message.case_id, status, messages: [] };
  const incoming = [result.message, result.assistant_message, result.reply_message]
    .filter((message): message is ChatMessageRead => Boolean(message));
  const replaced = base.messages.filter((message) => (
    message.id !== optimisticMessageId(requestKey) &&
    !incoming.some((candidate) => candidate.id === message.id)
  ));
  return {
    ...base,
    status,
    messages: [...replaced, ...incoming].sort((a, b) => a.ordinal - b.ordinal),
  };
}

export function removeOptimisticChatMessage(
  current: CaseChatDetail | undefined,
  requestKey: string,
): CaseChatDetail | undefined {
  if (!current) return current;
  return {
    ...current,
    messages: current.messages.filter((message) => message.id !== optimisticMessageId(requestKey)),
  };
}

function optimisticMessageId(requestKey: string): string {
  return `${optimisticMessagePrefix}${requestKey}`;
}
