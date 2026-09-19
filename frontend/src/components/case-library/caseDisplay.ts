import type { CaseRead } from "@/lib/api";
import { casePath } from "@/lib/workspaceRoutes";

export type CaseLibrarySort = "recent" | "oldest" | "title";
export type CaseLibraryViewMode = "grid" | "list";
export type CaseStatusTone = "neutral" | "positive" | "attention";

const statusLabels: Record<CaseRead["status"], string> = {
  idle: "Ready to begin",
  answered: "Analysis available",
};

export const toneDotClass: Record<CaseStatusTone, string> = {
  neutral: "bg-ink-muted",
  positive: "bg-established",
  attention: "bg-unresolved",
};

/** A case with an analysis opens on it; one without opens where you add sources. */
export function caseDestination(caseRecord: CaseRead): string {
  return casePath(caseRecord.id, caseRecord.latest_analysis_result_id ? "overview" : "sources");
}

export function caseStatusLabel(caseRecord: CaseRead): string {
  if (caseRecord.analysis_freshness === "stale") return "Needs re-analysis";
  return statusLabels[caseRecord.status];
}

export function caseStatusTone(caseRecord: CaseRead): CaseStatusTone {
  if (caseRecord.analysis_freshness === "stale") return "attention";
  if (caseRecord.status === "answered") return "positive";
  return "neutral";
}

export function analysisFreshnessLabel(caseRecord: CaseRead): string {
  if (caseRecord.analysis_freshness === "current") return "Current analysis";
  if (caseRecord.analysis_freshness === "stale") return "Older analysis";
  return "Analysis unavailable";
}

export function formatCaseDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Date unavailable";
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(date);
}

export function sortCases(cases: CaseRead[], sort: CaseLibrarySort): CaseRead[] {
  return [...cases].sort((left, right) => {
    if (sort === "title") return left.title.localeCompare(right.title);
    const dateDifference = Date.parse(right.updated_at) - Date.parse(left.updated_at);
    return sort === "recent" ? dateDifference : -dateDifference;
  });
}

export function matchingCases(cases: CaseRead[], query: string, sort: CaseLibrarySort): CaseRead[] {
  const wanted = query.trim().toLocaleLowerCase();
  const matching = wanted
    ? cases.filter((caseRecord) => caseRecord.title.toLocaleLowerCase().includes(wanted))
    : cases;
  return sortCases(matching, sort);
}
