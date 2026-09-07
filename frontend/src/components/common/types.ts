export type RunPhase =
  | "idle"
  | "querying"
  | "awaiting_followup"
  | "analyzing"
  | "ready"
  | "error";

export type WorkspaceView =
  | "intake"
  | "overview"
  | "materials"
  | "technical-context"
  | "report";

export type WorkspaceRouteView = WorkspaceView;

export function workspaceViewForRoute(
  view: WorkspaceRouteView,
): WorkspaceView {
  return view;
}

export const workspaceViewLabels: Record<WorkspaceView, string> = {
  intake: "Intake",
  overview: "Overview",
  materials: "Case Materials",
  "technical-context": "Technical Context",
  report: "Report",
};

export const workspaceViewDescriptions: Record<WorkspaceView, string> = {
  intake: "Case narrative intake & initial submission",
  overview: "Evidence-bound case summary, findings, and open questions",
  materials: "User-submitted case evidence & narrative records",
  "technical-context": "External MITRE ATT&CK reference context",
  report: "Provisional case analysis report",
};

