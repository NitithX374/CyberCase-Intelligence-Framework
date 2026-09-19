/**
 * Sending a message, and stopping.
 *
 * The panel showed "Answering…" over a conversation that had already been
 * answered, and kept showing it after a reload. Whether a send is in flight
 * was a flag kept beside the request, set on the way in and cleared on one of
 * the ways out — a failure left it set, and it was written to localStorage, so
 * the case came back still believing it was sending.
 *
 * These hold the shape that makes that impossible: the state belongs to the
 * request, so every way out of the request is a way out of the state, and a
 * fresh mount starts from nothing.
 */

import { QueryClientProvider, QueryClient } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import { act } from "react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useCaseChat } from "@/hooks/useCaseChat";
import { caseQueryKeys } from "@/hooks/useCaseQueries";
import { caseChat, chatResponse, deferred, message } from "./chat-session-test-support";

const getCaseChat = vi.fn();
const createCaseChatMessage = vi.fn();

vi.mock("@/lib/api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/lib/api")>()),
  getCaseChat: (...args: unknown[]) => getCaseChat(...args),
  createCaseChatMessage: (...args: unknown[]) => createCaseChatMessage(...args),
}));

function render() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: Infinity }, mutations: { retry: false } },
  });
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
  return { ...renderHook(() => useCaseChat({ caseId: "a" }), { wrapper }), queryClient };
}

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
  getCaseChat.mockResolvedValue(caseChat("a", "idle", [message("a", 1, "user", "สวัสดี")]));
});

describe("whether a send is in flight", () => {
  it("stops when the send succeeds", async () => {
    createCaseChatMessage.mockResolvedValue(
      chatResponse(message("a", 2, "assistant", "สวัสดีครับ")),
    );
    const { result } = render();
    await waitFor(() => expect(result.current.messages).toHaveLength(1));

    act(() => result.current.submitContent("สวัสดี"));
    await waitFor(() => expect(result.current.isSending).toBe(false));

    expect(result.current.messages.map((m) => m.content)).toContain("สวัสดีครับ");
    expect(result.current.input).toBe("");
  });

  it("stops when the send fails — the bug that left it on forever", async () => {
    createCaseChatMessage.mockRejectedValue(new Error("the backend never replied"));
    const { result } = render();
    await waitFor(() => expect(result.current.messages).toHaveLength(1));

    act(() => result.current.submitContent("สวัสดี"));
    await waitFor(() => expect(result.current.queryError).not.toBeNull());

    expect(result.current.isSending).toBe(false);
  });

  it("is on while the request is open, and the reader's own message is visible", async () => {
    const pending = deferred<ReturnType<typeof chatResponse>>();
    createCaseChatMessage.mockReturnValue(pending.promise);
    const { result } = render();
    await waitFor(() => expect(result.current.messages).toHaveLength(1));

    act(() => result.current.submitContent("ถามหน่อย"));
    await waitFor(() => expect(result.current.isSending).toBe(true));
    expect(result.current.messages.map((m) => m.content)).toContain("ถามหน่อย");

    await act(async () => {
      pending.resolve(chatResponse(message("a", 2, "assistant", "ครับ")));
    });
    await waitFor(() => expect(result.current.isSending).toBe(false));
  });

  it("marks a follow-up answer as analysis work while the request is open", async () => {
    const question = {
      ...message("a", 2, "assistant", "When did this happen?"),
      gap_key: "topic:incident-time",
      message_kind: "followup_question" as const,
    };
    getCaseChat.mockResolvedValue(caseChat("a", "answered", [question]));
    const pending = deferred<ReturnType<typeof chatResponse>>();
    createCaseChatMessage.mockReturnValue(pending.promise);
    const { result } = render();
    await waitFor(() => expect(result.current.pendingQuestionId).toBe(question.id));

    act(() => result.current.submitContent("ตอนตีสอง"));
    await waitFor(() => expect(result.current.isAnsweringQuestion).toBe(true));

    await act(async () => {
      pending.resolve(chatResponse(message("a", 3, "assistant", "ขอบคุณครับ")));
    });
    await waitFor(() => expect(result.current.isAnsweringQuestion).toBe(false));
  });

  it("puts the returned analysis in the cache before refetching the workspace", async () => {
    const analysis = {
      id: "analysis-2",
      case_id: "a",
      source_revision: 2,
      schema_version: "case_analysis_trace_v1",
      status: "validated" as const,
      answer: "Updated answer",
      summary: "Updated summary",
      trace_json: null,
      retrieval_context_id: null,
      pipeline_config: {},
      external_context_json: {},
      created_at: "2026-09-20T00:00:00Z",
      freshness: "current" as const,
    };
    createCaseChatMessage.mockResolvedValue({
      messages: [message("a", 2, "assistant", "เสร็จแล้ว")],
      analysis,
    });
    const { result, queryClient } = render();
    await waitFor(() => expect(result.current.messages).toHaveLength(1));

    act(() => result.current.submitContent("อัปเดตคดี"));
    await waitFor(() => expect(result.current.isSending).toBe(false));

    expect(queryClient.getQueryData(caseQueryKeys.analysis("a"))).toEqual(analysis);
  });

  it("starts off after a failed send is remounted", async () => {
    createCaseChatMessage.mockRejectedValue(new Error("gone"));
    const first = render();
    await waitFor(() => expect(first.result.current.messages).toHaveLength(1));
    act(() => first.result.current.submitContent("สวัสดี"));
    await waitFor(() => expect(first.result.current.queryError).not.toBeNull());
    first.unmount();

    const second = render();
    expect(second.result.current.isSending).toBe(false);
    expect(second.result.current.queryError).toBeNull();
  });
});

it("retries with the key the server already saw, so one message is not written twice", async () => {
  createCaseChatMessage.mockRejectedValueOnce(new Error("timed out"));
  createCaseChatMessage.mockResolvedValueOnce(chatResponse(message("a", 2, "assistant", "ครับ")));
  const { result } = render();
  await waitFor(() => expect(result.current.messages).toHaveLength(1));

  act(() => result.current.submitContent("สวัสดี"));
  await waitFor(() => expect(result.current.queryError).not.toBeNull());
  act(() => result.current.retryQuery());
  await waitFor(() => expect(result.current.isSending).toBe(false));

  const [firstCall, retryCall] = createCaseChatMessage.mock.calls;
  expect(retryCall[2]).toBe(firstCall[2]);
});
