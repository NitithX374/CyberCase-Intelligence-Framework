import type { PersistedChatMessage } from "@/lib/api";
import {
  getCaseEvidencePresentation,
  type MaterialType,
} from "@/lib/case-evidence";

export type { MaterialType };

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

  for (const msg of userMessages) {
    const content = msg.content.trim();
    if (!content) continue;

    const presentation = getCaseEvidencePresentation(msg);
    if (!presentation) continue;

    materialIndex++;
    const timestampDisplay = formatTimestamp(msg.created_at, msg.ordinal);

    items.push({
      id: msg.id,
      ordinal: msg.ordinal,
      itemNumber: String(materialIndex).padStart(2, "0"),
      type: presentation.materialType,
      typeLabel: presentation.materialTypeLabel,
      content,
      submittedAt: msg.created_at,
      timestampDisplay,
      isInitial: presentation.isInitial,
    });
  }

  return {
    items,
    totalCount: items.length,
    hasMaterials: items.length > 0,
  };
}

