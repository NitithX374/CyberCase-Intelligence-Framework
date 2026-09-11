import type { WorkspaceRouteView } from "@/components/common/types";

export interface ChatRouteState {
  caseId: string | null;
  view: WorkspaceRouteView;
}

export interface LegacyChatRouteState {
  threadId: string | null;
  view: WorkspaceRouteView;
}

export type LegacyChatAvailability = "historical_unavailable" | "unavailable";

export interface ChatCaseLinkResult {
  status: "linked" | "historical_unavailable";
  case_id: string | null;
}

export type LegacyChatDestination =
  | { kind: "case"; path: string }
  | { kind: "unavailable"; status: LegacyChatAvailability; path: string };

function decodeCaseId(segment: string): string {
  try {
    return decodeURIComponent(segment);
  } catch {
    return segment;
  }
}

export function resolveChatRouteState(pathname: string): ChatRouteState {
  const segments = pathname.split("/").filter(Boolean);
  const isCaseRoute = segments[0] === "case";
  const caseId =
    isCaseRoute && segments[1]
      ? decodeCaseId(segments[1])
      : null;
  return { caseId, view: viewForSegment(segments[2]) };
}

export function resolveLegacyChatRouteState(pathname: string): LegacyChatRouteState {
  const segments = pathname.split("/").filter(Boolean);
  const threadId = segments[0] === "chat" && segments[1]
    ? decodeCaseId(segments[1])
    : null;
  return { threadId, view: viewForSegment(segments[2]) };
}

export const chatRouteState = resolveChatRouteState;

export function composeCasePath(caseId: string, view: WorkspaceRouteView): string {
  const basePath = `/case/${encodeURIComponent(caseId)}`;
  return `${basePath}/${view}`;
}

export function legacyChatRedirectPath(pathname: string): string {
  const { threadId, view } = resolveLegacyChatRouteState(pathname);
  return threadId ? legacyChatUnavailablePath(threadId, view) : "/case";
}

export function legacyChatUnavailablePath(
  threadId: string,
  view: WorkspaceRouteView,
  status: LegacyChatAvailability = "unavailable",
): string {
  const query = new URLSearchParams({
    thread_id: threadId,
    view,
    status,
  });
  return `/chat-unavailable?${query.toString()}`;
}

export function resolveLegacyChatDestination(
  pathname: string,
  link: ChatCaseLinkResult | null,
): LegacyChatDestination {
  const route = resolveLegacyChatRouteState(pathname);
  if (!route.threadId) return { kind: "case", path: "/case" };
  if (link?.status === "linked" && link.case_id) {
    return { kind: "case", path: composeCasePath(link.case_id, route.view) };
  }
  const status = link?.status === "historical_unavailable" ? "historical_unavailable" : "unavailable";
  return {
    kind: "unavailable",
    status,
    path: legacyChatUnavailablePath(route.threadId, route.view, status),
  };
}

export const casePath = composeCasePath;
export const chatPath = composeCasePath;

function viewForSegment(segment: string | undefined): WorkspaceRouteView {
  return segment === "intake"
    ? "intake"
    : segment === "materials"
      ? "materials"
      : segment === "technical-context"
        ? "technical-context"
        : segment === "report"
          ? "report"
          : "overview";
}
