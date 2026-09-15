import { act, cleanup, renderHook } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { writeAccountValue } from "@/lib/account-storage";
import { useChatDraft } from "@/features/chat/workspace/use-chat-draft";
import type { PendingChatSubmission } from "@/features/chat/workspace/chat-workspace-types";
import { message, caseChat } from "./chat-session-test-support";

afterEach(() => {
  cleanup();
  window.localStorage.clear();
  vi.restoreAllMocks();
});

describe("Case Chat interrupted recovery", () => {
  it("restores a persisted Case Chat submission after reload", () => {
    const pending: PendingChatSubmission = {
      caseId: "case",
      content: "Original narrative",
      key: "original-key",
      kind: "message",
      lastKnownMessageOrdinal: 0,
    };
    writeAccountValue("pending-case-chat:case", JSON.stringify(pending));
    const detail = caseChat("case", "failed", [message("case", 1, "user", pending.content)]);
    const { result } = renderHook(() => useChatDraft());

    act(() => result.current.selectDraft("case"));
    act(() => result.current.reconcile(detail));

    expect(result.current.getPendingSubmission()).toMatchObject({
      ...pending,
      requestOrdinal: 1,
    });
    expect(result.current.state.queryError).toContain("Retry the saved message");
  });

});
