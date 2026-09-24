import type { CaseRead } from "@/lib/api";
import { casePath } from "@/features/workspace/routes";

export type CaseLibrarySort = "recent" | "oldest" | "title";
export type CaseLibraryViewMode = "grid" | "list";

const statusLabels: Record<CaseRead["status"], string> = {
  idle: "Not analyzed",
  answered: "Analyzed",
};

export function caseDestination(caseRecord: CaseRead): string {
  return casePath(caseRecord.id, caseRecord.latest_analysis_result_id ? "analysis" : "sources");
}

export function caseStatusLabel(caseRecord: CaseRead): string {
  if (caseRecord.analysis_freshness === "stale") return "Out of date";
  return statusLabels[caseRecord.status];
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
