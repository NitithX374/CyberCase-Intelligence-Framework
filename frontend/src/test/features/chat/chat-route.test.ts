import { describe, expect, it } from "vitest";

import { chatPath, chatRouteState } from "@/features/chat/routing/chat-route";

describe("chat workspace routes", () => {
  it("supports intake, overview, chat, and report workspaces", () => {
    expect(chatRouteState("/chat/thread-1")).toEqual({
      threadId: "thread-1",
      view: "overview",
    });
    expect(chatRouteState("/chat/thread-1/intake")).toEqual({
      threadId: "thread-1",
      view: "intake",
    });
    expect(chatRouteState("/chat/thread-1/overview")).toEqual({
      threadId: "thread-1",
      view: "overview",
    });
    expect(chatRouteState("/chat/thread-1/chat")).toEqual({
      threadId: "thread-1",
      view: "overview",
    });
    expect(chatRouteState("/chat/thread-1/report")).toEqual({
      threadId: "thread-1",
      view: "report",
    });
  });

  it("does not expose deleted extraction or relationship routes", () => {
    expect(chatRouteState("/chat/thread-1/extraction")).toEqual({
      threadId: "thread-1",
      view: "overview",
    });
    expect(chatRouteState("/chat/thread-1/relationships")).toEqual({
      threadId: "thread-1",
      view: "overview",
    });
    expect(chatPath("thread-1", "intake")).toBe("/chat/thread-1/intake");
    expect(chatPath("thread-1", "overview")).toBe("/chat/thread-1/overview");
    expect(chatPath("thread-1", "report")).toBe("/chat/thread-1/report");
  });
});
