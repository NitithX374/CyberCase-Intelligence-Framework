import { act, cleanup } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "@/lib/api";
import { chatQueryKeys } from "@/hooks/use-chat-queries";
import { accepted, deferred, message, renderSession, thread, tick } from "./chat-session-test-support";

beforeEach(() => { vi.useFakeTimers(); });
afterEach(() => { cleanup(); vi.useRealTimers(); vi.restoreAllMocks(); });

describe("chat submission lifecycle", () => {
  it("reuses the idempotency key after a lost receipt and clears the draft only after persisted output", async () => {
    const request = message("a", 1, "user", "Evidence");
    const receipt = accepted(request);
    vi.spyOn(api, "getChatThread")
      .mockResolvedValueOnce(thread())
      .mockResolvedValueOnce(thread("a", "processing", [request]))
      .mockResolvedValueOnce(thread("a", "answered", [request, message("a", 2, "assistant")]));
    const send = vi.spyOn(api, "createChatMessage")
      .mockRejectedValueOnce(new Error("Network failure"))
      .mockResolvedValueOnce(receipt);
    vi.spyOn(api, "getChatRun").mockResolvedValue({ ...receipt.run, status: "completed" });
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
    expect(result.current.session.input).toBe("Evidence");
    expect(result.current.session.getPendingSubmission()?.key).toBe(key);
    await tick(1000);
    expect(result.current.session.input).toBe("");
    expect(result.current.session.getPendingSubmission()).toBeNull();
    expect(result.current.session.messages).toHaveLength(2);
  });

  it("does not send duplicate messages when submit is triggered twice before rerender", async () => {
    vi.spyOn(api, "getChatThread").mockResolvedValue(thread());
    const waiting = deferred<api.ChatMessageAccepted>();
    const send = vi.spyOn(api, "createChatMessage").mockReturnValue(waiting.promise);
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
    const waiting = deferred<api.ChatMessageAccepted>();
    vi.spyOn(api, "createChatMessage").mockReturnValue(waiting.promise);
    const { result } = renderSession();
    await act(async () => { await result.current.session.selectThread("a"); });
    await tick();
    const onAccepted = vi.fn();
    act(() => result.current.submitContent("Evidence", "message", undefined, onAccepted));
    await act(async () => { await result.current.session.selectThread("b"); });
    await tick();
    await act(async () => { waiting.resolve(accepted(message("a", 1, "user"))); });
    await tick();
    expect(result.current.session.activeThreadId).toBe("b");
    expect(result.current.session.messages).toEqual([]);
    expect(onAccepted).not.toHaveBeenCalled();
  });

  it("retains a failed clarification answer and the same request key for retry", async () => {
    vi.spyOn(api, "getChatThread").mockResolvedValue(thread("a", "awaiting_followup"));
    const send = vi.spyOn(api, "createChatMessage").mockRejectedValue(new Error("Network failure"));
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
    const receipt = accepted(request);
    vi.spyOn(api, "getChatThread")
      .mockResolvedValueOnce(thread())
      .mockResolvedValue(thread("a", "answered", [request]));
    vi.spyOn(api, "createChatMessage").mockResolvedValue(receipt);
    vi.spyOn(api, "getChatRun").mockResolvedValue({ ...receipt.run, status: "completed" });
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
    const receipt = accepted(questionMsg);
    vi.spyOn(api, "getChatThread").mockResolvedValue(thread("a", "answered", previous));
    const send = vi.spyOn(api, "createChatMessage").mockResolvedValue(receipt);
    vi.spyOn(api, "getChatRun").mockResolvedValue({ ...receipt.run, status: "completed" });
    const { result } = renderSession();
    await act(async () => { await result.current.session.selectThread("a"); });
    await tick();
    act(() => result.current.submitContent("What technique is this?", "message"));
    await tick();
    expect(send).toHaveBeenCalledTimes(1);
    expect(send.mock.calls[0][4]).toBe("ask");
    expect(result.current.session.queryError).toBeNull();
  });
});
