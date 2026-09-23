import type { WorkspaceView } from "@/components/common/types";

export interface CaseRouteState {
  caseId: string | null;
  view: WorkspaceView;
}

const VALID_WORKSPACE_VIEWS: ReadonlySet<WorkspaceView> = new Set(["sources", "analysis", "legal"]);

function decodeCaseId(segment: string): string {
  try {
    return decodeURIComponent(segment);
  } catch {
    return segment;
  }
}

export function caseRouteState(pathname: string): CaseRouteState {
  const segments = pathname.split("/").filter(Boolean);
  const isCaseRoute = segments[0] === "case";
  if (!isCaseRoute) return { caseId: null, view: "analysis" };
  const caseId = segments[1] ? decodeCaseId(segments[1]) : null;
  return { caseId, view: viewForSegment(segments[2]) };
}

export function casePath(caseId: string, view: WorkspaceView): string {
  const basePath = `/case/${encodeURIComponent(caseId)}`;
  return `${basePath}/${view}`;
}

function viewForSegment(segment: string | undefined): WorkspaceView {
  if (segment && VALID_WORKSPACE_VIEWS.has(segment as WorkspaceView)) {
    return segment as WorkspaceView;
  }
  return "analysis";
}

