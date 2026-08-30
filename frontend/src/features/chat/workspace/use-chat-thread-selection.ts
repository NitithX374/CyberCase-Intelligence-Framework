"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  getApiErrorMessage,
  getChatThread,
  type ChatThreadDetail,
  type ChatThreadRead,
  type PersistedChatMessage,
  type ThreadStatus,
} from "@/lib/api";
import {
  hasCompletedAssistantOutput,
  persistedRequestOrdinal,
  type ActiveChatFollowUp,
} from "@/lib/chat-followup";
import type { RunPhase } from "@/components/common/types";
import { isChatRequestCanceled, waitForNextChatPoll } from "../runs/chat-polling";
import type { PendingChatSubmission } from "./chat-workspace-types";

interface UseChatThreadSelectionOptions {
  cacheUpsertThread: (thread: ChatThreadRead) => void;
  deletedThreadIdsRef: React.MutableRefObject<Set<string>>;
  pendingSubmissionRef: React.MutableRefObject<PendingChatSubmission | null>;
}

interface ChatThreadSelection {
  activeThreadId: string | null;
  setActiveThreadId: React.Dispatch<React.SetStateAction<string | null>>;
  activeThreadIdRef: React.MutableRefObject<string | null>;
  selectionGenerationRef: React.MutableRefObject<number>;
  pollControllerRef: React.MutableRefObject<AbortController | null>;
  messages: PersistedChatMessage[];
  setMessages: React.Dispatch<React.SetStateAction<PersistedChatMessage[]>>;
  threadStatus: ThreadStatus | null;
  setThreadStatus: React.Dispatch<React.SetStateAction<ThreadStatus | null>>;
  phase: RunPhase;
  setPhase: React.Dispatch<React.SetStateAction<RunPhase>>;
  input: string;
  setInput: React.Dispatch<React.SetStateAction<string>>;
  pendingFollowUp: {
    threadId: string;
    followUp: ActiveChatFollowUp;
  } | null;
  setPendingFollowUp: React.Dispatch<
    React.SetStateAction<{
      threadId: string;
      followUp: ActiveChatFollowUp;
    } | null>
  >;
  postAnswerAction: "ask" | "add_case_info" | null;
  setPostAnswerAction: React.Dispatch<
    React.SetStateAction<"ask" | "add_case_info" | null>
  >;
  queryError: string | null;
  setQueryError: React.Dispatch<React.SetStateAction<string | null>>;
  upsertThread: (thread: ChatThreadRead) => void;
  isCurrentSelection: (threadId: string, generation: number) => boolean;
  applyThreadDetail: (
    detail: ChatThreadDetail,
    failureMessage?: string | null,
  ) => void;
  pollThreadUntilSettled: (
    threadId: string,
    generation: number,
    signal: AbortSignal,
  ) => Promise<void>;
  loadThread: (
    threadId: string,
    generation: number,
    signal: AbortSignal,
  ) => Promise<void>;
  selectThread: (threadId: string) => Promise<void>;
}

function phaseForThread(detail: ChatThreadDetail): RunPhase {
  if (detail.status === "processing") return "querying";
  if (detail.status === "awaiting_followup") return "awaiting_followup";
  if (detail.status === "failed") return "error";
  return detail.messages.length > 0 ? "ready" : "idle";
}

