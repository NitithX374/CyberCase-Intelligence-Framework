import type { PersistedChatMessage, ThreadStatus } from "@/lib/api";
import type { CaseOverviewData } from "@/lib/case-overview-contracts";
import {
  buildLegacyCaseOverview,
  isLegacyCaseOverviewMessage,
} from "@/lib/case-overview-legacy";
import {
  buildV3CaseOverview,
  isV3CaseOverviewMessage,
} from "@/lib/case-overview-v3";

export * from "@/lib/case-overview-contracts";

export function buildCaseOverview(
  messages: PersistedChatMessage[],
  threadStatus?: ThreadStatus | null,
): CaseOverviewData {
  const isProcessing =
    threadStatus === "processing" || threadStatus === "awaiting_followup";
  const assistantMessages = messages.filter((message) => message.role === "assistant");
  const v3Message = [...assistantMessages].reverse().find(isV3CaseOverviewMessage);
  if (v3Message) return buildV3CaseOverview(v3Message, messages, isProcessing);

  const legacyMessage = [...assistantMessages]
    .reverse()
    .find(isLegacyCaseOverviewMessage);
  if (legacyMessage) {
    return buildLegacyCaseOverview(legacyMessage, messages, isProcessing);
  }

  return {
    hasAnalysis: false,
    isProcessing,
    incidentSummary: "",
    findings: [],
    gaps: [],
    mitreContext: [],
    technicalContextStatus: "hidden",
    analysisMessageId: null,
    contractVersion: null,
  };
}
