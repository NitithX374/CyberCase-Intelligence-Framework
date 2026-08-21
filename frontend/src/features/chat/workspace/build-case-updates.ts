import type { PersistedChatMessage } from "@/lib/api";
import { caseUpdateForMessage, latestValidatedGaps, type CaseUpdateView } from "@/lib/case-update";
import { mitreCandidatesForMessage } from "@/lib/mitre-candidate";
import type { CaseStateInspectorUpdate } from "@/components/conversation/CaseStateInspector";

export function buildCaseUpdates(
  messages: PersistedChatMessage[],
): CaseStateInspectorUpdate[] {
  return messages
    .filter((message) => message.role === "assistant")
    .map((message) => {
      const update = caseUpdateForMessage(message, messages);
      const fallbackGaps = latestValidatedGaps(messages, message.ordinal);
      const resolvedUpdate: CaseUpdateView = update ?? {
        status: "no_change",
        parentVersion: 1,
        childVersion: null,
        added: [],
        changed: [],
        currentUnresolvedInformation: fallbackGaps,
      };
      return {
        ordinal: message.ordinal,
        update: resolvedUpdate,
        mitreCandidates: mitreCandidatesForMessage(message),
      };
    });
}
