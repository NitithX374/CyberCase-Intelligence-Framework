export type WorkspaceView = "sources" | "analysis" | "legal";

export const workspaceViewDescriptions: Record<WorkspaceView, string> = {
  sources: "What the case knows: narratives, documents and clarification answers",
  analysis: "Findings, the ATT&CK context behind them, and the report",
  legal: "Thai provisions that may bear on the case, from an external legal service",
};
