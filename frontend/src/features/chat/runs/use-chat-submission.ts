"use client";

import { useCallback, useRef } from "react";
import {
  createChatMessage, getApiErrorMessage,
  type CaseNarrativeDocumentSource, type ChatThreadRead,
} from "@/lib/api";
import { hasCompletedAssistantOutput, type ActiveChatFollowUp } from "@/lib/chat-followup";
import { isChatRequestCanceled } from "./chat-polling";
import type { PendingChatSubmission } from "../workspace/chat-workspace-types";
import type { ChatSelection, ChatSession } from "../workspace/use-chat-thread-selection";

interface UseChatSubmissionOptions {
  session: ChatSession;
  threads: ChatThreadRead[];
  createThread: () => Promise<ChatThreadRead>;
  updateThread: (input: { threadId: string; title: string }) => Promise<ChatThreadRead>;
  router: { push(path: string): void };
  chatPath: (threadId: string, view: "chat") => string;
}

export function useChatSubmission({
  session, threads, createThread, updateThread, router, chatPath,
}: UseChatSubmissionOptions) {
  const submissionsRef = useRef(new Set<ChatSelection | null>());
  const submitContent = useCallback((
    rawContent: string,
    kind: PendingChatSubmission["kind"],
    followUp?: ActiveChatFollowUp,
    onAccepted?: () => void,
    documentSources?: CaseNarrativeDocumentSource[],
  ) => {
    if (session.phase === "querying" || session.phase === "analyzing") return;
    const content = rawContent.trim();
    const saved = session.getPendingSubmission();
    const savedRetry = saved?.threadId === session.getActiveThreadId() &&
      saved.content === content && saved.kind === kind ? saved : null;
    if (!content || (kind === "followup" && !followUp && !savedRetry)) return;
    const initialSelection = session.getSelection();
    if (submissionsRef.current.has(initialSelection)) return;
    const statusBeforeSubmit = session.threadStatus;
    const action = savedRetry ? savedRetry.action : statusBeforeSubmit === "answered"
      ? session.postAnswerAction ?? undefined : undefined;
    if (statusBeforeSubmit === "answered" && action === undefined) {
      session.reportError("Choose how to use the next message before sending it.");
      return;
    }
    submissionsRef.current.add(initialSelection);

    void (async () => {
      let selection = initialSelection;
      let requestAccepted = false;
      try {
        let currentThread = threads.find((thread) => thread.id === selection?.threadId);
        if (!selection) {
          const created = await createThread();
          if (session.getSelection() !== initialSelection) return;
          router.push(chatPath(created.id, "chat"));
          await session.selectThread(created.id);
          selection = session.getSelection();
          if (selection?.threadId !== created.id) return;
          currentThread = created;
        }
        if (!selection || !session.isCurrentSelection(selection)) return;
        const threadId = selection.threadId;
        const pending = session.getPendingSubmission();
        const samePending = pending?.threadId === threadId &&
          pending.content === content && pending.action === action && pending.kind === kind &&
          JSON.stringify(pending.documentSources ?? []) === JSON.stringify(documentSources ?? []);
        const submission: PendingChatSubmission = samePending ? pending : {
          threadId, content, key: window.crypto.randomUUID(), kind, action, documentSources,
          lastKnownMessageOrdinal: session.messages.reduce((ordinal, message) => Math.max(ordinal, message.ordinal), 0),
        };
        session.beginSubmission(submission, followUp);
        const accepted = await createChatMessage(
          threadId, content, submission.key, selection.signal, action, documentSources,
        );
        if (!session.isCurrentSelection(selection)) return;
        requestAccepted = true;
        session.acceptSubmission(selection, submission.key, accepted);
        onAccepted?.();

        if (kind === "message" && session.messages.length === 0 &&
          (currentThread?.title === "New chat" || currentThread?.title === "New case")) {
          const requestSelection = selection;
          void updateThread({
            threadId,
            title: content.length <= 60 ? content : `${content.slice(0, 57).trimEnd()}...`,
          }).then((updated) => {
            if (session.isCurrentSelection(requestSelection)) session.upsertThread(updated);
          }).catch((error: unknown) => {
            if (session.isCurrentSelection(requestSelection)) {
              session.reportError(getApiErrorMessage(error, "The chat title could not be updated."));
            }
          });
        }

        const completed = await session.monitorThread(selection, accepted.run.id);
        if (completed && session.isCurrentSelection(selection) &&
          !hasCompletedAssistantOutput(completed, accepted.message.ordinal)) {
          session.reportError("The completed run did not persist an assistant response. Retry the saved answer.");
        }
      } catch (error) {
        if (selection && (isChatRequestCanceled(selection.signal, error) || !session.isCurrentSelection(selection))) return;
        if (!selection && session.getSelection() !== initialSelection) return;
        session.failSubmission(kind, statusBeforeSubmit, getApiErrorMessage(
          error,
          !selection ? "A chat could not be created." : requestAccepted
            ? "The run status could not be confirmed. Retry the saved message."
            : "The message could not be submitted.",
        ));
      } finally {
        submissionsRef.current.delete(initialSelection);
      }
    })();
  }, [chatPath, createThread, router, session, threads, updateThread]);

  return { submitContent };
}
