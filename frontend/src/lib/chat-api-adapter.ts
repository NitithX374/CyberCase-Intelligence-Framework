import type { ChatThreadDetail } from "./apiTypes";
import type { ChatThreadDetail as ChatThreadDetailWire } from "./generated/chatTypes";

export function normalizeChatThreadDetail(
  detail: ChatThreadDetailWire,
): ChatThreadDetail {
  return {
    ...detail,
    messages: detail.messages ?? [],
    retry_request: detail.retry_request ?? null,
  };
}
