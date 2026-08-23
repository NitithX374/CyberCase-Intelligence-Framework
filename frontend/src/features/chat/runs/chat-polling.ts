import {
  getChatRun,
  getChatThread,
  type ChatThreadDetail,
} from "@/lib/api";

export const CHAT_POLL_INTERVAL_MS = 1000;

export function waitForNextChatPoll(signal: AbortSignal): Promise<void> {
  return new Promise((resolve) => {
    if (signal.aborted) {
      resolve();
      return;
    }

    const timeoutId = window.setTimeout(resolve, CHAT_POLL_INTERVAL_MS);
    signal.addEventListener(
      "abort",
      () => {
        window.clearTimeout(timeoutId);
        resolve();
      },
      { once: true },
    );
  });
}

export function isChatRequestCanceled(
  signal: AbortSignal,
  error: unknown,
): boolean {
  return (
    signal.aborted ||
    (typeof error === "object" &&
      error !== null &&
      "code" in error &&
      error.code === "ERR_CANCELED")
  );
}

interface ChatRunPollingOptions {
  threadId: string;
  runId: string;
  generation: number;
  signal: AbortSignal;
  isCurrentSelection: (threadId: string, generation: number) => boolean;
  applyThreadDetail: (
    detail: ChatThreadDetail,
    failureMessage?: string | null,
  ) => void;
}

export async function pollChatRunUntilCompleted({
  threadId,
  runId,
  generation,
  signal,
  isCurrentSelection,
  applyThreadDetail,
}: ChatRunPollingOptions): Promise<ChatThreadDetail | null> {
  let consecutiveReadFailures = 0;
  while (!signal.aborted && isCurrentSelection(threadId, generation)) {
    await waitForNextChatPoll(signal);
    if (signal.aborted || !isCurrentSelection(threadId, generation)) return null;
    let detail: ChatThreadDetail;
    try {
      detail = await getChatThread(threadId, signal);
      consecutiveReadFailures = 0;
    } catch (error) {
      if (
        isChatRequestCanceled(signal, error) ||
        !isCurrentSelection(threadId, generation)
      ) {
        return null;
      }
      consecutiveReadFailures += 1;
      if (consecutiveReadFailures > 1) throw error;
      continue;
    }
    if (!isCurrentSelection(threadId, generation)) return null;
    if (detail.status === "processing") {
      applyThreadDetail(detail);
      continue;
    }
    let run;
    try {
      run = await getChatRun(threadId, runId, signal);
    } catch (error) {
      if (
        isChatRequestCanceled(signal, error) ||
        !isCurrentSelection(threadId, generation)
      ) {
        return null;
      }
      throw error;
    }
    if (!isCurrentSelection(threadId, generation)) return null;
    if (run.status === "failed") {
      applyThreadDetail(
        detail,
        run.error_message || "Background processing failed. Retry the answer.",
      );
      return null;
    }
    if (run.status === "completed") {
      applyThreadDetail(detail);
      return detail;
    }
  }
  return null;
}
