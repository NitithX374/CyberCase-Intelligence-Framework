import type { ThreadStatus } from "@/lib/api";
import { StatusPill, type StatusPillTone } from "./StatusPill";

const statusPresentation: Record<
  ThreadStatus,
  { label: string; tone: StatusPillTone }
> = {
  idle: { label: "Ready for analysis", tone: "neutral" },
  processing: { label: "Analysis in progress", tone: "evidence" },
  awaiting_followup: { label: "Your input is needed", tone: "attention" },
  answered: { label: "Analysis available", tone: "positive" },
  failed: { label: "Analysis needs attention", tone: "critical" },
};

export function ThreadStatusPill({ status }: { status: ThreadStatus }) {
  const presentation = statusPresentation[status];
  return <StatusPill tone={presentation.tone}>{presentation.label}</StatusPill>;
}
