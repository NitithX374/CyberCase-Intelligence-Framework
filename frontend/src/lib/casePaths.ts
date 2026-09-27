export type WorkspaceView = "sources" | "analysis" | "legal";

export function casePath(caseId: string, view: WorkspaceView): string {
  return `/case/${encodeURIComponent(caseId)}/${view}`;
}
