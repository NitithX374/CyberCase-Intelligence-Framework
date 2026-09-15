import type { CaseRead } from "@/lib/api";
import { casePath } from "@/features/chat/routing/workspaceRoutes";

export type CaseLibrarySort = "recent" | "oldest" | "title";

const statusLabels: Record<CaseRead["status"], string> = {
  idle: "Ready to begin",
  processing: "Analysis in progress",
  awaiting_followup: "Input needed",
  answered: "Analysis available",
  failed: "Needs attention",
};

export function caseDestination(caseRecord: CaseRead): string {
  return casePath(caseRecord.id, caseRecord.latest_analysis_result_id ? "overview" : "intake");
}

export function caseStatusLabel(caseRecord: CaseRead): string {
  if (caseRecord.analysis_freshness === "stale") return "Needs re-analysis";
  return statusLabels[caseRecord.status];
}

export function caseStatusTone(caseRecord: CaseRead): "neutral" | "positive" | "attention" | "critical" {
  if (caseRecord.analysis_freshness === "stale" || caseRecord.status === "awaiting_followup") return "attention";
  if (caseRecord.status === "failed") return "critical";
  if (caseRecord.status === "answered") return "positive";
  return "neutral";
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
