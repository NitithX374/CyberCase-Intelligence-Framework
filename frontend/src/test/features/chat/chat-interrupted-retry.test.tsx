import { act, cleanup, renderHook } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { writeAccountValue } from "@/lib/account-storage";
import { useChatDraft, type PendingChatSubmission } from "@/features/chat/useChatDraft";
import { message, caseChat } from "./chat-session-test-support";

afterEach(() => {
  cleanup();
  window.localStorage.clear();
  vi.restoreAllMocks();
});

describe("Case Chat interrupted recovery", () => {
  it("keeps the response activity while an optimistic message waits for the assistant", () => {
    const pending: PendingChatSubmission = {
      caseId: "case",
      content: "Original narrative",
      key: "original-key",
      kind: "message",
      lastKnownMessageOrdinal: 0,
    };
    const optimisticMessage = {
      ...message("case", 1, "user", pending.content),
      id: `optimistic:${pending.key}`,
      client_request_id: pending.key,
    };
    const { result } = renderHook(() => useChatDraft());

    act(() => result.current.selectDraft("case"));
    act(() => result.current.beginSubmission(pending));
    act(() => result.current.reconcile(caseChat("case", "idle", [optimisticMessage])));

    expect(result.current.state.activity?.phase).toBe("querying");
  });

  it("restores a persisted Case Chat submission after reload", () => {
    const pending: PendingChatSubmission = {
      caseId: "case",
      content: "Original narrative",
      key: "original-key",
      kind: "message",
      lastKnownMessageOrdinal: 0,
    };
    writeAccountValue("pending-case-chat:case", JSON.stringify(pending));
    const detail = caseChat("case", "idle", [message("case", 1, "user", pending.content)]);
    const { result } = renderHook(() => useChatDraft());

    act(() => result.current.selectDraft("case"));
    act(() => result.current.reconcile(detail, "Background processing failed. Retry the saved message."));

    expect(result.current.getPendingSubmission()).toMatchObject({
      ...pending,
      requestOrdinal: 1,
    });
    expect(result.current.state.queryError).toContain("Retry the saved message");
  });
});
