import type { ChatMessageAction } from "@/lib/api";

export interface PendingChatSubmission {
  threadId: string;
  caseId: string;
  content: string;
  key: string;
  kind: "message" | "followup";
  action?: ChatMessageAction;
  lastKnownMessageOrdinal: number;
  requestOrdinal?: number;
}
