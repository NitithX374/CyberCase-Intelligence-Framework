import type { WorkspaceRouteView } from "@/components/common/types";

export interface ChatRouteState {
  threadId: string | null;
  view: WorkspaceRouteView;
}

function decodeThreadId(segment: string): string {
  try {
    return decodeURIComponent(segment);
  } catch {
    return segment;
  }
}

export function chatRouteState(pathname: string): ChatRouteState {
  const segments = pathname.split("/").filter(Boolean);
  const threadId =
    segments[0] === "chat" && segments[1]
      ? decodeThreadId(segments[1])
      : null;
  const routeSegment = segments[2];
  const view: WorkspaceRouteView =
    routeSegment === "intake"
      ? "intake"
      : routeSegment === "materials"
        ? "materials"
        : routeSegment === "technical-context"
          ? "technical-context"
          : routeSegment === "report"
            ? "report"
            : "overview";

  return { threadId, view };
}

export function chatPath(threadId: string, view: WorkspaceRouteView): string {
  const basePath = `/chat/${encodeURIComponent(threadId)}`;
  return `${basePath}/${view}`;
}

