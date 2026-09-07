import { afterEach, beforeEach, expect, it, vi } from "vitest";
import * as api from "@/lib/api";
import { pollChatThreadUntilSettled, waitForNextChatPoll } from "@/features/chat/runs/chat-polling";
import { accepted, deferred, message, thread } from "./chat-session-test-support";

beforeEach(() => { vi.useFakeTimers(); });
afterEach(() => { vi.useRealTimers(); vi.restoreAllMocks(); });

it("preserves the existing one-read retry budget and then surfaces the error", async () => {
  const controller = new AbortController();
  const failure = new Error("Read failed");
  const readThread = vi.fn().mockRejectedValue(failure);
  const apply = vi.fn();
  const completion = pollChatThreadUntilSettled({
    threadId: "a", signal: controller.signal, isCurrent: () => true,
    readThread, applyThreadDetail: apply,
  });
  const assertion = expect(completion).rejects.toThrow("Read failed");
  await vi.advanceTimersByTimeAsync(2000);
  await assertion;
  expect(readThread).toHaveBeenCalledTimes(2);
  expect(apply).not.toHaveBeenCalled();
});

it("surfaces a run failure even when the thread response has already settled", async () => {
  const receipt = accepted(message("a", 1, "user"));
  vi.spyOn(api, "getChatRun").mockResolvedValue({
    ...receipt.run, status: "failed", error_message: "Analysis failed",
  });
  const apply = vi.fn();
  const detail = thread("a", "answered");
  const completion = pollChatThreadUntilSettled({
    threadId: "a", runId: receipt.run.id,
    signal: new AbortController().signal, isCurrent: () => true,
    readThread: async () => detail, applyThreadDetail: apply,
  });
  await vi.advanceTimersByTimeAsync(1000);
  expect(await completion).toBeNull();
  expect(apply).toHaveBeenCalledWith(detail, "Analysis failed");
});

it("does not apply a run result after cancellation during its HTTP request", async () => {
  const controller = new AbortController();
  const waiting = deferred<api.ChatRun>();
  const receipt = accepted(message("a", 1, "user"));
  vi.spyOn(api, "getChatRun").mockReturnValue(waiting.promise);
  const apply = vi.fn();
  const completion = pollChatThreadUntilSettled({
    threadId: "a", runId: receipt.run.id, signal: controller.signal,
    isCurrent: () => true, readThread: async () => thread("a", "answered"),
    applyThreadDetail: apply,
  });
  await vi.advanceTimersByTimeAsync(1000);
  controller.abort();
  waiting.resolve({ ...receipt.run, status: "completed" });
  expect(await completion).toBeNull();
  expect(apply).not.toHaveBeenCalled();
});

it("releases abort listeners after each elapsed interval and cancels the next timer", async () => {
  const controller = new AbortController();
  const removed = vi.spyOn(controller.signal, "removeEventListener");
  const first = waitForNextChatPoll(controller.signal);
  await vi.advanceTimersByTimeAsync(1000);
  await first;
  expect(removed).toHaveBeenCalledTimes(1);
  const second = waitForNextChatPoll(controller.signal);
  controller.abort();
  await second;
  expect(removed).toHaveBeenCalledTimes(2);
  expect(vi.getTimerCount()).toBe(0);
});