export function useChatThreadSelection({
  cacheUpsertThread,
  deletedThreadIdsRef,
  pendingSubmissionRef,
}: UseChatThreadSelectionOptions): ChatThreadSelection {
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const [threadStatus, setThreadStatus] = useState<ThreadStatus | null>(null);
  const [messages, setMessages] = useState<PersistedChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [postAnswerAction, setPostAnswerAction] = useState<
    "ask" | "add_case_info" | null
  >(null);
  const [pendingFollowUp, setPendingFollowUp] = useState<{
    threadId: string;
    followUp: ActiveChatFollowUp;
  } | null>(null);
  const [phase, setPhase] = useState<RunPhase>("idle");
  const [queryError, setQueryError] = useState<string | null>(null);
  const activeThreadIdRef = useRef<string | null>(null);
  const selectionGenerationRef = useRef(0);
  const pollControllerRef = useRef<AbortController | null>(null);

  const upsertThread = useCallback(
    (thread: ChatThreadRead) => {
      if (deletedThreadIdsRef.current.has(thread.id)) return;
      cacheUpsertThread(thread);
    },
    [cacheUpsertThread, deletedThreadIdsRef],
  );

  const isCurrentSelection = useCallback(
    (threadId: string, generation: number) =>
      activeThreadIdRef.current === threadId &&
      selectionGenerationRef.current === generation,
    [],
  );

  const applyThreadDetail = useCallback(
    (detail: ChatThreadDetail, failureMessage?: string | null) => {
      const orderedMessages = [...detail.messages].sort(
        (left, right) => left.ordinal - right.ordinal,
      );
      setMessages(orderedMessages);
      setThreadStatus(detail.status);
      setPhase(phaseForThread(detail));
      upsertThread(detail);

      const pending = pendingSubmissionRef.current;
      const recoveredRequestOrdinal =
        pending?.threadId === detail.id && pending.requestOrdinal === undefined
          ? persistedRequestOrdinal(
              detail,
              pending.lastKnownMessageOrdinal,
              pending.content,
            )
          : undefined;
      if (
        pending?.threadId === detail.id &&
        recoveredRequestOrdinal !== undefined
      ) {
        pendingSubmissionRef.current = {
          ...pending,
          requestOrdinal: recoveredRequestOrdinal,
        };
      }
      const requestOrdinal =
        pending?.threadId === detail.id
          ? pending.requestOrdinal ?? recoveredRequestOrdinal
          : undefined;

      if (failureMessage || detail.status === "failed") {
        setQueryError(
          failureMessage ||
            "Background processing failed. Retry the saved message.",
        );
      } else if (
        pending?.threadId !== detail.id ||
        requestOrdinal !== undefined
      ) {
        setQueryError(null);
      }

      if (
        pending?.threadId === detail.id &&
        requestOrdinal !== undefined &&
        hasCompletedAssistantOutput(detail, requestOrdinal)
      ) {
        pendingSubmissionRef.current = null;
        setPendingFollowUp(null);
        setInput("");
        setPostAnswerAction(null);
      }
    },
    [pendingSubmissionRef, upsertThread],
  );

  const pollThreadUntilSettled = useCallback(
    async (
      threadId: string,
      generation: number,
      signal: AbortSignal,
    ): Promise<void> => {
      let consecutiveReadFailures = 0;
      while (!signal.aborted && isCurrentSelection(threadId, generation)) {
        await waitForNextChatPoll(signal);
        if (signal.aborted || !isCurrentSelection(threadId, generation)) return;
        let detail: ChatThreadDetail;
        try {
          detail = await getChatThread(threadId, signal);
          consecutiveReadFailures = 0;
        } catch (error) {
          if (
            isChatRequestCanceled(signal, error) ||
            !isCurrentSelection(threadId, generation)
          ) {
            return;
          }
          consecutiveReadFailures += 1;
          if (consecutiveReadFailures > 1) throw error;
          continue;
        }
        if (!isCurrentSelection(threadId, generation)) return;
        applyThreadDetail(detail);
        if (detail.status !== "processing") return;
      }
    },
    [applyThreadDetail, isCurrentSelection],
  );

  const loadThread = useCallback(
    async (
      threadId: string,
      generation: number,
      signal: AbortSignal,
    ): Promise<void> => {
      try {
        const detail = await getChatThread(threadId, signal);
        if (!isCurrentSelection(threadId, generation)) return;
        applyThreadDetail(detail);
        if (detail.status === "processing") {
          await pollThreadUntilSettled(threadId, generation, signal);
        }
      } catch (error) {
        if (isChatRequestCanceled(signal, error) || !isCurrentSelection(threadId, generation)) {
          return;
        }
        setPhase("error");
        setQueryError(getApiErrorMessage(error, "The chat could not be loaded."));
      }
    },
    [applyThreadDetail, isCurrentSelection, pollThreadUntilSettled],
  );

  const selectThread = useCallback(
    async (threadId: string): Promise<void> => {
      pollControllerRef.current?.abort();
      const controller = new AbortController();
      pollControllerRef.current = controller;
      const generation = selectionGenerationRef.current + 1;
      selectionGenerationRef.current = generation;
      activeThreadIdRef.current = threadId;
      setActiveThreadId(threadId);
      setPostAnswerAction(null);
      const pending = pendingSubmissionRef.current;
      setInput(
        pending?.threadId === threadId && pending.kind === "followup"
          ? pending.content
          : "",
      );
      setPendingFollowUp((current) =>
        current?.threadId === threadId ? current : null,
      );
      setMessages([]);
      setThreadStatus(null);
      setQueryError((current) =>
        pending?.threadId === threadId ? current : null,
      );
      setPhase("querying");
      await loadThread(threadId, generation, controller.signal);
    },
    [loadThread, pendingSubmissionRef],
  );

  useEffect(() => {
    return () => {
      pollControllerRef.current?.abort();
    };
  }, []);

  return {
    activeThreadId,
    setActiveThreadId,
    activeThreadIdRef,
    selectionGenerationRef,
    pollControllerRef,
    messages,
    setMessages,
    threadStatus,
    setThreadStatus,
    phase,
    setPhase,
    input,
    setInput,
    pendingFollowUp,
    setPendingFollowUp,
    postAnswerAction,
    setPostAnswerAction,
    queryError,
    setQueryError,
    upsertThread,
    isCurrentSelection,
    applyThreadDetail,
    pollThreadUntilSettled,
    loadThread,
    selectThread,
  };
}
