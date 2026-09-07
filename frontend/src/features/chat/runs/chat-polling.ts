import { getChatRun, type ChatThreadDetail } from "@/lib/api";

export const CHAT_POLL_INTERVAL_MS = 1000;

export function waitForNextChatPoll(signal: AbortSignal): Promise<void> {
  return new Promise((resolve) => {
    if (signal.aborted) {
      resolve();
      return;
    }
    const finish = () => {
      window.clearTimeout(timeoutId);
      signal.removeEventListener("abort", finish);
      resolve();
    };
    const timeoutId = window.setTimeout(finish, CHAT_POLL_INTERVAL_MS);
    signal.addEventListener("abort", finish, { once: true });
  });
}

export function isChatRequestCanceled(signal: AbortSignal, error: unknown): boolean {
  return signal.aborted || (
    typeof error === "object" && error !== null &&
    "code" in error && error.code === "ERR_CANCELED"
  );
}

interface ChatPollingOptions {
  threadId: string;
  runId?: string;
  signal: AbortSignal;
  isCurrent: () => boolean;
  readThread: () => Promise<ChatThreadDetail>;
  applyThreadDetail: (detail: ChatThreadDetail, failureMessage?: string) => void;
}

export async function pollChatThreadUntilSettled({
  threadId, runId, signal, isCurrent, readThread, applyThreadDetail,
}: ChatPollingOptions): Promise<ChatThreadDetail | null> {
  let consecutiveReadFailures = 0;
  while (!signal.aborted && isCurrent()) {
    await waitForNextChatPoll(signal);
    if (signal.aborted || !isCurrent()) return null;
    let detail: ChatThreadDetail;
    try {
      detail = await readThread();
      consecutiveReadFailures = 0;
    } catch (error) {
      if (isChatRequestCanceled(signal, error) || !isCurrent()) return null;
      consecutiveReadFailures += 1;
      if (consecutiveReadFailures > 1) throw error;
      continue;
    }
    if (signal.aborted || !isCurrent()) return null;
    if (detail.status === "processing") {
      applyThreadDetail(detail);
      continue;
    }
    if (runId) {
      let run;
      try {
        run = await getChatRun(threadId, runId, signal);
      } catch (error) {
        if (isChatRequestCanceled(signal, error) || !isCurrent()) return null;
        throw error;
      }
      if (signal.aborted || !isCurrent()) return null;
      if (run.status === "failed") {
        applyThreadDetail(detail, run.error_message || "Background processing failed. Retry the answer.");
        return null;
      }
      if (run.status !== "completed") continue;
    }
    applyThreadDetail(detail);
    return detail;
  }
  return null;
}
