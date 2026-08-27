import type { PersistedChatMessage } from "@/lib/api";
import { type SourceMessageRef } from "@/lib/case-overview";
import { getCaseEvidencePresentation } from "@/lib/case-evidence";

export interface TechnicalContextCard {
  techniqueId: string;
  techniqueName: string;
  tactic: string;
  shortPlainMeaning: string;
  fullTechnicalDefinition: string;
  whyRelevantHere: string;
  caseBasisSources: SourceMessageRef[];
  isExternalReference: true;
}

export interface TechnicalContextData {
  hasContext: boolean;
  techniques: TechnicalContextCard[];
  totalCount: number;
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

function asArray(value: unknown): unknown[] | null {
  return Array.isArray(value) ? value : null;
}

function asString(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

function extractShortPlainMeaning(description: string): string {
  const clean = description.trim();
  if (!clean) return "คำอธิบายพฤติกรรมตามกรอบมาตรฐาน MITRE ATT&CK";
  const firstSentence = clean.split(/(?<=[.!?])\s+|\n+/)[0] ?? clean;
  if (firstSentence.length > 200) {
    return `${firstSentence.slice(0, 197)}...`;
  }
  return firstSentence;
}

function resolveCaseRelevance(reason: string): string {
  const trimmed = reason.trim();
  if (
    !trimmed ||
    trimmed.includes("เทคนิคนี้ถูกนำมาใช้เป็นกรอบอ้างอิงเชิงวิเคราะห์") ||
    trimmed.includes("analytical reference")
  ) {
    return "พบพฤติกรรมในข้อมูลคดีที่สอดคล้องกับเทคนิคนี้";
  }
  return trimmed;
}

function mapSourceMessageIds(
  sourceIds: string[],
  allMessages: PersistedChatMessage[],
): SourceMessageRef[] {
  const refs: SourceMessageRef[] = [];
  const messageMap = new Map<string, PersistedChatMessage>();
  for (const msg of allMessages) {
    messageMap.set(msg.id, msg);
  }

  for (const id of sourceIds) {
    const msg = messageMap.get(id);
    if (!msg) continue;

    const presentation = getCaseEvidencePresentation(msg);
    if (!presentation) continue;

    refs.push({
      id: msg.id,
      ordinal: msg.ordinal,
      label: presentation.label,
      excerpt:
        msg.content.length > 120 ? `${msg.content.slice(0, 120)}…` : msg.content,
      sourceType: presentation.sourceType,
      sourceTypeLabel: presentation.sourceTypeLabel,
      fullContent: msg.content,
    });
  }

  return refs;
}

export function buildTechnicalContext(messages: PersistedChatMessage[]): TechnicalContextData {
  const assistantMessages = messages.filter((m) => m.role === "assistant");
  const analysisMessage = [...assistantMessages].reverse().find((m) => {
    const kind = m.metadata_json.analysis_kind;
    const trace = asRecord(m.metadata_json.analysis_trace);
    return kind === "grounded_main_analysis" || trace?.version === "analysis_trace_v2";
  });

  if (!analysisMessage) {
    return {
      hasContext: false,
      techniques: [],
      totalCount: 0,
    };
  }

  const rawTrace = asRecord(analysisMessage.metadata_json.analysis_trace);
  const rawClaimsList = asArray(rawTrace?.claims) ?? [];
  const rawAssocList = asArray(rawTrace?.mitre_associations) ?? [];
  const rawMitreTable = asArray(analysisMessage.metadata_json.mitre_table) ?? [];

  // Build claims lookup for source message IDs
  const claimSourceMap = new Map<string, string[]>();
  for (const rawClaim of rawClaimsList) {
    const c = asRecord(rawClaim);
    if (c) {
      const claimId = asString(c.claim_id);
      const sources = (asArray(c.source_message_ids) ?? []).map(asString).filter(Boolean);
      if (claimId) {
        claimSourceMap.set(claimId, sources);
      }
    }
  }


  interface MitreTableRow {
    id: string;
    name: string;
    tactic: string;
    description: string;
    reason: string;
  }
  const mitreRows: MitreTableRow[] = [];
  const seenIds = new Set<string>();

  for (const rawRow of rawMitreTable) {
    const row = asRecord(rawRow);
    if (row) {
      const id = asString(row.technique_id);
      const name = asString(row.name);
      const tactic = asString(row.tactic);
      const description = asString(row.description);
      const reason = asString(row.reason);
      const isTechnique =
        id &&
        !id.toUpperCase().startsWith("TA") &&
        (id.toUpperCase().startsWith("T") || !id.includes("TA"));
      if (isTechnique && !seenIds.has(id)) {
        seenIds.add(id);
        mitreRows.push({ id, name, tactic, description, reason });
      }
    }
  }

  // Build association map
  const assocMap = new Map<string, { reason: string; sourceIds: string[] }>();
  for (const rawAssoc of rawAssocList) {
    const a = asRecord(rawAssoc);
    if (a) {
      const techId = asString(a.technique_id);
      const reason = asString(a.reason);
      const claimIds = (asArray(a.claim_ids) ?? []).map(asString).filter(Boolean);
      const sourceIds: string[] = [];
      for (const cid of claimIds) {
        const s = claimSourceMap.get(cid);
        if (s) sourceIds.push(...s);
      }
      if (techId && !techId.toUpperCase().startsWith("TA")) {
        assocMap.set(techId, {
          reason: reason || assocMap.get(techId)?.reason || "",
          sourceIds: Array.from(new Set([...(assocMap.get(techId)?.sourceIds ?? []), ...sourceIds])),
        });
      }
    }
  }

  // Ensure any associated techniques not in rawMitreTable are also present
  for (const [techId, assoc] of assocMap.entries()) {
    if (!seenIds.has(techId) && !techId.toUpperCase().startsWith("TA")) {
      seenIds.add(techId);
      mitreRows.push({
        id: techId,
        name: techId,
        tactic: "",
        description: "",
        reason: assoc.reason,
      });
    }
  }

  const techniques: TechnicalContextCard[] = [];

  for (const row of mitreRows) {
    const assoc = assocMap.get(row.id);
    const whyRelevantHere = resolveCaseRelevance(assoc?.reason || row.reason || "");
    const sourceIds = assoc?.sourceIds ?? [];
    const caseBasisSources = mapSourceMessageIds(sourceIds, messages);
    const tactic = row.tactic && row.tactic !== "Adversary Tactic" ? row.tactic : "";

    techniques.push({
      techniqueId: row.id,
      techniqueName: row.name || row.id,
      tactic,
      shortPlainMeaning: extractShortPlainMeaning(row.description || ""),
      fullTechnicalDefinition: row.description || "",
      whyRelevantHere,
      caseBasisSources,
      isExternalReference: true,
    });
  }

  // Sort: associated techniques with sources first
  techniques.sort((a, b) => {
    const aHasSources = a.caseBasisSources.length > 0 ? 1 : 0;
    const bHasSources = b.caseBasisSources.length > 0 ? 1 : 0;
    if (aHasSources !== bHasSources) return bHasSources - aHasSources;
    const aInAssoc = assocMap.has(a.techniqueId) ? 1 : 0;
    const bInAssoc = assocMap.has(b.techniqueId) ? 1 : 0;
    return bInAssoc - aInAssoc;
  });

  return {
    hasContext: techniques.length > 0,
    techniques,
    totalCount: techniques.length,
  };
}
