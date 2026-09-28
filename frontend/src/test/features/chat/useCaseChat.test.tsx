import { QueryClientProvider, QueryClient } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import { act } from "react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useCaseChat, useIsFollowupPending } from "@/features/chat/useCaseChat";
import { caseQueryKeys } from "@/lib/queryKeys";
import { caseChat, chatResponse, deferred, message } from "@/test/chat";

const getCaseChat = vi.fn();
const createCaseChatMessage = vi.fn();

vi.mock("@/features/chat/api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/features/chat/api")>()),
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
  return { ...renderHook(() => useCaseChat({ caseId: "a" }), { wrapper }), queryClient, wrapper };
}

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
  getCaseChat.mockResolvedValue(caseChat("a", [message("a", 1, "user", "สวัสดี")]));
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

  it("stops when workspace refresh is still waiting", async () => {
    createCaseChatMessage.mockResolvedValue(chatResponse(message("a", 2, "assistant", "ตอบแล้ว")));
    const { result, queryClient } = render();
    const refresh = deferred<void>();
    vi.spyOn(queryClient, "invalidateQueries").mockReturnValue(refresh.promise);
    await waitFor(() => expect(result.current.messages).toHaveLength(1));

    act(() => result.current.submitContent("ตอบหน่อย"));
    await waitFor(() => expect(result.current.isSending).toBe(false));

    refresh.resolve();
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
    const { result, wrapper } = render();
    const followup = renderHook(() => useIsFollowupPending("a"), { wrapper });
    await waitFor(() => expect(result.current.messages).toHaveLength(1));

    act(() => result.current.submitContent("ถามหน่อย"));
    await waitFor(() => expect(result.current.isSending).toBe(true));
    expect(result.current.messages.map((m) => m.content)).toContain("ถามหน่อย");
    expect(followup.result.current).toBe(false);

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
    getCaseChat.mockResolvedValue(caseChat("a", [question], question.id));
    const pending = deferred<ReturnType<typeof chatResponse>>();
    createCaseChatMessage.mockReturnValue(pending.promise);
    const { result, wrapper } = render();
    const followup = renderHook(() => useIsFollowupPending("a"), { wrapper });
    const otherCase = renderHook(() => useIsFollowupPending("b"), { wrapper });
    await waitFor(() => expect(result.current.pendingQuestionId).toBe(question.id));

    act(() => result.current.submitContent("ตอนตีสอง"));
    await waitFor(() => expect(result.current.isAnsweringQuestion).toBe(true));
    await waitFor(() => expect(followup.result.current).toBe(true));
    expect(otherCase.result.current).toBe(false);

    await act(async () => {
      pending.resolve(chatResponse(message("a", 3, "assistant", "ขอบคุณครับ")));
    });
    await waitFor(() => expect(result.current.isAnsweringQuestion).toBe(false));
    await waitFor(() => expect(followup.result.current).toBe(false));
  });

  it("puts the returned analysis in the cache before refetching the workspace", async () => {
    const analysis = {
      id: "analysis-2",
      case_id: "a",
      source_revision: 2,
      schema_version: "case_analysis_trace_v1",
      status: "validated" as const,
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

describe("the question the analysis is waiting on", () => {
  const question = {
    ...message("a", 2, "assistant", "When did this happen?"),
    gap_key: "topic:incident-time",
    message_kind: "followup_question" as const,
    qa_id: "QA-01",
  };

  it("is the one the backend names, not one guessed from the messages", async () => {
    getCaseChat.mockResolvedValue(caseChat("a", [question], null));
    const { result } = render();
    await waitFor(() => expect(result.current.messages).toHaveLength(1));

    expect(result.current.pendingQuestionId).toBeNull();
  });

  it("moves to the question the send returns, and clears once none is left", async () => {
    getCaseChat.mockResolvedValue(caseChat("a", [question], question.id));
    const answer = {
      ...message("a", 3, "user", "ตอนตีสอง"),
      message_kind: "followup_answer" as const,
      in_reply_to_message_id: question.id,
      qa_id: "QA-01",
    };
    const next = {
      ...message("a", 4, "assistant", "Which account was used?"),
      gap_key: "topic:account",
      message_kind: "followup_question" as const,
      qa_id: "QA-02",
    };
    createCaseChatMessage.mockResolvedValueOnce({
      ...chatResponse(answer, next),
      pending_question_id: next.id,
    });
    const { result } = render();
    await waitFor(() => expect(result.current.pendingQuestionId).toBe(question.id));

    act(() => result.current.submitContent("ตอนตีสอง"));
    await waitFor(() => expect(result.current.pendingQuestionId).toBe(next.id));

    createCaseChatMessage.mockResolvedValueOnce(
      chatResponse({
        ...message("a", 5, "user", "บัญชีผู้ดูแล"),
        message_kind: "followup_answer" as const,
        in_reply_to_message_id: next.id,
      }),
    );
    act(() => result.current.submitContent("บัญชีผู้ดูแล"));
    await waitFor(() => expect(result.current.pendingQuestionId).toBeNull());
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

describe("the chat error modal", () => {
  it("opens again when a second send fails with the same error", async () => {
    createCaseChatMessage.mockRejectedValue(new Error("Network Error"));
    const { result } = render();
    await waitFor(() => expect(result.current.messages).toHaveLength(1));

    act(() => result.current.submitContent("สวัสดี"));
    await waitFor(() => expect(result.current.queryError).not.toBeNull());
    act(() => result.current.clearQueryError());
    await waitFor(() => expect(result.current.queryError).toBeNull());

    act(() => result.current.submitContent("สวัสดี"));
    await waitFor(() => expect(result.current.queryError).not.toBeNull());
    expect(createCaseChatMessage).toHaveBeenCalledTimes(2);
  });

  it("reloads the chat to retry a failed load, and sends nothing", async () => {
    createCaseChatMessage.mockResolvedValue(chatResponse(message("a", 2, "assistant", "ครับ")));
    const { result, queryClient } = render();
    await waitFor(() => expect(result.current.messages).toHaveLength(1));
    act(() => result.current.submitContent("สวัสดี"));
    await waitFor(() => expect(result.current.isSending).toBe(false));

    getCaseChat.mockRejectedValueOnce(new Error("the chat could not be read"));
    await act(() => queryClient.refetchQueries({ queryKey: caseQueryKeys.chat("a") }));
    await waitFor(() => expect(result.current.queryError).not.toBeNull());

    act(() => result.current.retryQuery());

    await waitFor(() => expect(result.current.queryError).toBeNull());
    expect(getCaseChat).toHaveBeenCalledTimes(3);
    expect(createCaseChatMessage).toHaveBeenCalledTimes(1);
  });

  it("keeps a closed load error closed until the chat fails to load again", async () => {
    getCaseChat.mockRejectedValue(new Error("the chat could not be read"));
    const { result, queryClient } = render();
    await waitFor(() => expect(result.current.queryError).not.toBeNull());

    act(() => result.current.clearQueryError());
    expect(result.current.queryError).toBeNull();

    await act(() => queryClient.refetchQueries({ queryKey: caseQueryKeys.chat("a") }));
    await waitFor(() => expect(result.current.queryError).not.toBeNull());
  });
});
