import type { SourceMessageRef } from "@/features/citations/types";
import type { UnconfirmedStatus } from "@/features/citations/unconfirmed";
import type { FindingTraceabilityData } from "./findingTraceabilityData";

export type ClaimType = "reported" | "analytical_inference" | "unknown";

export type EpistemicStatus =
  "reported" | "suspected" | "contradicted" | "not_established" | "unknown" | "not_confirmed";

export type GapStatus = "NOT_PROVIDED" | "EXPLICITLY_UNKNOWN" | "AMBIGUOUS" | "CONFLICTING";

export interface CaseFinding {
  id: string;
  text: string;
  claimType: ClaimType;
  epistemicStatus: EpistemicStatus;
  reasoningSummary: string | null;
  traceability: FindingTraceabilityData;
  supportingSources: SourceMessageRef[];
  contradictingSources: SourceMessageRef[];
  techniqueIds: string[];
  unverifiedQuotes: UnverifiedQuote[];
}

export interface QuotePlace {
  written: string;
  source: string;
}

export interface UnverifiedQuote {
  writtenQuote: string;
  evidenceUnitId?: string | null;
  places: QuotePlace[];
  passage: SourceMessageRef | null;
  meaningPassage: SourceMessageRef | null;
}

export interface CaseGap {
  id: string;
  topic: string;
  status: GapStatus;
  description: string;
  reason: string;
  askable: boolean;
  affectedFindings: Pick<CaseFinding, "id" | "text">[];
}

export interface FindingMark {
  number: number;
  claimId: string;
}

export interface SummaryUnit {
  text: string;
  claimIds: string[];
  marks: FindingMark[];
  closing: string;
  supportNote: string | null;
  noteMark: string | null;
}

export interface ClaimBacked {
  sources: SourceMessageRef[];
  inferred: boolean;
  supportNote?: string | null;
  unconfirmed: UnconfirmedStatus[];
  linkedClaims?: Pick<CaseFinding, "id" | "text">[];
}

export interface CaseParty extends ClaimBacked {
  name: string;
  role: string | null;
}

export interface CaseTimelineEvent extends ClaimBacked {
  time: string | null;
  event: string;
}

export interface CaseImpact extends ClaimBacked {
  description: string;
}

export interface CaseOverviewData {
  hasAnalysis: boolean;
  incidentSummary: string;
  summaryUnits: SummaryUnit[];
  findings: CaseFinding[];
  gaps: CaseGap[];
  parties: CaseParty[];
  timeline: CaseTimelineEvent[];
  impacts: CaseImpact[];
  unavailableReason?: string;
}
