import type { CaseChatDetail } from "./apiTypes";
import type { CaseChatRead } from "./generated/chatTypes";

export function normalizeCaseChat(detail: CaseChatRead): CaseChatDetail {
  return {
    ...detail,
    messages: detail.messages ?? [],
  };
}
