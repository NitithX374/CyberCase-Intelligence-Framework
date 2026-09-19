export type WorkspaceView = "overview" | "sources" | "technical-context" | "report";

export const workspaceViewLabels: Record<WorkspaceView, string> = {
  overview: "Overview",
  sources: "Sources",
  "technical-context": "Technical Context",
  report: "Report",
};

export const workspaceViewDescriptions: Record<WorkspaceView, string> = {
  overview: "Case summary, findings, and open questions grounded in the sources",
  sources: "What the case knows: narratives, documents and clarification answers",
  "technical-context": "External MITRE ATT&CK reference context",
  report: "Provisional case analysis report",
};
