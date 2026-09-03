export {
  formatEvidenceCitationText,
  formatPageReference,
  mapSourceMessageIds,
  parseEvidenceCitations,
} from "@/lib/evidence-citation";
import type {
  MitreExplainedCard,
  MitreTechniqueRef,
} from "@/lib/case-overview-contracts";

export function asRecord(value: unknown): Record<string, unknown> | null {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

export function asArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

export function asString(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

export function asStringArray(value: unknown): string[] {
  return asArray(value).map(asString).filter(Boolean);
}

interface ParsedAssociation {
  techniqueId: string;
  claimIds: string[];
  reason: string;
}

interface ParsedMitreTableRow {
  name: string;
  description: string;
}

export function parseAssociations(value: unknown): ParsedAssociation[] {
  return asArray(value).flatMap((item) => {
    const association = asRecord(item);
    if (!association) return [];
    const techniqueId = asString(association.technique_id);
    if (!techniqueId) return [];
    return [{
      techniqueId,
      claimIds: asStringArray(association.claim_ids),
      reason: asString(association.reason),
    }];
  });
}

export function parseMitreTable(value: unknown): Map<string, ParsedMitreTableRow> {
  const table = new Map<string, ParsedMitreTableRow>();
  for (const item of asArray(value)) {
    const row = asRecord(item);
    if (!row) continue;
    const techniqueId = asString(row.technique_id);
    if (!techniqueId) continue;
    table.set(techniqueId, {
      name: asString(row.name),
      description: asString(row.description),
    });
  }
  return table;
}

export function techniquesForClaim(
  claimId: string,
  associations: ParsedAssociation[],
  table: Map<string, ParsedMitreTableRow>,
): MitreTechniqueRef[] {
  return associations
    .filter((association) => association.claimIds.includes(claimId))
    .map((association) => {
      const row = table.get(association.techniqueId);
      return {
        techniqueId: association.techniqueId,
        techniqueName: row?.name || association.techniqueId,
        reason: association.reason,
        description: row?.description || "",
      };
    });
}

export function buildMitreCards(
  associations: ParsedAssociation[],
  table: Map<string, ParsedMitreTableRow>,
  claimTextById: Map<string, string>,
): MitreExplainedCard[] {
  const grouped = new Map<string, ParsedAssociation[]>();
  for (const association of associations) {
    const matches = grouped.get(association.techniqueId) ?? [];
    matches.push(association);
    grouped.set(association.techniqueId, matches);
  }
  return [...grouped.entries()].map(([techniqueId, matches]) => {
    const row = table.get(techniqueId);
    const linkedClaimTexts = [...new Set(matches.flatMap((match) =>
      match.claimIds.map((id) => claimTextById.get(id)).filter(Boolean),
    ))] as string[];
    return {
      techniqueId,
      techniqueName: row?.name || techniqueId,
      description: row?.description || "",
      caseAssociationReason: matches.map((match) => match.reason).filter(Boolean).join(" "),
      isExternalContext: true,
      linkedClaimTexts,
    };
  });
}
