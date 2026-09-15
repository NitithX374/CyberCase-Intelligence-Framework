export interface PendingChatSubmission {
  caseId: string;
  content: string;
  key: string;
  kind: "message" | "followup";
  lastKnownMessageOrdinal: number;
  requestOrdinal?: number;
}
