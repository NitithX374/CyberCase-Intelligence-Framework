import { afterEach, beforeEach, expect, it, vi } from "vitest";
import * as api from "@/lib/api";
import { pollCaseRunUntilSettled, waitForNextChatPoll } from "@/features/chat/runs/chat-polling";
import { caseAccepted, deferred, message, thread } from "./chat-session-test-support";

beforeEach(() => { vi.useFakeTimers(); });
afterEach(() => { vi.useRealTimers(); vi.restoreAllMocks(); });

it("preserves the CaseRun one-read retry budget and then surfaces the error", async () => {
  const controller = new AbortController();
  const failure = new Error("Read failed");
  const readRun = vi.fn().mockRejectedValue(failure);
  const apply = vi.fn();
  const completion = pollCaseRunUntilSettled({
    runId: "run-1", signal: controller.signal, isCurrent: () => true,
    readRun, readThread: vi.fn(), applyThreadDetail: apply,
  });
  const assertion = expect(completion).rejects.toThrow("Read failed");
  await vi.advanceTimersByTimeAsync(2000);
  await assertion;
  expect(readRun).toHaveBeenCalledTimes(2);
  expect(apply).not.toHaveBeenCalled();
});

it("surfaces a CaseRun failure even when the thread response has already settled", async () => {
  const receipt = caseAccepted(message("a", 1, "user"));
  const apply = vi.fn();
  const detail = thread("a", "answered");
  const completion = pollCaseRunUntilSettled({
    runId: receipt.run.id,
    signal: new AbortController().signal, isCurrent: () => true,
    readRun: async () => ({ ...receipt.run, status: "failed", error_message: "Analysis failed" }),
    readThread: async () => detail, applyThreadDetail: apply,
  });
  await vi.advanceTimersByTimeAsync(1000);
  expect(await completion).toBeNull();
  expect(apply).toHaveBeenCalledWith(detail, "Analysis failed");
});

it("does not apply a run result after cancellation during its HTTP request", async () => {
  const controller = new AbortController();
  const waiting = deferred<api.CaseRunRead>();
  const apply = vi.fn();
  const completion = pollCaseRunUntilSettled({
    runId: "run-1", signal: controller.signal,
    isCurrent: () => true, readRun: () => waiting.promise,
    readThread: async () => thread("a", "answered"),
    applyThreadDetail: apply,
  });
  await vi.advanceTimersByTimeAsync(1000);
  controller.abort();
  waiting.resolve({
    ...caseAccepted(message("a", 1, "user")).run,
    status: "completed",
  });
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
