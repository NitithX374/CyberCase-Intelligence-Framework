import { act, cleanup, renderHook } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import * as api from "@/lib/api";
import type { ChatThreadDetail } from "@/lib/api";
import { restoreInterruptedSubmission } from "@/features/chat/workspace/chat-retry-request";
import { useChatDraft } from "@/features/chat/workspace/use-chat-draft";
import { renderSession, tick } from "./chat-session-test-support";

afterEach(() => { cleanup(); vi.useRealTimers(); vi.restoreAllMocks(); });

const interrupted: ChatThreadDetail = {
  id: "thread", title: "Interrupted case", status: "failed",
  created_at: "2026-09-05T00:00:00Z", updated_at: "2026-09-05T00:00:00Z",
  messages: [{
    id: "message", thread_id: "thread", ordinal: 1, role: "user",
    content: "Original narrative", retrieval_context_id: null,
    metadata_json: { evidence_kind: "initial_case_narrative" },
    created_at: "2026-09-05T00:00:00Z",
  }],
  retry_request: {
    content: "Original narrative", idempotency_key: "original-key",
    action: null, request_ordinal: 1, clarification_answer: false,
    document_sources: [],
  },
};

describe("Interrupted chat recovery", () => {
  it("submits a restored clarification using its saved key without an in-memory question", async () => {
    vi.useFakeTimers();
    vi.spyOn(api, "getChatThread").mockResolvedValue({
      ...interrupted,
      retry_request: { ...interrupted.retry_request!, action: "add_case_info", clarification_answer: true },
    });
    const send = vi.spyOn(api, "createChatMessage").mockRejectedValue(new Error("Network failure"));
    const { result } = renderSession();
    await act(async () => { await result.current.session.selectThread("thread"); });
    await tick();
    act(() => result.current.submitContent("Original narrative", "followup", undefined, undefined, []));
    await tick();
    expect(send).toHaveBeenCalledWith("thread", "Original narrative", "original-key", expect.any(AbortSignal), "add_case_info", []);
  });

  it("restores the original request identity into a fresh draft after reload", () => {
    const { result } = renderHook(() => useChatDraft());
    act(() => result.current.reconcile(interrupted));
    expect(result.current.getPendingSubmission()).toMatchObject({
      key: "original-key", threadId: "thread", content: "Original narrative",
      requestOrdinal: 1, lastKnownMessageOrdinal: 0,
    });
    expect(result.current.state.queryError).toContain("Retry the saved message");
  });

  it("preserves clarification retry kind and the original action", () => {
    const pending = restoreInterruptedSubmission({
      ...interrupted,
      retry_request: { ...interrupted.retry_request!, action: "add_case_info", clarification_answer: true },
    });
    expect(pending).toMatchObject({ kind: "followup", action: "add_case_info", key: "original-key" });
  });

  it("does not fabricate retry identity from an ordinary failed thread", () => {
    expect(restoreInterruptedSubmission({ ...interrupted, retry_request: null })).toBeNull();
  });

  it("rejects incomplete document retry metadata", () => {
    expect(() => restoreInterruptedSubmission({
      ...interrupted,
      retry_request: {
        ...interrupted.retry_request!,
        document_sources: [{
          document_id: "doc", filename: "source.pdf", extraction_method: "native_pdf",
          page_count: 1, verification_status: "native", confidence_status: "not_applicable",
        }],
      },
    })).toThrow("incomplete");
  });
});
