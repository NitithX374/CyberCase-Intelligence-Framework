import type { CaseChatDetail, CaseRunRead } from "@/lib/api";

export const CHAT_POLL_INTERVAL_MS = 1000;

export function waitForNextChatPoll(signal: AbortSignal): Promise<void> {
  return new Promise((resolve) => {
    if (signal.aborted) {
      resolve();
      return;
    }
    const finishChatPollingWait = () => {
      window.clearTimeout(timeoutId);
      signal.removeEventListener("abort", finishChatPollingWait);
      resolve();
    };
    const timeoutId = window.setTimeout(finishChatPollingWait, CHAT_POLL_INTERVAL_MS);
    signal.addEventListener("abort", finishChatPollingWait, { once: true });
  });
}

export function isChatRequestCanceled(signal: AbortSignal, error: unknown): boolean {
  return signal.aborted || (
    typeof error === "object" && error !== null &&
    "code" in error && error.code === "ERR_CANCELED"
  );
}

interface CasePollingOptions {
  runId: string;
  signal: AbortSignal;
  isCurrent: () => boolean;
  readRun: () => Promise<CaseRunRead>;
  readCaseChat: () => Promise<CaseChatDetail>;
  applyCaseChat: (detail: CaseChatDetail, failureMessage?: string) => void;
}

export async function pollCaseRunUntilSettled({
  signal,
  isCurrent,
  readRun,
  readCaseChat,
  applyCaseChat,
}: CasePollingOptions): Promise<CaseChatDetail | null> {
  let consecutiveReadFailures = 0;
  while (!signal.aborted && isCurrent()) {
    await waitForNextChatPoll(signal);
    if (signal.aborted || !isCurrent()) return null;
    let run: CaseRunRead;
    try {
      run = await readRun();
      consecutiveReadFailures = 0;
    } catch (error) {
      if (isChatRequestCanceled(signal, error) || !isCurrent()) return null;
      consecutiveReadFailures += 1;
      if (consecutiveReadFailures > 1) throw error;
      continue;
    }
    if (signal.aborted || !isCurrent()) return null;
    if (run.status === "queued" || run.status === "running") continue;
    let detail: CaseChatDetail;
    try {
      detail = await readCaseChat();
    } catch (error) {
      if (isChatRequestCanceled(signal, error) || !isCurrent()) return null;
      throw error;
    }
    if (signal.aborted || !isCurrent()) return null;
    if (run.status === "failed") {
      applyCaseChat(
        detail,
        run.error_message || "Case processing failed. Retry the saved message.",
      );
      return null;
    }
    applyCaseChat(detail);
    return detail;
  }
  return null;
}
