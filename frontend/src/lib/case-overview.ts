import type { PersistedChatMessage, ThreadStatus } from "@/lib/api";
import {
  getCaseEvidencePresentation,
  type EvidenceSourceType,
} from "@/lib/case-evidence";

export interface SourceMessageRef {
  id: string;
  ordinal: number;
  label: string;
  excerpt: string;
  sourceType: EvidenceSourceType;
  sourceTypeLabel: string;
  fullContent: string;
}

export interface MitreTechniqueRef {
  techniqueId: string;
  techniqueName: string;
  reason: string;
  description: string;
}

export interface AttackStoryStep {
  stepNumber: number;
  text: string;
  claimType: "reported" | "analytical_inference" | "unknown";
  epistemicStatus:
    | "reported"
    | "suspected"
    | "contradicted"
    | "not_established"
    | "unknown"
    | "not_confirmed";
  sourceMessages: SourceMessageRef[];
  mitreTechniques: MitreTechniqueRef[];
}

export interface EstablishedFact {
  id: string;
  text: string;
  sourceMessages: SourceMessageRef[];
}

export interface UnclearItem {
  id: string;
  topic: string;
  description: string;
  status: string;
  reason?: string;
  affects?: string;
  priority?: "high" | "medium" | "low";
}

export interface InvestigationPoint {
  id: string;
  suggestion: string;
  rationale: string;
  focusArea?: string;
  priority?: "high" | "medium" | "low";
}

export interface MitreExplainedCard {
  techniqueId: string;
  techniqueName: string;
  description: string;
  caseAssociationReason: string;
  isExternalContext: true;
  linkedClaimTexts: string[];
}

export interface CaseOverviewData {
  hasAnalysis: boolean;
  isProcessing: boolean;
  incidentSummary: string;
  attackStory: AttackStoryStep[];
  establishedFacts: EstablishedFact[];
  unclearItems: UnclearItem[];
  investigationPoints: InvestigationPoint[];
  mitreContext: MitreExplainedCard[];
  analysisMessageId: string | null;
  totalMessagesCount: number;
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

interface RawTraceClaim {
  claim_id: string;
  claim_type: "reported" | "analytical_inference" | "unknown";
  text: string;
  epistemic_status:
    | "reported"
    | "suspected"
    | "contradicted"
    | "not_established"
    | "unknown"
    | "not_confirmed";
  source_message_ids: string[];
}

interface RawTraceAssociation {
  association_id: string;
  technique_id: string;
  claim_ids: string[];
  reason: string;
  status: string;
  support_role: string;
}

interface RawGapItem {
  topic: string;
  status: string;
  description: string;
  affects: string;
  reason: string;
  priority: "high" | "medium" | "low";
  askable: boolean;
}

function parseAnalysisSections(markdown: string): Map<number, string> {
  const sections = new Map<number, string>();
  if (!markdown) return sections;

  // Split by markdown headings like "### 1. Overall Case Picture" or "### 1. ..."
  const headingRegex = /^###\s*(\d+)\.\s*([^\n]+)/gm;
  const matches: Array<{ index: number; sectionNum: number; fullMatchLength: number }> = [];

  let match: RegExpExecArray | null;
  while ((match = headingRegex.exec(markdown)) !== null) {
    const sectionNum = parseInt(match[1], 10);
    matches.push({
      index: match.index,
      sectionNum,
      fullMatchLength: match[0].length,
    });
  }

  for (let i = 0; i < matches.length; i++) {
    const current = matches[i];
    const next = matches[i + 1];
    const start = current.index + current.fullMatchLength;
    const end = next ? next.index : markdown.length;
    const sectionBody = markdown.slice(start, end).trim();
    sections.set(current.sectionNum, sectionBody);
  }

  return sections;
}

function cleanMarkdownSnippet(text: string): string {
  return text
    .replace(/^[-*•]\s+/gm, "")
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/\n\s*\n/g, "\n")
    .trim();
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
      label: presentation.overviewSourceLabel,
      excerpt:
        msg.content.length > 120 ? `${msg.content.slice(0, 120)}…` : msg.content,
      sourceType: presentation.sourceType,
      sourceTypeLabel: presentation.sourceTypeLabel,
      fullContent: msg.content,
    });
  }
  return refs;
}

