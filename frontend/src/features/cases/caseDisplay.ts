import type { CaseRead } from "@/lib/api/types";
import { casePath } from "@/lib/casePaths";

export type CaseLibrarySort = "recent" | "oldest" | "title";
export type CaseLibraryViewMode = "grid" | "list";

const freshnessLabels: Record<CaseRead["analysis_freshness"], string> = {
  missing: "Not analyzed",
  current: "Analyzed",
  stale: "Out of date",
};

export function caseDestination(caseRecord: CaseRead): string {
  return casePath(caseRecord.id, caseRecord.latest_analysis_result_id ? "analysis" : "sources");
}

export function caseStatusLabel(caseRecord: CaseRead): string {
  return freshnessLabels[caseRecord.analysis_freshness];
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
