import { act, cleanup } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "@/lib/api";
import { caseQueryKeys } from "@/hooks/useCaseQueries";
import { readAccountValue } from "@/lib/account-storage";
import { caseAccepted, deferred, message, renderSession, caseChat, tick } from "./chat-session-test-support";

beforeEach(() => { vi.useFakeTimers(); localStorage.clear(); });
afterEach(() => { cleanup(); vi.useRealTimers(); vi.restoreAllMocks(); });

describe("chat submission lifecycle", () => {
  it("sends an idle Case Chat message without starting implicit analysis", async () => {
    vi.spyOn(api, "getCaseChat").mockResolvedValue(caseChat("a", "idle"));
    const send = vi.spyOn(api, "createCaseChatMessage").mockRejectedValue(new Error("Analyze the Case before asking a Chat question"));
    const { result } = renderSession();
    await act(async () => { await result.current.selectCaseChat("a"); });
    await tick();
    act(() => result.current.submitContent("What happened?", "message"));
    await tick();
    expect(send.mock.calls[0]).toHaveLength(4);
    expect(result.current.queryError).toContain("Analyze the Case");
  });

  it("sends a clarification answer when caseChat status is awaiting_followup", async () => {
    const question = followUpQuestion();
    vi.spyOn(api, "getCaseChat").mockResolvedValue(caseChat("a", "awaiting_followup", [question]));
    const send = vi.spyOn(api, "createCaseChatMessage").mockRejectedValue(new Error("Testing follow-up"));
    const { result } = renderSession();
    await act(async () => { await result.current.selectCaseChat("a"); });
    await tick();
    act(() => result.current.submitFollowUp({
      gapId: "gap-host",
      answer: "Stole Phone B",
      disposition: "answered",
    }));
    await tick();
    expect(send.mock.calls[0][1]).toBe("Stole Phone B");
    expect(send.mock.calls[0][4]).toBe("followup_answer");
    expect(send.mock.calls[0][5]).toBe(question.id);
    expect(send.mock.calls[0][6]).toEqual({
      gap_id: "gap-host",
      answer: "Stole Phone B",
      disposition: "answered",
    });
  });
  it("reuses the idempotency key after a lost receipt and settles synchronous Ask response", async () => {
    const request = message("a", 1, "user", "Evidence");
    const assistant = message("a", 2, "assistant", "Answer");
    const receipt: api.CaseChatMessageResult = {
      message: request,
      assistant_message: assistant,
      run: null,
    };
    vi.spyOn(api, "getCaseChat")
      .mockResolvedValueOnce(caseChat())
      .mockResolvedValueOnce(caseChat("a", "answered", [request, assistant]));
    const send = vi.spyOn(api, "createCaseChatMessage")
      .mockRejectedValueOnce(new Error("Network failure"))
      .mockResolvedValueOnce(receipt);
    const { result, queryClient } = renderSession();
    await act(async () => { await result.current.selectCaseChat("a"); });
    await tick();
    act(() => {
      result.current.changeInput("Evidence");
      result.current.submitContent("Evidence", "message");
    });
    await tick();
    const key = send.mock.calls[0][2];
    expect(result.current.input).toBe("Evidence");
    expect(result.current.queryError).toBeTruthy();
    act(() => result.current.submitContent("Evidence", "message"));
    await tick();
    expect(send.mock.calls[1][2]).toBe(key);
    expect(result.current.messages).toEqual([request, assistant]);
    expect(queryClient.getQueryData<api.CaseChatDetail>(caseQueryKeys.chat("a"))?.messages).toEqual([request, assistant]);
    expect(result.current.input).toBe("");
    expect(result.current.getPendingSubmission()).toBeNull();
    expect(readAccountValue("pending-case-chat:a")).toBeNull();
    expect(result.current.messages).toHaveLength(2);
  });

  it("does not send duplicate messages when submit is triggered twice before rerender", async () => {
    vi.spyOn(api, "getCaseChat").mockResolvedValue(caseChat());
    const waiting = deferred<api.CaseChatMessageResult>();
    const send = vi.spyOn(api, "createCaseChatMessage").mockReturnValue(waiting.promise);
    const { result } = renderSession();
    await act(async () => { await result.current.selectCaseChat("a"); });
    await tick();
    act(() => {
      result.current.submitContent("Evidence", "message");
      result.current.submitContent("Evidence", "message");
    });
    expect(send).toHaveBeenCalledTimes(1);
    waiting.reject(new Error("Network failure"));
    await tick();
  });

  it("shows the outgoing Ask message while the response is pending", async () => {
    vi.spyOn(api, "getCaseChat")
      .mockResolvedValueOnce(caseChat())
      .mockResolvedValue(caseChat("a", "answered", [message("a", 1, "user", "Evidence")]));
    const waiting = deferred<api.CaseChatMessageResult>();
    vi.spyOn(api, "createCaseChatMessage").mockReturnValue(waiting.promise);
    const { result, queryClient } = renderSession();
    await act(async () => { await result.current.selectCaseChat("a"); });
    await tick();

    act(() => result.current.submitContent("Evidence", "message"));

    const pending = queryClient.getQueryData<api.CaseChatDetail>(caseQueryKeys.chat("a"));
    expect(pending?.messages).toHaveLength(1);
    expect(pending?.messages[0]).toMatchObject({
      role: "user",
      content: "Evidence",
      id: expect.stringMatching(/^optimistic:/),
    });

    waiting.resolve(caseAccepted(message("a", 1, "user", "Evidence")));
    await tick();
    expect(queryClient.getQueryData<api.CaseChatDetail>(caseQueryKeys.chat("a"))?.messages).toEqual([
      message("a", 1, "user", "Evidence"),
    ]);
  });

  it("ignores a late message receipt after switching chats", async () => {
    vi.spyOn(api, "getCaseChat").mockImplementation(async (id) => caseChat(id));
    const waiting = deferred<api.CaseChatMessageResult>();
    vi.spyOn(api, "createCaseChatMessage").mockReturnValue(waiting.promise);
    const { result } = renderSession();
    await act(async () => { await result.current.selectCaseChat("a"); });
    await tick();
    act(() => result.current.submitContent("Evidence", "message"));
    await act(async () => { await result.current.selectCaseChat("b"); });
    await tick();
    await act(async () => { waiting.resolve(caseAccepted(message("a", 1, "user"))); });
    await tick();
    expect(result.current.activeCaseChatId).toBe("b");
    expect(result.current.messages).toEqual([]);
  });

  it("retains a failed clarification answer and the same request key for retry", async () => {
    vi.spyOn(api, "getCaseChat").mockResolvedValue(caseChat("a", "awaiting_followup", [followUpQuestion()]));
    const send = vi.spyOn(api, "createCaseChatMessage").mockRejectedValue(new Error("Network failure"));
    const { result } = renderSession();
    await act(async () => { await result.current.selectCaseChat("a"); });
    await tick();
    const answer = { gapId: "gap-host", answer: "Unknown", disposition: "answered" as const };
    act(() => {
      result.current.submitFollowUp(answer);
    });
    await tick();
    expect(result.current.chatStatus).toBe("awaiting_followup");
    expect(result.current.pendingFollowUp?.question).toBe("When?");
    expect(result.current.getPendingSubmission()?.followUpAnswer).toEqual(answer);
    act(() => result.current.retryQuery());
    await tick();
    expect(send.mock.calls[1][2]).toBe(send.mock.calls[0][2]);
  });

  it("seeds the run cache and delegates settlement to useCaseRunPolling when clarification triggers analysis", async () => {
    const question = followUpQuestion();
    const answer = message("a", 2, "user", "Evidence");
    const receipt = caseAccepted(answer);
    vi.spyOn(api, "getCaseChat")
      .mockResolvedValueOnce(caseChat("a", "awaiting_followup", [question]))
      .mockResolvedValue(caseChat("a", "answered", [question, answer]));
    vi.spyOn(api, "createCaseChatMessage").mockResolvedValue(receipt);
    const { result, queryClient, upsert } = renderSession();
    await act(async () => { await result.current.selectCaseChat("a"); });
    await tick();
    act(() => result.current.submitFollowUp({
      gapId: "gap-host",
      answer: "Evidence",
      disposition: "answered",
    }));
    await tick();
    expect(queryClient.getQueryData(caseQueryKeys.run("a", receipt.run!.id))).toBeDefined();
    expect(upsert).toHaveBeenCalledWith(expect.objectContaining({
      active_run_id: receipt.run!.id,
    }));
  });

  it("immediately settles synchronous Ask message and updates chat cache", async () => {
    const request = message("a", 1, "user", "What happened?");
    const assistant = message("a", 2, "assistant", "Answer");
    const nativeReceipt: api.CaseChatMessageResult = {
      message: request,
      assistant_message: assistant,
      run: null,
    };
    vi.spyOn(api, "getCaseChat")
      .mockResolvedValueOnce(caseChat("a", "answered"))
      .mockResolvedValue(caseChat("a", "answered", [request, assistant]));
    const send = vi.spyOn(api, "createCaseChatMessage").mockResolvedValue(nativeReceipt);
    const { result, queryClient } = renderSession("a");
    await act(async () => { await result.current.selectCaseChat("a"); });
    await tick();
    act(() => {
      result.current.changeInput("What happened?");
      result.current.submitContent("What happened?", "message");
    });
    await tick();
    expect(send).toHaveBeenCalledWith(
      "a", "What happened?", expect.any(String),
      expect.any(AbortSignal),
    );
    expect(result.current.messages).toEqual([request, assistant]);
    expect(queryClient.getQueryData<api.CaseChatDetail>(caseQueryKeys.chat("a"))?.messages).toEqual([request, assistant]);
    expect(result.current.input).toBe("");
    expect(result.current.getPendingSubmission()).toBeNull();
  });

  it("clears activity and localStorage pending submission when accepted.run is null (e.g. skipped follow-up)", async () => {
    const question = followUpQuestion();
    vi.spyOn(api, "getCaseChat")
      .mockResolvedValueOnce(caseChat("a", "awaiting_followup", [question]))
      .mockResolvedValueOnce(caseChat("a", "idle", [question, message("a", 3, "user", "I don't have this information")]));

    const send = vi.spyOn(api, "createCaseChatMessage").mockResolvedValue({
      message: message("a", 3, "user", "I don't have this information"),
      run: null,
    });

    const { result } = renderSession();
    await act(async () => { await result.current.selectCaseChat("a"); });
    await tick();

    act(() => {
      result.current.submitFollowUp({
        gapId: "gap-host",
        answer: "I don't have this information",
        disposition: "skipped",
      });
    });
    await tick(50);

    expect(send).toHaveBeenCalled();
    expect(result.current.phase).not.toBe("querying");
    expect(readAccountValue("pending-case-chat:a")).toBeNull();
  });
});

function followUpQuestion(): api.ChatMessageRead {
  return {
    ...message("a", 2, "assistant", "When?"),
    message_kind: "followup_question",
    analysis_result_id: "analysis-1",
    metadata_json: {
      action: "follow_up",
      chat_followup: {
        root_ordinal: 2,
        round: 1,
        source_analysis_id: "analysis-1",
        source_revision: 1,
        gap: {
          gap_id: "gap-host",
          gap_key: "affected_host",
          topic: "affected host",
          status: "NOT_PROVIDED",
          description: "The affected host was not provided.",
          affects: "The impacted system cannot be scoped.",
          reason: "The reported event has no host identifier.",
          priority: "high",
          askable: true,
          clarification_question: "When?",
        },
      },
    },
  };
}
