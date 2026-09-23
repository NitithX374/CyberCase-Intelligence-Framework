import type { CaseCitation, SourceMessageRef } from "@/features/sources/types";

export type ClaimType = "reported" | "analytical_inference" | "unknown";

export type EpistemicStatus =
  "reported" | "suspected" | "contradicted" | "not_established" | "unknown" | "not_confirmed";

export type GapStatus = "NOT_PROVIDED" | "EXPLICITLY_UNKNOWN" | "AMBIGUOUS" | "CONFLICTING";

export type GapPriority = "high" | "medium" | "low";

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
  /** The question the analysis wants answered, when it thought one worth asking. */
  clarificationQuestion: string | null;
}

export interface CaseOverviewData {
  hasAnalysis: boolean;
  incidentSummary: string;
  findings: CaseFinding[];
  gaps: CaseGap[];
  unavailableReason?: string;
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
  plainMeaning: string;
}

export interface ParsedCaseTrace {
  summary: string;
  claims: CaseTraceClaim[];
  gaps: CaseGap[];
  associations: CaseTraceAssociation[];
  retrievalContextId: string | null;
}
