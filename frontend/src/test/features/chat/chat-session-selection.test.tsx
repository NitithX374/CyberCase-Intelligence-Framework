import { act, cleanup } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "@/lib/api";
import { chatQueryKeys } from "@/hooks/useChatQueries";
import { deferred, message, renderSession, thread, tick } from "./chat-session-test-support";

beforeEach(() => { vi.useFakeTimers(); });
afterEach(() => { cleanup(); vi.useRealTimers(); vi.restoreAllMocks(); });

describe("chat session selection", () => {
  it("cancels an old selection and ignores its late response, including when returning to the same chat", async () => {
    const old = deferred<api.ChatThreadDetail>();
    const reads = vi.spyOn(api, "getChatThread")
      .mockReturnValueOnce(old.promise)
      .mockResolvedValueOnce(thread("b", "answered", [message("b", 1, "user")]))
      .mockResolvedValueOnce(thread("a", "answered", [message("a", 2, "assistant", "Current")]));
    const { result, queryClient } = renderSession();
    let first!: Promise<void>;
    act(() => { first = result.current.session.selectThread("a"); });
    const signal = reads.mock.calls[0][1]!;
    await act(async () => { await result.current.session.selectThread("b"); });
    await tick();
    expect(signal.aborted).toBe(true);
    expect(result.current.session.messages[0].thread_id).toBe("b");
    await act(async () => { await result.current.session.selectThread("a"); });
    await tick();
    await act(async () => {
      old.resolve(thread("a", "answered", [message("a", 1, "assistant", "Stale")]));
      await first;
    });
    await tick();
    expect(result.current.session.messages[0].content).toBe("Current");
    expect(queryClient.getQueryData<api.ChatThreadDetail>(chatQueryKeys.detail("a"))?.messages[0].content).toBe("Current");
  });

  it("loads a processing Case Chat without starting the retired ChatRun poll", async () => {
    const processing = thread("a", "processing");
    const reads = vi.spyOn(api, "getChatThread").mockResolvedValue(processing);
    const runRead = vi.spyOn(api, "getChatRun");
    const { result, queryClient } = renderSession();
    await act(async () => { await result.current.session.selectThread("a"); });
    await tick();
    expect(result.current.session.threadStatus).toBe("processing");
    expect(result.current.session.messages).toEqual(processing.messages);
    expect(queryClient.getQueryData(chatQueryKeys.detail("a"))).toEqual(processing);
    expect(reads).toHaveBeenCalledTimes(1);
    expect(runRead).not.toHaveBeenCalled();
  });

  it("stops Case Chat selection on unmount and cancels the pending HTTP request", async () => {
    const waiting = deferred<api.ChatThreadDetail>();
    const reads = vi.spyOn(api, "getChatThread").mockReturnValue(waiting.promise);
    const { result, unmount, upsert } = renderSession();
    act(() => { void result.current.session.selectThread("a"); });
    await tick();
    expect(reads).toHaveBeenCalledTimes(1);
    const signal = reads.mock.calls[0][1]!;
    unmount();
    expect(signal.aborted).toBe(true);
    waiting.resolve(thread("a", "answered"));
    await tick(5000);
    expect(upsert).not.toHaveBeenCalled();
    expect(reads).toHaveBeenCalledTimes(1);
  });

  it("keeps the retry key when a selected chat is suspended and restored after deletion fails", async () => {
    vi.spyOn(api, "getChatThread").mockResolvedValue(thread());
    vi.spyOn(api, "createCaseChatMessage").mockRejectedValue(new Error("Network failure"));
    const { result } = renderSession();
    await act(async () => { await result.current.session.selectThread("a"); });
    await tick();
    act(() => result.current.submitContent("Evidence", "message"));
    await tick();
    const key = result.current.session.getPendingSubmission()?.key;
    act(() => { result.current.session.suspendThread("a"); });
    act(() => { result.current.session.restoreThread("a"); });
    await act(async () => { await result.current.session.selectThread("a"); });
    await tick();
    expect(result.current.session.getPendingSubmission()?.key).toBe(key);
  });
});
