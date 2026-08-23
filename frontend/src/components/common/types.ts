export type RunPhase =
  | "idle"
  | "querying"
  | "awaiting_followup"
  | "analyzing"
  | "ready"
  | "error";

export type WorkspaceView =
  | "chat"
  | "report";

export type WorkspaceRouteView = WorkspaceView;

export function workspaceViewForRoute(
  view: WorkspaceRouteView,
): WorkspaceView {
  return view;
}

export const workspaceViewLabels: Record<WorkspaceView, string> = {
  chat: "Chat",
  report: "Report generation",
};

export const workspaceViewDescriptions: Record<WorkspaceView, string> = {
  chat: "Interactive incident reasoning",
  report: "Provisional case analysis report",
};
