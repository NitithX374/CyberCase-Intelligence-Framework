export type ClaimType = "reported" | "analytical_inference" | "unknown";
export type EvidenceSourceType = "case_description" | "clarification_response";
export type EpistemicStatus =
  | "reported"
  | "suspected"
  | "contradicted"
  | "not_established"
  | "unknown"
  | "not_confirmed";
export type GapStatus =
  | "NOT_PROVIDED"
  | "EXPLICITLY_UNKNOWN"
  | "AMBIGUOUS"
  | "CONFLICTING";
export type GapPriority = "high" | "medium" | "low";
export type TechnicalContextStatus =
  | "hidden"
  | "available"
  | "retrieved_from_rag"
  | "unavailable"
  | "no_matches";

export interface SourceMessageRef {
  id: string;
  ordinal: number;
  label: string;
  excerpt: string;
  sourceType: EvidenceSourceType;
  sourceTypeLabel: string;
  fullContent: string;
  displayContent: string;
  exactQuote: string | null;
  documentId: string | null;
  filename: string | null;
  pageNumbers: number[];
  evidencePages: EvidencePage[];
  isNativeEvidence?: boolean;
}

export interface EvidencePage {
  pageNumber: number;
  text: string;
  exactQuote: string | null;
}

export interface MitreTechniqueRef {
  techniqueId: string;
  techniqueName: string;
  reason: string;
  description: string;
}

export interface CaseFinding {
  id: string;
  text: string;
  claimType: ClaimType;
  epistemicStatus: EpistemicStatus;
  reasoningSummary: string | null;
  supportingSources: SourceMessageRef[];
  contradictingSources: SourceMessageRef[];
  mitreTechniques: MitreTechniqueRef[];
}

export interface CaseGap {
  id: string;
  topic: string;
  status: GapStatus;
  description: string;
  affectedClaimIds: string[];
  reason: string;
  priority: GapPriority;
  askable: boolean;
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
  findings: CaseFinding[];
  gaps: CaseGap[];
  mitreContext: MitreExplainedCard[];
  technicalContextStatus: TechnicalContextStatus;
  unavailableReason?: string;
}

export interface CaseEvidenceSource {
  id: string;
  kind: string;
  ordinal: number;
  text: string;
  provenance: Record<string, unknown>;
  documentId: string | null;
  filename: string | null;
}

export interface CaseCitation {
  sourceId: string;
  exactQuote: string;
  documentId: string | null;
  filename: string | null;
  pageNumbers: number[];
}

export interface CaseTraceClaim {
  claimId: string;
  claimType: ClaimType;
  text: string;
  epistemicStatus: EpistemicStatus;
  reasoningSummary: string | null;
  supportingIds: string[];
  contradictingIds: string[];
  supportingCitations: CaseCitation[];
  contradictingCitations: CaseCitation[];
}

export interface CaseTraceAssociation {
  id: string;
  techniqueId: string;
  claimIds: string[];
  reason: string;
}

export interface ParsedCaseTrace {
  summary: string;
  claims: CaseTraceClaim[];
  gaps: CaseGap[];
  associations: CaseTraceAssociation[];
  retrievalContextId: string | null;
}
