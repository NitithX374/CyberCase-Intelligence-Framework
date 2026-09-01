import type { PersistedChatMessage } from "@/lib/api";
import { getCaseEvidencePresentation } from "@/lib/case-evidence";
import type {
  AnalysisEvidenceCitation,
  MitreExplainedCard,
  MitreTechniqueRef,
  SourceMessageRef,
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

export function mapSourceMessageIds(
  sourceIds: string[],
  messages: PersistedChatMessage[],
  citations: AnalysisEvidenceCitation[] = [],
): SourceMessageRef[] {
  const messageMap = new Map(messages.map((message) => [message.id, message]));
  return sourceIds.flatMap((id) => {
    const message = messageMap.get(id);
    if (!message) return [];
    const presentation = getCaseEvidencePresentation(message);
    if (!presentation) return [];
    const citation = citations.find((value) => value.sourceMessageId === id) ?? null;
    const pageContent = citation ? contentForCitation(message, citation) : null;
    const pageLabel = citation ? citationLabel(citation) : null;
    const hasDocumentSource = asArray(message.metadata_json.document_sources).length > 0;
    const narrativeLabel = hasDocumentSource
      ? "Reviewed case narrative"
      : presentation.kind === "initial_case_narrative"
        ? "Case narrative"
        : presentation.overviewSourceLabel;
    return [{
      id: message.id,
      ordinal: message.ordinal,
      label: pageLabel ?? narrativeLabel,
      excerpt: message.content.length > 120
        ? `${message.content.slice(0, 120)}…`
        : message.content,
      sourceType: presentation.sourceType,
      sourceTypeLabel: pageLabel
        ? `${pageLabel} · ตำแหน่งอ้างอิงในเอกสาร`
        : hasDocumentSource
          ? "Reviewed case narrative · ข้อความจากเอกสารที่ผู้ใช้ตรวจทาน"
          : presentation.sourceTypeLabel,
      fullContent: message.content,
      displayContent: pageContent ?? contextualExcerpt(message.content, citation?.exactQuote),
      exactQuote: citation?.exactQuote ?? null,
      filename: citation?.filename ?? null,
      pageNumbers: citation?.pageNumbers ?? [],
    }];
  });
}

export function parseEvidenceCitations(value: unknown): AnalysisEvidenceCitation[] {
  return asArray(value).flatMap((item) => {
    const citation = asRecord(item);
    if (!citation) return [];
    const sourceMessageId = asString(citation.source_message_id);
    const exactQuote = asString(citation.exact_quote);
    if (!sourceMessageId || !exactQuote) return [];
    return [{
      sourceMessageId,
      exactQuote,
      documentId: asString(citation.document_id) || null,
      filename: asString(citation.filename) || null,
      pageNumbers: asArray(citation.page_numbers).filter(
        (page): page is number => Number.isInteger(page) && Number(page) > 0,
      ) as number[],
    }];
  });
}

function citationLabel(citation: AnalysisEvidenceCitation): string | null {
  if (!citation.filename || citation.pageNumbers.length === 0) return null;
  const pages = citation.pageNumbers;
  const pageText = pages.length === 1
    ? `p. ${pages[0]}`
    : `pp. ${formatPageList(pages)}`;
  return `${citation.filename} · ${pageText}`;
}

function formatPageList(pages: number[]): string {
  const consecutive = pages.every(
    (page, index) => index === 0 || page === pages[index - 1] + 1,
  );
  return consecutive
    ? `${pages[0]}–${pages[pages.length - 1]}`
    : pages.join(", ");
}

function contentForCitation(
  message: PersistedChatMessage,
  citation: AnalysisEvidenceCitation,
): string | null {
  if (!citation.documentId || citation.pageNumbers.length === 0) return null;
  const documentSources = asArray(message.metadata_json.document_sources);
  const document = documentSources
    .map(asRecord)
    .find((value) => asString(value?.document_id) === citation.documentId);
  if (!document) return null;
  const selectedPages = new Set(citation.pageNumbers);
  const pageTexts = asArray(document.page_spans).flatMap((item) => {
    const span = asRecord(item);
    if (!span) return [];
    const page = span.page_number;
    const start = span.start_offset;
    const end = span.end_offset;
    if (
      !Number.isInteger(page) || !selectedPages.has(Number(page)) ||
      !Number.isInteger(start) || !Number.isInteger(end) ||
      Number(start) < 0 || Number(end) > message.content.length ||
      Number(start) >= Number(end)
    ) {
      return [];
    }
    return [message.content.slice(Number(start), Number(end))];
  });
  return pageTexts.length > 0 ? pageTexts.join("\n\n") : null;
}

function contextualExcerpt(content: string, exactQuote?: string): string {
  if (!exactQuote) {
    return content.length > 640 ? `${content.slice(0, 640)}…` : content;
  }
  const quoteStart = content.indexOf(exactQuote);
  if (quoteStart < 0) return exactQuote;
  const start = Math.max(0, quoteStart - 220);
  const end = Math.min(content.length, quoteStart + exactQuote.length + 220);
  return `${start > 0 ? "…" : ""}${content.slice(start, end)}${end < content.length ? "…" : ""}`;
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
