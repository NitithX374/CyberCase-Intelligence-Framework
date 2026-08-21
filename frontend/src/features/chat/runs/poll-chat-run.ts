import {
  getChatRun,
  getChatThread,
  type ChatThreadDetail,
} from "@/lib/api";
import {
  isChatRequestCanceled,
  waitForNextChatPoll,
} from "./chat-polling";

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
