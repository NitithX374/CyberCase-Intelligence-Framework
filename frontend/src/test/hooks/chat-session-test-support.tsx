import type { CaseChatDetail, CaseChatResponse, CaseChatStatus, ChatMessageRead } from "@/lib/api";

export function message(
  caseId: string,
  ordinal: number,
  role: "user" | "assistant",
  content: string = role,
): ChatMessageRead {
  return {
    id: `${caseId}-${ordinal}`,
    case_id: caseId,
    ordinal,
    role,
    content,
    message_kind: "conversation",
    analysis_result_id: null,
    metadata_json: {},
    retrieval_context_id: null,
    created_at: "2026-09-05T00:00:00Z",
  };
}

export function caseChat(
  caseId = "a",
  status: CaseChatStatus = "idle",
  messages: ChatMessageRead[] = [],
): CaseChatDetail {
  return { case_id: caseId, status, messages };
}

export function chatResponse(...messages: ChatMessageRead[]): CaseChatResponse {
  return { messages, analysis: null };
}

/** A promise this test resolves by hand, to hold a request open. */
export function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (error: unknown) => void;
  const promise = new Promise<T>((yes, no) => {
    resolve = yes;
    reject = no;
  });
  return { promise, resolve, reject };
}
