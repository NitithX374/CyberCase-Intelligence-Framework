export type WorkspaceView = "sources" | "analysis";

export const workspaceViewDescriptions: Record<WorkspaceView, string> = {
  sources: "What the case knows: narratives, documents and clarification answers",
  analysis: "Findings, the ATT&CK context behind them, and the report",
};
