import { act, cleanup, renderHook } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { ChatThreadDetail } from "@/lib/api";
import { writeAccountValue } from "@/lib/account-storage";
import { useChatDraft } from "@/features/chat/workspace/use-chat-draft";
import type { PendingChatSubmission } from "@/features/chat/workspace/chat-workspace-types";
import { message, thread } from "./chat-session-test-support";

afterEach(() => {
  cleanup();
  window.localStorage.clear();
  vi.restoreAllMocks();
});

describe("Case Chat interrupted recovery", () => {
  it("restores a persisted Case Chat submission after reload", () => {
    const pending: PendingChatSubmission = {
      threadId: "thread",
      caseId: "case",
      content: "Original narrative",
      key: "original-key",
      kind: "message",
      lastKnownMessageOrdinal: 0,
    };
    writeAccountValue("pending-case-chat:thread", JSON.stringify(pending));
    const detail = thread("thread", "failed", [message("thread", 1, "user", pending.content)]);
    const { result } = renderHook(() => useChatDraft());

    act(() => result.current.selectDraft("thread"));
    act(() => result.current.reconcile(detail));

    expect(result.current.getPendingSubmission()).toMatchObject({
      ...pending,
      requestOrdinal: 1,
    });
    expect(result.current.state.queryError).toContain("Retry the saved message");
  });

  it("does not restore legacy retry metadata into Case Chat state", () => {
    const detail: ChatThreadDetail = {
      ...thread("thread", "failed", [message("thread", 1, "user", "Historical narrative")]),
      retry_request: {
        content: "Historical narrative",
        idempotency_key: "legacy-key",
        action: null,
        request_ordinal: 1,
        clarification_answer: false,
        document_sources: [],
      },
    };
    const { result } = renderHook(() => useChatDraft());

    act(() => result.current.reconcile(detail));

    expect(result.current.getPendingSubmission()).toBeNull();
    expect(result.current.state.queryError).toContain("Retry the saved message");
  });
});
