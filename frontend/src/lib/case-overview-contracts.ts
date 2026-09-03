import type { EvidenceSourceType } from "@/lib/case-evidence";

export type ClaimType = "reported" | "analytical_inference" | "unknown";
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
}

export interface EvidencePage {
  pageNumber: number;
  text: string;
  exactQuote: string | null;
}

export interface AnalysisEvidenceCitation {
  sourceMessageId: string;
  exactQuote: string;
  documentId: string | null;
  filename: string | null;
  pageNumbers: number[];
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
  analysisMessageId: string | null;
  contractVersion: "v3" | "legacy" | null;
}
