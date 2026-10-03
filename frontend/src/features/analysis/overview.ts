import type { CaseAnalysisResultRead, CaseSourceRead } from "@/lib/api/types";
import { claimRefs, parseCaseSources, passageRef } from "@/features/citations/sourceRefs";
import {
  checkedSources,
  isUnconfirmed,
  unconfirmedStatuses,
} from "@/features/citations/unconfirmed";
import { analysisFollowups } from "./analysisRecord";
import { supportNote } from "./supportNote";
import type { CaseFinding, CaseOverviewData, ClaimBacked, ClaimType } from "./types";

export const claimTypeLabels: Record<ClaimType, string> = {
  reported: "Reported information",
  analytical_inference: "Analytical inference",
  unknown: "Unknown information",
};

const checklistTopics: Record<string, string> = {
  who_affected: "Who was affected",
  who_responsible: "Who carried it out",
  what: "What happened",
  when: "When it happened",
  where: "Where it happened",
  why: "Why it happened",
  how: "How it was done",
  how_much: "How much",
};

export function gapTopic(topic: string, gapKey: string): string {
  if (topic !== gapKey) return topic;
  const named = checklistTopics[gapKey];
  if (named) return named;
  const words = gapKey.replace(/[_:-]+/g, " ").trim();
  return words.charAt(0).toUpperCase() + words.slice(1);
}

const groupDefinitions = [
  { id: "not_established", title: "Not established", collapsible: false },
  { id: "not_confirmed", title: "Not confirmed", collapsible: false },
  { id: "unknown", title: "Unknown", collapsible: false },
  { id: "contradicted", title: "Contradicted", collapsible: false },
  { id: "suspected", title: "Suspected", collapsible: false },
  { id: "reported", title: "Reported information", collapsible: true },
  { id: "analytical_inference", title: "Analytical inferences", collapsible: true },
  { id: "unknown_claim", title: "Unknown information", collapsible: false },
] as const;

export function groupCaseFindings(findings: CaseFinding[]) {
  return groupDefinitions
    .map((group) => ({
      ...group,
      findings: findings.filter((finding) => {
        const key =
          finding.epistemicStatus !== "reported"
            ? finding.epistemicStatus
            : finding.claimType === "unknown"
              ? "unknown_claim"
              : finding.claimType;
        return key === group.id;
      }),
    }))
    .filter((group) => group.findings.length > 0);
}

export function buildCaseOverview(
  result: CaseAnalysisResultRead | null,
  rows: CaseSourceRead[] | null,
): CaseOverviewData {
  if (!result) return emptyCaseOverview();
  if (!rows) return unavailableCaseOverview("The case sources are not available yet.");
  const trace = result.trace_json;
  if (
    trace?.version !== "case_analysis_trace_v1" ||
    trace.validation_status !== "validated" ||
    trace.analysis_mode !== "case_overview"
  ) {
    return unavailableCaseOverview("The saved Case analysis trace is unavailable or unsupported.");
  }
  const sources = parseCaseSources(rows, analysisFollowups(result));
  const associations = trace.mitre_associations ?? [];
  const findings: CaseFinding[] = trace.claims.map((claim) => {
    const cited = claimRefs(claim, sources);
    return {
      id: claim.claim_id,
      text: claim.text,
      claimType: claim.claim_type,
      epistemicStatus: claim.epistemic_status,
      reasoningSummary: claim.reasoning_summary ?? null,
      supportingSources: cited.supporting,
      contradictingSources: cited.contradicting,
      techniqueIds: associations
        .filter((association) => association.claim_ids.includes(claim.claim_id))
        .map((association) => association.technique_id),
      unverifiedQuotes: (claim.unverified_citations ?? []).map((item) => ({
        writtenQuote: item.written_quote,
        places: (item.near_passage?.differences ?? []).map(({ written, source }) => ({
          written,
          source,
        })),
        passage: item.near_passage
          ? passageRef(sources, item.source_id, item.near_passage.source_text)
          : null,
      })),
    };
  });
  const backing = claimBacking(findings);
  const affected = findingsNamed(findings);
  const incidentSummary = trace.summary || result.summary || "Case summary not provided.";
  return {
    hasAnalysis: true,
    incidentSummary,
    findings,
    gaps: (trace.gaps ?? []).map((gap) => ({
      id: gap.gap_id,
      topic: gapTopic(gap.topic, gap.gap_key),
      status: gap.status,
      description: gap.description,
      reason: gap.reason,
      askable: gap.askable,
      affectedFindings: affected(gap.affected_claim_ids),
    })),
    parties: (trace.involved_parties ?? []).map(({ name, role, claim_ids, support }) => ({
      name,
      role,
      ...backing(claim_ids),
      supportNote: supportNote(support, incidentSummary),
    })),
    timeline: (trace.timeline ?? []).map(({ time, event, claim_ids, support }) => ({
      time,
      event,
      ...backing(claim_ids),
      supportNote: supportNote(support, incidentSummary),
    })),
    impacts: (trace.impacts ?? []).map(({ description, claim_ids, support }) => ({
      description,
      ...backing(claim_ids),
      supportNote: supportNote(support, incidentSummary),
    })),
  };
}

function emptyCaseOverview(): CaseOverviewData {
  return {
    hasAnalysis: false,
    incidentSummary: "",
    findings: [],
    gaps: [],
    parties: [],
    timeline: [],
    impacts: [],
  };
}

function claimBacking(findings: CaseFinding[]) {
  const byId = new Map(findings.map((finding) => [finding.id, finding]));
  return (claimIds: string[] = []): ClaimBacked => {
    const cited = claimIds.flatMap((id) => byId.get(id) ?? []);
    const seen = new Set<string>();
    const sources = cited
      .flatMap((finding) =>
        checkedSources(finding.supportingSources, isUnconfirmed(finding.epistemicStatus)),
      )
      .filter((source) => {
        const key = JSON.stringify([source.id, source.pageNumbers]);
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      });
    return {
      sources,
      inferred:
        cited.length > 0 && cited.every((finding) => finding.claimType === "analytical_inference"),
      unconfirmed: unconfirmedStatuses(cited.map((finding) => finding.epistemicStatus)),
    };
  };
}

function findingsNamed(findings: CaseFinding[]) {
  const byId = new Map(findings.map((finding) => [finding.id, finding]));
  return (claimIds: string[] = []): Pick<CaseFinding, "id" | "text">[] =>
    claimIds.flatMap((id) => {
      const finding = byId.get(id);
      return finding ? [{ id: finding.id, text: finding.text }] : [];
    });
}

function unavailableCaseOverview(reason: string): CaseOverviewData {
  return { ...emptyCaseOverview(), unavailableReason: reason };
}
