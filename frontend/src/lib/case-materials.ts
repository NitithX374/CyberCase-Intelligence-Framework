import type { PersistedChatMessage } from "@/lib/api";

export type MaterialType =
  | "initial_case_description"
  | "clarification_response"
  | "additional_case_info";

export interface CaseMaterialItem {
  id: string;
  ordinal: number;
  itemNumber: string; // "01", "02", ...
  type: MaterialType;
  typeLabel: string;
  content: string;
  submittedAt: string;
  timestampDisplay: string;
  isInitial: boolean;
}

export interface CaseMaterialsData {
  items: CaseMaterialItem[];
  totalCount: number;
  hasMaterials: boolean;
}

function formatTimestamp(isoString: string, ordinal: number): string {
  try {
    const date = new Date(isoString);
    if (!isNaN(date.getTime())) {
      const day = String(date.getDate()).padStart(2, "0");
      const month = String(date.getMonth() + 1).padStart(2, "0");
      const year = date.getFullYear();
      const hours = String(date.getHours()).padStart(2, "0");
      const minutes = String(date.getMinutes()).padStart(2, "0");
      return `${day}/${month}/${year} ${hours}:${minutes}`;
    }
  } catch {
    // ignore
  }
  return `Evidence #${ordinal}`;
}

export function buildCaseMaterials(messages: PersistedChatMessage[]): CaseMaterialsData {
  const userMessages = messages
    .filter((m) => m.role === "user")
    .sort((a, b) => a.ordinal - b.ordinal);

  const items: CaseMaterialItem[] = [];
  let materialIndex = 0;

  for (let i = 0; i < userMessages.length; i++) {
    const msg = userMessages[i];
    const content = msg.content.trim();
    if (!content) continue;

    const action = msg.metadata_json?.action;
    const evidenceKind = msg.metadata_json?.evidence_kind;

    // Ordinary asks are NOT case material
    if (
      action === "ask" &&
      evidenceKind !== "clarification_answer" &&
      evidenceKind !== "added_case_information"
    ) {
      continue;
    }

    materialIndex++;
    const isInitial = i === 0 || evidenceKind === "initial_case_narrative";
    const isClarification =
      action === "answer_followup" || evidenceKind === "clarification_answer";

    let type: MaterialType;
    let typeLabel: string;

    if (isInitial) {
      type = "initial_case_description";
      typeLabel = "Initial case description · รายละเอียดคดีเริ่มต้น";
    } else if (isClarification) {
      type = "clarification_response";
      typeLabel = "Clarification response · คำตอบชี้แจงเพิ่มเติม";
    } else {
      type = "additional_case_info";
      typeLabel = "Additional case information · ข้อมูลคดีเพิ่มเติม";
    }

    const timestampDisplay = formatTimestamp(msg.created_at, msg.ordinal);

    items.push({
      id: msg.id,
      ordinal: msg.ordinal,
      itemNumber: String(materialIndex).padStart(2, "0"),
      type,
      typeLabel,
      content,
      submittedAt: msg.created_at,
      timestampDisplay,
      isInitial,
    });
  }

  return {
    items,
    totalCount: items.length,
    hasMaterials: items.length > 0,
  };
}
