import { describe, expect, it } from "vitest";

import { chatPath, chatRouteState } from "@/features/chat/routing/chat-route";

describe("chat workspace routes", () => {
  it("supports only chat and report workspaces", () => {
    expect(chatRouteState("/chat/thread-1")).toEqual({
      threadId: "thread-1",
      view: "chat",
    });
    expect(chatRouteState("/chat/thread-1/report")).toEqual({
      threadId: "thread-1",
      view: "report",
    });
  });

  it("does not expose deleted extraction or relationship routes", () => {
    expect(chatRouteState("/chat/thread-1/extraction")).toEqual({
      threadId: "thread-1",
      view: "chat",
    });
    expect(chatRouteState("/chat/thread-1/relationships")).toEqual({
      threadId: "thread-1",
      view: "chat",
    });
    expect(chatPath("thread-1", "chat")).toBe("/chat/thread-1");
    expect(chatPath("thread-1", "report")).toBe("/chat/thread-1/report");
  });
});
