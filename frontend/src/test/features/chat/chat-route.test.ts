import { describe, expect, it } from "vitest";

import {
  casePath,
  chatPath,
  chatRouteState,
  legacyChatRedirectPath,
  resolveLegacyChatDestination,
  resolveLegacyChatRouteState,
} from "@/features/chat/routing/workspaceRoutes";

describe("chat workspace routes", () => {
  it("supports intake, overview, chat, and report workspaces", () => {
    expect(chatRouteState("/chat/thread-1")).toEqual({
      caseId: null,
      view: "overview",
    });
    expect(chatRouteState("/chat/thread-1/intake")).toEqual({
      caseId: null,
      view: "intake",
    });
    expect(chatRouteState("/chat/thread-1/overview")).toEqual({
      caseId: null,
      view: "overview",
    });
    expect(chatRouteState("/chat/thread-1/chat")).toEqual({
      caseId: null,
      view: "overview",
    });
    expect(chatRouteState("/chat/thread-1/report")).toEqual({
      caseId: null,
      view: "report",
    });
  });

  it("does not expose deleted extraction or relationship routes", () => {
    expect(chatRouteState("/case/thread-1/extraction")).toEqual({
      caseId: "thread-1",
      view: "overview",
    });
    expect(chatRouteState("/case/thread-1/relationships")).toEqual({
      caseId: "thread-1",
      view: "overview",
    });
    expect(chatRouteState("/chat/thread-1/extraction")).toEqual({
      caseId: null,
      view: "overview",
    });
    expect(chatPath("thread-1", "intake")).toBe("/case/thread-1/intake");
    expect(chatPath("thread-1", "overview")).toBe("/case/thread-1/overview");
    expect(chatPath("thread-1", "report")).toBe("/case/thread-1/report");
    expect(casePath("thread-1", "overview")).toBe("/case/thread-1/overview");
  });

  it("maps every legacy leaf to an explicit Case view", () => {
    expect(legacyChatRedirectPath("/chat/thread-1/chat")).toBe("/chat-unavailable?thread_id=thread-1&view=overview&status=unavailable");
    expect(legacyChatRedirectPath("/chat/thread-1/extraction")).toBe("/chat-unavailable?thread_id=thread-1&view=overview&status=unavailable");
    expect(legacyChatRedirectPath("/chat/thread-1/materials")).toBe("/chat-unavailable?thread_id=thread-1&view=materials&status=unavailable");
    expect(legacyChatRedirectPath("/chat")).toBe("/case");
  });

  it("keeps legacy Chat identity separate until an owned relation proves the Case", () => {
    expect(resolveLegacyChatRouteState("/chat/thread-1/materials")).toEqual({ threadId: "thread-1", view: "materials" });
    expect(resolveLegacyChatDestination("/chat/thread-1/materials", { status: "linked", case_id: "case-9" })).toEqual({
      kind: "case",
      path: "/case/case-9/materials",
    });
    expect(resolveLegacyChatDestination("/chat/thread-1/materials", { status: "historical_unavailable", case_id: null })).toMatchObject({
      kind: "unavailable",
      status: "historical_unavailable",
    });
    expect(resolveLegacyChatDestination("/chat/thread-1/materials", null)).toMatchObject({
      kind: "unavailable",
      status: "unavailable",
    });
  });
});
