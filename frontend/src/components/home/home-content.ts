export type HomePillarVisual = "bars" | "grid" | "line";

export interface HomePillar {
  number: string;
  title: string;
  description: string;
  label: string;
  type: HomePillarVisual;
}

export const homePillars: HomePillar[] = [
  {
    number: "01",
    title: "Ask",
    description:
      "Bring an incident, question, or piece of evidence into one persistent conversation.",
    label: "Start anywhere",
    type: "bars",
  },
  {
    number: "02",
    title: "Clarify",
    description:
      "Work through missing context with focused, guided follow-up questions.",
    label: "Guided context",
    type: "grid",
  },
  {
    number: "03",
    title: "Continue",
    description:
      "Keep saved chat threads available so every investigation can pick up where it left off.",
    label: "Saved threads",
    type: "line",
  },
];

export const homeWorkflowSteps = [
  ["01", "Start", "Open a chat and describe what you need to understand."],
  ["02", "Clarify", "Answer focused follow-ups when more context is needed."],
  ["03", "Continue", "Keep each accepted message and response in the thread."],
  ["04", "Return", "Come back to any saved chat without losing the thread."],
] as const;

export const homeIntelligencePillars = [
  ["Persistent context", "Keep the accepted conversation available across sessions."],
  ["Guided follow-up", "Ask for the missing detail before continuing the analysis."],
  ["Saved threads", "Switch between multiple conversations from one workspace."],
  ["Clear handoff", "Keep questions, answers, and analysis together."],
] as const;
