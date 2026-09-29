export type WorkspaceView = "sources" | "analysis" | "legal";

export type AnalysisSection = "findings" | "details" | "questions" | "report";

export function casePath(caseId: string, view: WorkspaceView): string {
  return `/case/${encodeURIComponent(caseId)}/${view}`;
}

export function analysisPath(caseId: string, section?: AnalysisSection): string {
  const base = casePath(caseId, "analysis");
  return section ? `${base}/${section}` : base;
}
