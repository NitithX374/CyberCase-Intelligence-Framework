"use client";

import { useCallback } from "react";
import {
  createChatMessage,
  getApiErrorMessage,
  type ChatMessageAction,
  type ChatThreadDetail,
  type ChatThreadRead,
} from "@/lib/api";
import {
  hasCompletedAssistantOutput,
  type ActiveChatFollowUp,
} from "@/lib/chat-followup";
import type { RunPhase } from "@/components/common/types";
import {
  isChatRequestCanceled,
  pollChatRunUntilCompleted,
} from "./chat-polling";
import type { PendingChatSubmission } from "../workspace/chat-workspace-types";

interface RouterLike {
  push(path: string): void;
}

interface UseChatSubmissionOptions {
  activeThreadIdRef: React.MutableRefObject<string | null>;
  selectionGenerationRef: React.MutableRefObject<number>;
  pollControllerRef: React.MutableRefObject<AbortController | null>;
  pendingSubmissionRef: React.MutableRefObject<PendingChatSubmission | null>;
  messages: ChatThreadDetail["messages"];
  threads: ChatThreadRead[];
  phase: RunPhase;
  threadStatus: ChatThreadRead["status"] | null;
  postAnswerAction: ChatMessageAction | null;
  createThread: () => Promise<ChatThreadRead>;
  updateThread: (input: { threadId: string; title: string }) => Promise<ChatThreadRead>;
  router: RouterLike;
  chatPath: (threadId: string, view: "chat") => string;
  selectThread: (threadId: string) => Promise<void>;
  isCurrentSelection: (threadId: string, generation: number) => boolean;
  applyThreadDetail: (
    detail: ChatThreadDetail,
    failureMessage?: string | null,
  ) => void;
  upsertThread: (thread: ChatThreadRead) => void;
  setMessages: React.Dispatch<React.SetStateAction<ChatThreadDetail["messages"]>>;
  setPhase: React.Dispatch<React.SetStateAction<RunPhase>>;
  setThreadStatus: React.Dispatch<React.SetStateAction<ChatThreadRead["status"] | null>>;
  setQueryError: React.Dispatch<React.SetStateAction<string | null>>;
  setInput: React.Dispatch<React.SetStateAction<string>>;
  setPendingFollowUp: React.Dispatch<React.SetStateAction<{
    threadId: string;
    followUp: ActiveChatFollowUp;
  } | null>>;
  setPostAnswerAction: React.Dispatch<React.SetStateAction<ChatMessageAction | null>>;
}

