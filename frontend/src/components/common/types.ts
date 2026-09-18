export type RunPhase =
  | "idle"
  | "querying"
  | "awaiting_followup"
  | "analyzing"
  | "ready"
  | "error";

export type WorkspaceView =
  | "overview"
  | "materials"
  | "technical-context"
  | "report";

export const workspaceViewLabels: Record<WorkspaceView, string> = {
  overview: "Overview",
  materials: "Case Materials",
  "technical-context": "Technical Context",
  report: "Report",
};

export const workspaceViewDescriptions: Record<WorkspaceView, string> = {
  overview: "Evidence-bound case summary, findings, and open questions",
  materials: "User-submitted case evidence & narrative records",
  "technical-context": "External MITRE ATT&CK reference context",
  report: "Provisional case analysis report",
};

