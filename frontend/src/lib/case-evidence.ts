import type { PersistedChatMessage } from "@/lib/api";

export type CaseEvidenceKind =
  | "initial_case_narrative"
  | "clarification_answer"
  | "added_case_information";

export type EvidenceSourceType =
  | "case_description"
  | "clarification_response"
  | "additional_info";

export type MaterialType =
  | "initial_case_description"
  | "clarification_response"
  | "additional_case_info";

export interface CaseEvidencePresentation {
  kind: CaseEvidenceKind;
  sourceType: EvidenceSourceType;
  materialType: MaterialType;
  label: string;
  overviewSourceLabel: string;
  sourceTypeLabel: string;
  materialTypeLabel: string;
  isInitial: boolean;
}

export function getCaseEvidenceKind(
  message: PersistedChatMessage,
): CaseEvidenceKind | null {
  if (message.role !== "user") return null;

  const rawKind = message.metadata_json?.evidence_kind;
  if (rawKind === "initial_case_narrative") return "initial_case_narrative";
  if (rawKind === "clarification_answer") return "clarification_answer";
  if (rawKind === "added_case_information") return "added_case_information";
  if (rawKind === "analyst_question") return null;

  // Narrow legacy-safe fallback: only if ordinal === 1 without explicit evidence_kind
  if (message.ordinal === 1 && !rawKind) {
    return "initial_case_narrative";
  }

  return null;
}

export function isCaseEvidenceMessage(
  message: PersistedChatMessage,
): boolean {
  return getCaseEvidenceKind(message) !== null;
}

export function getCaseEvidencePresentation(
  message: PersistedChatMessage,
): CaseEvidencePresentation | null {
  const kind = getCaseEvidenceKind(message);
  if (!kind) return null;

  if (kind === "initial_case_narrative") {
    return {
      kind,
      sourceType: "case_description",
      materialType: "initial_case_description",
      label: "Initial case description",
      overviewSourceLabel: "Case description",
      sourceTypeLabel: "Case description · รายละเอียดคดีเริ่มต้น",
      materialTypeLabel: "Initial case description · รายละเอียดคดีเริ่มต้น",
      isInitial: true,
    };
  }

  if (kind === "clarification_answer") {
    return {
      kind,
      sourceType: "clarification_response",
      materialType: "clarification_response",
      label: "Clarification response",
      overviewSourceLabel: "Clarification",
      sourceTypeLabel: "Clarification response · คำตอบชี้แจงเพิ่มเติม",
      materialTypeLabel: "Clarification response · คำตอบชี้แจงเพิ่มเติม",
      isInitial: false,
    };
  }

  return {
    kind,
    sourceType: "additional_info",
    materialType: "additional_case_info",
    label: `Evidence #${message.ordinal}`,
    overviewSourceLabel: `Evidence #${message.ordinal}`,
    sourceTypeLabel: "Additional case information · ข้อมูลคดีเพิ่มเติม",
    materialTypeLabel: "Additional case information · ข้อมูลคดีเพิ่มเติม",
    isInitial: false,
  };
}
