import { act, cleanup } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "@/lib/api";
import { chatQueryKeys } from "@/hooks/useChatQueries";
import { readAccountValue } from "@/lib/account-storage";
import { caseAccepted, deferred, message, renderSession, thread, tick } from "./chat-session-test-support";

beforeEach(() => { vi.useFakeTimers(); localStorage.clear(); });
afterEach(() => { cleanup(); vi.useRealTimers(); vi.restoreAllMocks(); });

describe("chat submission lifecycle", () => {
  it("sends an idle Chat message as ask rather than implicit analysis", async () => {
    vi.spyOn(api, "getChatThread").mockResolvedValue(thread("a", "idle"));
    const send = vi.spyOn(api, "createCaseChatMessage").mockRejectedValue(new Error("Analyze the Case before asking a Chat question"));
    const { result } = renderSession();
    await act(async () => { await result.current.session.selectThread("a"); });
    await tick();
    act(() => result.current.submitContent("What happened?", "message"));
    await tick();
    expect(send.mock.calls[0][4]).toBe("ask");
    expect(result.current.session.queryError).toContain("Analyze the Case");
  });

  it("sends chat message as add_case_info when thread status is awaiting_followup", async () => {
    vi.spyOn(api, "getChatThread").mockResolvedValue(thread("a", "awaiting_followup"));
    const send = vi.spyOn(api, "createCaseChatMessage").mockRejectedValue(new Error("Testing follow-up"));
    const { result } = renderSession();
    await act(async () => { await result.current.session.selectThread("a"); });
    await tick();
    act(() => result.current.submitContent("Stole Phone B", "message"));
    await tick();
    expect(send.mock.calls[0][4]).toBe("add_case_info");
  });
  it("reuses the idempotency key after a lost receipt and clears the draft only after persisted output", async () => {
    const request = message("a", 1, "user", "Evidence");
    const receipt = caseAccepted(request);
    vi.spyOn(api, "getChatThread")
      .mockResolvedValueOnce(thread())
      .mockResolvedValueOnce(thread("a", "answered", [request, message("a", 2, "assistant")]));
    const send = vi.spyOn(api, "createCaseChatMessage")
      .mockRejectedValueOnce(new Error("Network failure"))
      .mockResolvedValueOnce(receipt);
    vi.spyOn(api, "getCaseRun").mockResolvedValue({ ...receipt.run, status: "completed" });
    const { result, queryClient } = renderSession();
    await act(async () => { await result.current.session.selectThread("a"); });
    await tick();
    act(() => {
      result.current.session.changeInput("Evidence");
      result.current.submitContent("Evidence", "message");
    });
    await tick();
    const key = send.mock.calls[0][2];
    expect(result.current.session.input).toBe("Evidence");
    expect(result.current.session.queryError).toBeTruthy();
    act(() => result.current.submitContent("Evidence", "message"));
    await tick();
    expect(send.mock.calls[1][2]).toBe(key);
    expect(result.current.session.messages).toEqual([request]);
    expect(queryClient.getQueryData<api.ChatThreadDetail>(chatQueryKeys.detail("a"))?.messages).toEqual([request]);
    await tick(1000);
    expect(result.current.session.input).toBe("");
    expect(result.current.session.getPendingSubmission()).toBeNull();
    expect(readAccountValue("pending-case-chat:a")).toBeNull();
    expect(result.current.session.messages).toHaveLength(2);
  });

  it("does not send duplicate messages when submit is triggered twice before rerender", async () => {
    vi.spyOn(api, "getChatThread").mockResolvedValue(thread());
    const waiting = deferred<api.CaseChatMessageAccepted>();
    const send = vi.spyOn(api, "createCaseChatMessage").mockReturnValue(waiting.promise);
    const { result } = renderSession();
    await act(async () => { await result.current.session.selectThread("a"); });
    await tick();
    act(() => {
      result.current.submitContent("Evidence", "message");
      result.current.submitContent("Evidence", "message");
    });
    expect(send).toHaveBeenCalledTimes(1);
    waiting.reject(new Error("Network failure"));
    await tick();
  });

  it("ignores a late message receipt after switching chats", async () => {
    vi.spyOn(api, "getChatThread").mockImplementation(async (id) => thread(id));
    const waiting = deferred<api.CaseChatMessageAccepted>();
    vi.spyOn(api, "createCaseChatMessage").mockReturnValue(waiting.promise);
    const { result } = renderSession();
    await act(async () => { await result.current.session.selectThread("a"); });
    await tick();
    act(() => result.current.submitContent("Evidence", "message"));
    await act(async () => { await result.current.session.selectThread("b"); });
    await tick();
    await act(async () => { waiting.resolve(caseAccepted(message("a", 1, "user"))); });
    await tick();
    expect(result.current.session.activeThreadId).toBe("b");
    expect(result.current.session.messages).toEqual([]);
  });

  it("retains a failed clarification answer and the same request key for retry", async () => {
    vi.spyOn(api, "getChatThread").mockResolvedValue(thread("a", "awaiting_followup"));
    const send = vi.spyOn(api, "createCaseChatMessage").mockRejectedValue(new Error("Network failure"));
    const { result } = renderSession();
    await act(async () => { await result.current.session.selectThread("a"); });
    await tick();
    const followUp = { question: "When?", entries: [], rootOrdinal: 1 };
    act(() => {
      result.current.session.changeInput("Unknown");
      result.current.submitContent("Unknown", "followup", followUp);
    });
    await tick();
    expect(result.current.session.threadStatus).toBe("awaiting_followup");
    expect(result.current.session.input).toBe("Unknown");
    expect(result.current.session.pendingFollowUp?.followUp).toEqual(followUp);
    act(() => result.current.submitContent("Unknown", "followup", followUp));
    await tick();
    expect(send.mock.calls[1][2]).toBe(send.mock.calls[0][2]);
  });

  it("reports a completed run without assistant output and retains its submission for retry", async () => {
    const request = message("a", 1, "user", "Evidence");
    const receipt = caseAccepted(request);
    vi.spyOn(api, "getChatThread")
      .mockResolvedValueOnce(thread())
      .mockResolvedValue(thread("a", "answered", [request]));
    vi.spyOn(api, "createCaseChatMessage").mockResolvedValue(receipt);
    vi.spyOn(api, "getCaseRun").mockResolvedValue({ ...receipt.run, status: "completed" });
    const { result } = renderSession();
    await act(async () => { await result.current.session.selectThread("a"); });
    await tick();
    act(() => result.current.submitContent("Evidence", "message"));
    await tick(1000);
    expect(result.current.session.queryError).toContain("did not persist an assistant response");
    expect(result.current.session.getPendingSubmission()?.content).toBe("Evidence");
  });

  it("defaults post-answer action to 'ask' when submitting on an answered thread without explicit choice", async () => {
    const previous = [message("a", 1, "user", "Evidence"), message("a", 2, "assistant", "Summary")];
    const questionMsg = message("a", 3, "user", "What technique is this?");
    const receipt = caseAccepted(questionMsg, "ask");
    vi.spyOn(api, "getChatThread").mockResolvedValue(thread("a", "answered", previous));
    const send = vi.spyOn(api, "createCaseChatMessage").mockResolvedValue(receipt);
    vi.spyOn(api, "getCaseRun").mockResolvedValue({ ...receipt.run, status: "completed" });
    const { result } = renderSession();
    await act(async () => { await result.current.session.selectThread("a"); });
    await tick();
    act(() => result.current.submitContent("What technique is this?", "message"));
    await tick();
    expect(send).toHaveBeenCalledTimes(1);
    expect(send.mock.calls[0][4]).toBe("ask");
    expect(result.current.session.queryError).toBeNull();
  });

  it("does not let a persisted add-case-info choice change an ordinary Chat question", async () => {
    const previous = [message("a", 1, "user", "Evidence"), message("a", 2, "assistant", "Summary")];
    const questionMsg = message("a", 3, "user", "What technique is this?");
    const receipt = caseAccepted(questionMsg, "ask");
    vi.spyOn(api, "getChatThread").mockResolvedValue(thread("a", "answered", previous));
    const send = vi.spyOn(api, "createCaseChatMessage").mockResolvedValue(receipt);
    vi.spyOn(api, "getCaseRun").mockResolvedValue({ ...receipt.run, status: "completed" });
    const { result } = renderSession();
    await act(async () => { await result.current.session.selectThread("a"); });
    await tick();
    act(() => { result.current.session.changePostAnswerAction("add_case_info"); });
    await tick();
    expect(result.current.session.threadStatus).toBe("answered");
    expect(result.current.session.postAnswerAction).toBe("add_case_info");
    act(() => { result.current.submitContent("What technique is this?", "message"); });
    await tick();
    expect(send).toHaveBeenCalledTimes(1);
    expect(send.mock.calls[0][4]).toBe("ask");
  });

  it("uses the explicit CaseRun transport for Case Chat submissions", async () => {
    const request = message("a", 1, "user", "What happened?");
    const nativeReceipt: api.CaseChatMessageAccepted = {
      message: request,
      run: {
        id: "case-run-1",
        case_id: "a",
        operation: "ask",
        snapshot_id: "snapshot-1",
        request_message_id: request.id,
        context_analysis_result_id: "result-1",
        clarification_id: null,
        status: "queued",
        attempt_count: 0,
        error_code: null,
        error_message: null,
        created_at: request.created_at,
        started_at: null,
        finished_at: null,
        updated_at: request.created_at,
      },
    };
    vi.spyOn(api, "getChatThread")
      .mockResolvedValueOnce(thread("a", "answered"))
      .mockResolvedValue(thread("a", "answered", [request, message("a", 2, "assistant", "Answer")]));
    const send = vi.spyOn(api, "createCaseChatMessage").mockResolvedValue(nativeReceipt);
    const runRead = vi.spyOn(api, "getCaseRun").mockResolvedValue({
      ...nativeReceipt.run,
      status: "completed",
    });
    const legacyRunRead = vi.spyOn(api, "getChatRun");
    const { result } = renderSession("a");
    await act(async () => { await result.current.session.selectThread("a"); });
    await tick();
    act(() => {
      result.current.session.changeInput("What happened?");
      result.current.submitContent("What happened?", "message");
    });
    await tick(1000);
    expect(send).toHaveBeenCalledWith(
      "a", "What happened?", expect.any(String),
      expect.any(AbortSignal), "ask",
    );
    expect(runRead).toHaveBeenCalledWith("a", nativeReceipt.run.id, expect.any(AbortSignal));
    expect(legacyRunRead).not.toHaveBeenCalled();
    expect(result.current.session.messages).toEqual([request, message("a", 2, "assistant", "Answer")]);
  });
});