export function useChatSubmission({
  activeThreadIdRef,
  selectionGenerationRef,
  pollControllerRef,
  pendingSubmissionRef,
  messages,
  threads,
  phase,
  threadStatus,
  postAnswerAction,
  createThread,
  updateThread,
  router,
  chatPath,
  selectThread,
  isCurrentSelection,
  applyThreadDetail,
  upsertThread,
  setMessages,
  setPhase,
  setThreadStatus,
  setQueryError,
  setInput,
  setPendingFollowUp,
  setPostAnswerAction,
}: UseChatSubmissionOptions) {
  const submitContent = useCallback(
    (
      rawContent: string,
      kind: PendingChatSubmission["kind"],
      followUp?: ActiveChatFollowUp,
    ) => {
      if (phase === "querying" || phase === "analyzing") return;
      const content = rawContent.trim();
      if (!content) return;
      const statusBeforeSubmit = threadStatus;
      const action =
        statusBeforeSubmit === "answered"
          ? postAnswerAction ?? undefined
          : undefined;
      if (statusBeforeSubmit === "answered" && action === undefined) {
        setQueryError("Choose how to use the next message before sending it.");
        return;
      }

      void (async () => {
        let threadId = activeThreadIdRef.current;
        let currentThread = threads.find((thread) => thread.id === threadId);
        if (!threadId) {
          try {
            const created = await createThread();
            router.push(chatPath(created.id, "chat"));
            await selectThread(created.id);
            threadId = created.id;
            currentThread = created;
          } catch (error) {
            setQueryError(getApiErrorMessage(error, "A chat could not be created."));
            setPhase("error");
            return;
          }
        }
        if (kind === "followup" && !followUp) return;
        const generation = selectionGenerationRef.current;
        const controller = pollControllerRef.current;
        if (!controller || !isCurrentSelection(threadId, generation)) return;
        const existingMessages = messages;
        const pending = pendingSubmissionRef.current;
        const samePending =
          pending?.threadId === threadId &&
          pending.content === content &&
          pending.action === action;
        const idempotencyKey = samePending
          ? pending.key
          : window.crypto.randomUUID();
        const lastKnownMessageOrdinal = samePending
          ? pending.lastKnownMessageOrdinal
          : existingMessages.reduce(
              (latestOrdinal, message) =>
                Math.max(latestOrdinal, message.ordinal),
              0,
            );
        pendingSubmissionRef.current = {
          threadId,
          content,
          key: idempotencyKey,
          kind,
          action,
          lastKnownMessageOrdinal,
        };
        if (kind === "followup" && followUp) {
          setPendingFollowUp({ threadId, followUp });
        }
        setPhase("querying");
        setThreadStatus("processing");
        setQueryError(null);
        let requestAccepted = false;
        try {
          const accepted = await createChatMessage(
            threadId,
            content,
            idempotencyKey,
            controller.signal,
            action,
          );
          if (!isCurrentSelection(threadId, generation)) return;
          requestAccepted = true;
          const pendingAfterAccept = pendingSubmissionRef.current;
          if (
            pendingAfterAccept?.threadId === threadId &&
            pendingAfterAccept.key === idempotencyKey
          ) {
            pendingSubmissionRef.current = {
              ...pendingAfterAccept,
              requestOrdinal: accepted.message.ordinal,
            };
          }
          setMessages((current) => {
            if (current.some((message) => message.id === accepted.message.id)) {
              return current;
            }
            return [...current, accepted.message].sort(
              (left, right) => left.ordinal - right.ordinal,
            );
          });
          if (currentThread) upsertThread({ ...currentThread, status: "processing" });
          if (
            kind === "message" &&
            (currentThread?.title === "New chat" || currentThread?.title === "New case") &&
            existingMessages.length === 0
          ) {
            void updateThread({
              threadId,
              title: content.length <= 60 ? content : `${content.slice(0, 57).trimEnd()}...`,
            })
              .then((updated) => {
                if (isCurrentSelection(threadId, generation)) upsertThread(updated);
              })
              .catch(() => undefined);
          }
          const completedDetail = await pollChatRunUntilCompleted({
            threadId,
            runId: accepted.run.id,
            generation,
            signal: controller.signal,
            isCurrentSelection,
            applyThreadDetail,
          });
          if (
            completedDetail &&
            hasCompletedAssistantOutput(completedDetail, accepted.message.ordinal)
          ) {
            pendingSubmissionRef.current = null;
            setPendingFollowUp(null);
            setInput("");
            setPostAnswerAction(null);
          } else if (completedDetail && isCurrentSelection(threadId, generation)) {
            setQueryError(
              "The completed run did not persist an assistant response. Retry the saved answer.",
            );
          }
        } catch (error) {
          if (
            isChatRequestCanceled(controller.signal, error) ||
            !isCurrentSelection(threadId, generation)
          ) {
            return;
          }
          if (kind === "followup") {
            setThreadStatus("awaiting_followup");
            setPhase("awaiting_followup");
          } else {
            setThreadStatus(statusBeforeSubmit);
            setPhase("error");
          }
          setQueryError(
            getApiErrorMessage(
              error,
              requestAccepted
                ? "The run status could not be confirmed. Retry the saved message."
                : "The message could not be submitted.",
            ),
          );
        }
      })();
    },
    [
      activeThreadIdRef,
      applyThreadDetail,
      chatPath,
      createThread,
      isCurrentSelection,
      messages,
      pendingSubmissionRef,
      phase,
      pollControllerRef,
      postAnswerAction,
      router,
      selectThread,
      selectionGenerationRef,
      setInput,
      setMessages,
      setPendingFollowUp,
      setPhase,
      setPostAnswerAction,
      setQueryError,
      setThreadStatus,
      threadStatus,
      threads,
      updateThread,
      upsertThread,
    ],
  );

  return { submitContent };
}
