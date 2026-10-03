import type { SourceMessageRef } from "@/features/citations/types";

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
  places: QuotePlace[];
  passage: SourceMessageRef | null;
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

interface ClaimBacked {
  sources: SourceMessageRef[];
  inferred: boolean;
}

export interface CaseParty extends ClaimBacked {
  name: string;
  role: string;
}

export interface CaseTimelineEvent extends ClaimBacked {
  time: string;
  event: string;
}

export interface CaseImpact extends ClaimBacked {
  description: string;
}

export interface CaseOverviewData {
  hasAnalysis: boolean;
  incidentSummary: string;
  findings: CaseFinding[];
  gaps: CaseGap[];
  parties: CaseParty[];
  timeline: CaseTimelineEvent[];
  impacts: CaseImpact[];
  unavailableReason?: string;
}