export function buildCaseOverview(
  messages: PersistedChatMessage[],
  threadStatus?: ThreadStatus | null,
): CaseOverviewData {
  const isProcessing =
    threadStatus === "processing" || threadStatus === "awaiting_followup";

  // Find latest grounded analysis assistant message
  const assistantMessages = messages.filter((m) => m.role === "assistant");
  const analysisMessage = [...assistantMessages].reverse().find((m) => {
    const kind = m.metadata_json.analysis_kind;
    const trace = asRecord(m.metadata_json.analysis_trace);
    return kind === "grounded_main_analysis" || trace?.version === "analysis_trace_v2";
  });

  if (!analysisMessage) {
    return {
      hasAnalysis: false,
      isProcessing,
      incidentSummary: "",
      attackStory: [],
      establishedFacts: [],
      unclearItems: [],
      investigationPoints: [],
      mitreContext: [],
      analysisMessageId: null,
      totalMessagesCount: messages.length,
    };
  }

  const rawTrace = asRecord(analysisMessage.metadata_json.analysis_trace);
  const rawClaimsList = asArray(rawTrace?.claims);
  const rawAssocList = asArray(rawTrace?.mitre_associations);
  const rawMitreTable = asArray(analysisMessage.metadata_json.mitre_table);
  const rawFollowup = asRecord(analysisMessage.metadata_json.chat_followup);
  const rawGapAnalysis = asRecord(rawFollowup?.gap_analysis);
  const rawGaps = asArray(rawGapAnalysis?.gaps);

  // Parse MITRE Table rows
  const mitreTableMap = new Map<
    string,
    { name: string; description: string; tactic: string }
  >();
  if (rawMitreTable) {
    for (const rawRow of rawMitreTable) {
      const row = asRecord(rawRow);
      if (row) {
        const id = asString(row.technique_id);
        const name = asString(row.name);
        const desc = asString(row.description);
        const tactic = asString(row.tactic);
        if (id) {
          mitreTableMap.set(id, { name, description: desc, tactic });
        }
      }
    }
  }

  // Parse claims
  const parsedClaims: RawTraceClaim[] = [];
  if (rawClaimsList) {
    for (const rawClaim of rawClaimsList) {
      const c = asRecord(rawClaim);
      if (c) {
        const claimId = asString(c.claim_id);
        const claimType = asString(c.claim_type) as RawTraceClaim["claim_type"];
        const text = asString(c.text);
        const epistemic = asString(c.epistemic_status) as RawTraceClaim["epistemic_status"];
        const sourceIds = (asArray(c.source_message_ids) ?? []).map(asString).filter(Boolean);
        if (claimId && text) {
          parsedClaims.push({
            claim_id: claimId,
            claim_type: claimType || "unknown",
            text,
            epistemic_status: epistemic || "unknown",
            source_message_ids: sourceIds,
          });
        }
      }
    }
  }

  // Parse associations
  const parsedAssociations: RawTraceAssociation[] = [];
  if (rawAssocList) {
    for (const rawAssoc of rawAssocList) {
      const a = asRecord(rawAssoc);
      if (a) {
        const assocId = asString(a.association_id);
        const techniqueId = asString(a.technique_id);
        const reason = asString(a.reason);
        const claimIds = (asArray(a.claim_ids) ?? []).map(asString).filter(Boolean);
        if (assocId && techniqueId) {
          parsedAssociations.push({
            association_id: assocId,
            technique_id: techniqueId,
            claim_ids: claimIds,
            reason,
            status: asString(a.status),
            support_role: asString(a.support_role),
          });
        }
      }
    }
  }

  // 1. WHAT HAPPENED? (Incident Summary)
  const sections = parseAnalysisSections(analysisMessage.content);
  let incidentSummary = sections.get(1) || "";
  if (!incidentSummary) {
    // Fallback: take content before section 2 or first 2 paragraphs
    const firstSectionMatch = analysisMessage.content.split(/###\s*\d+\./)[0]?.trim();
    if (firstSectionMatch && firstSectionMatch.length > 30) {
      incidentSummary = firstSectionMatch;
    } else {
      // Fallback: use top reported claims
      const reportedClaims = parsedClaims
        .filter((c) => c.epistemic_status === "reported" || c.claim_type === "reported")
        .slice(0, 3)
        .map((c) => c.text);
      incidentSummary = reportedClaims.join(" ");
    }
  }

  // 2. ATTACK STORY
  const attackStory: AttackStoryStep[] = parsedClaims.map((claim, index) => {
    // Find linked MITRE techniques
    const linkedAssocs = parsedAssociations.filter((a) =>
      a.claim_ids.includes(claim.claim_id),
    );
    const mitreTechniques: MitreTechniqueRef[] = linkedAssocs.map((assoc) => {
      const tableEntry = mitreTableMap.get(assoc.technique_id);
      return {
        techniqueId: assoc.technique_id,
        techniqueName: tableEntry?.name || assoc.technique_id,
        reason: assoc.reason,
        description: tableEntry?.description || "",
      };
    });

    const sourceRefs = mapSourceMessageIds(claim.source_message_ids, messages);

    return {
      stepNumber: index + 1,
      text: claim.text,
      claimType: claim.claim_type,
      epistemicStatus: claim.epistemic_status,
      sourceMessages: sourceRefs,
      mitreTechniques,
    };
  });

  // 3. WHAT IS ESTABLISHED?
  const establishedFacts: EstablishedFact[] = parsedClaims
    .filter(
      (c) =>
        (c.epistemic_status === "reported" || c.claim_type === "reported") &&
        c.source_message_ids.length > 0,
    )
    .map((c) => ({
      id: c.claim_id,
      text: c.text,
      sourceMessages: mapSourceMessageIds(c.source_message_ids, messages),
    }));

  // 4. WHAT REMAINS UNCLEAR?
  const unclearItems: UnclearItem[] = [];

  // Parse structured gaps if available
  if (rawGaps) {
    for (let i = 0; i < rawGaps.length; i++) {
      const g = asRecord(rawGaps[i]);
      if (g) {
        const topic = asString(g.topic);
        const desc = asString(g.description);
        const status = asString(g.status);
        const reason = asString(g.reason);
        const affects = asString(g.affects);
        const priority = asString(g.priority) as RawGapItem["priority"];
        if (topic || desc) {
          unclearItems.push({
            id: `gap-${i + 1}`,
            topic: topic || "Unresolved item",
            description: desc || reason,
            status: status || "NOT_PROVIDED",
            reason,
            affects,
            priority: priority || "medium",
          });
        }
      }
    }
  }

  // Include claims that are suspected, contradicted, or not confirmed
  const unconfirmedClaims = parsedClaims.filter(
    (c) =>
      c.epistemic_status === "suspected" ||
      c.epistemic_status === "not_established" ||
      c.epistemic_status === "contradicted" ||
      c.epistemic_status === "not_confirmed" ||
      c.epistemic_status === "unknown",
  );

  for (const claim of unconfirmedClaims) {
    // Avoid exact duplicate
    if (!unclearItems.some((u) => u.description.includes(claim.text))) {
      unclearItems.push({
        id: `unclear-claim-${claim.claim_id}`,
        topic: claim.claim_id,
        description: claim.text,
        status: claim.epistemic_status.toUpperCase(),
        priority: claim.epistemic_status === "contradicted" ? "high" : "medium",
      });
    }
  }

  // Fallback to Section 4 if unclearItems is still empty
  if (unclearItems.length === 0 && sections.has(4)) {
    const section4Text = cleanMarkdownSnippet(sections.get(4)!);
    if (section4Text && !section4Text.toLowerCase().includes("none") && !section4Text.toLowerCase().includes("ไม่มี")) {
      const lines = section4Text.split("\n").filter(Boolean);
      lines.forEach((line, index) => {
        unclearItems.push({
          id: `unclear-sec4-${index + 1}`,
          topic: "Unresolved matter",
          description: line,
          status: "NOT_ESTABLISHED",
          priority: "medium",
        });
      });
    }
  }

  // 5. POINTS FOR FURTHER INVESTIGATION
  const investigationPoints: InvestigationPoint[] = [];

  for (const gap of unclearItems) {
    let suggestion = "";
    let rationale = "";

    if (gap.affects) {
      rationale = `Affects: ${gap.affects}`;
    } else if (gap.reason) {
      rationale = gap.reason;
    } else {
      rationale = "Information is currently unconfirmed in the case narrative.";
    }

    if (gap.description) {
      suggestion = formatInvestigationSuggestion(gap.topic, gap.description);
    } else {
      suggestion = `Investigate and gather further records regarding ${gap.topic.toLowerCase()}.`;
    }

    investigationPoints.push({
      id: `investigation-${gap.id}`,
      suggestion,
      rationale,
      focusArea: gap.topic !== gap.id ? gap.topic : undefined,
      priority: gap.priority,
    });
  }

  // 6. MITRE EXPLAINED SIMPLY
  const mitreContext: MitreExplainedCard[] = [];
  const seenTechniques = new Set<string>();

  for (const assoc of parsedAssociations) {
    if (seenTechniques.has(assoc.technique_id)) continue;
    seenTechniques.add(assoc.technique_id);

    const tableInfo = mitreTableMap.get(assoc.technique_id);
    const techniqueName = tableInfo?.name || assoc.technique_id;
    const description =
      tableInfo?.description ||
      "External cybersecurity threat pattern defined by MITRE ATT&CK intelligence.";

    // Claims linked to this technique
    const linkedClaims = parsedClaims
      .filter((c) => assoc.claim_ids.includes(c.claim_id))
      .map((c) => c.text);

    mitreContext.push({
      techniqueId: assoc.technique_id,
      techniqueName,
      description,
      caseAssociationReason: assoc.reason,
      isExternalContext: true,
      linkedClaimTexts: linkedClaims,
    });
  }

  return {
    hasAnalysis: true,
    isProcessing,
    incidentSummary,
    attackStory,
    establishedFacts,
    unclearItems,
    investigationPoints,
    mitreContext,
    analysisMessageId: analysisMessage.id,
    totalMessagesCount: messages.length,
  };
}

function formatInvestigationSuggestion(topic: string, description: string): string {
  const clean = description.replace(/^[-*•]\s+/, "").trim();
  const lower = clean.toLowerCase();

  if (
    lower.startsWith("consider") ||
    lower.startsWith("review") ||
    lower.startsWith("examine") ||
    lower.startsWith("verify") ||
    lower.startsWith("request") ||
    lower.startsWith("obtain")
  ) {
    return clean;
  }

  return `Consider verifying records or obtaining additional logs regarding ${clean.replace(/^[A-Z]/, (m) => m.toLowerCase())}`;
}
