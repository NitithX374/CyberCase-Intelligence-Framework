"use client";

import { useCallback } from "react";
import type { ChatThreadDetail, ChatThreadRead, ThreadStatus } from "@/lib/api";
import type { RunPhase, WorkspaceRouteView } from "@/components/common/types";
import type { ActiveChatFollowUp } from "@/lib/chat-followup";
import type { PendingChatSubmission } from "./chat-workspace-types";

interface RouterLike {
  replace(path: string): void;
}

interface UseChatThreadDeletionOptions {
  deleteCandidate: ChatThreadRead | null;
  deletingThreadId: string | null;
  activeThreadIdRef: React.MutableRefObject<string | null>;
  pollControllerRef: React.MutableRefObject<AbortController | null>;
  selectionGenerationRef: React.MutableRefObject<number>;
  pendingSubmissionRef: React.MutableRefObject<PendingChatSubmission | null>;
  deletedThreadIdsRef: React.MutableRefObject<Set<string>>;
  activeView: WorkspaceRouteView;
  threads: ChatThreadRead[];
  deleteThread: (threadId: string) => Promise<void>;
  router: RouterLike;
  selectThread: (threadId: string) => Promise<void>;
  setDeleteCandidate: React.Dispatch<React.SetStateAction<ChatThreadRead | null>>;
  setActiveThreadId: React.Dispatch<React.SetStateAction<string | null>>;
  setPendingFollowUp: React.Dispatch<React.SetStateAction<{
    threadId: string;
    followUp: ActiveChatFollowUp;
  } | null>>;
  setPostAnswerAction: React.Dispatch<React.SetStateAction<"ask" | "add_case_info" | null>>;
  setMessages: React.Dispatch<React.SetStateAction<ChatThreadDetail["messages"]>>;
  setInput: React.Dispatch<React.SetStateAction<string>>;
  setThreadStatus: React.Dispatch<React.SetStateAction<ThreadStatus | null>>;
  setQueryError: React.Dispatch<React.SetStateAction<string | null>>;
  setPhase: React.Dispatch<React.SetStateAction<RunPhase>>;
}

export function useChatThreadDeletion({
  deleteCandidate,
  deletingThreadId,
  activeThreadIdRef,
  pollControllerRef,
  selectionGenerationRef,
  pendingSubmissionRef,
  deletedThreadIdsRef,
  activeView,
  threads,
  deleteThread,
  router,
  selectThread,
  setDeleteCandidate,
  setActiveThreadId,
  setPendingFollowUp,
  setPostAnswerAction,
  setMessages,
  setInput,
  setThreadStatus,
  setQueryError,
  setPhase,
}: UseChatThreadDeletionOptions) {
  const cancelDelete = useCallback(() => {
    if (deletingThreadId === null) setDeleteCandidate(null);
  }, [deletingThreadId, setDeleteCandidate]);

  const confirmDelete = useCallback(async () => {
    const thread = deleteCandidate;
    if (!thread || deletingThreadId !== null) return;
    const deletingActiveThread = activeThreadIdRef.current === thread.id;
    deletedThreadIdsRef.current.add(thread.id);
    if (deletingActiveThread) {
      pollControllerRef.current?.abort();
      pollControllerRef.current = null;
      selectionGenerationRef.current += 1;
      activeThreadIdRef.current = null;
      if (pendingSubmissionRef.current?.threadId === thread.id) {
        pendingSubmissionRef.current = null;
        setPendingFollowUp(null);
      }
      setPostAnswerAction(null);
    }
    try {
      await deleteThread(thread.id);
    } catch {
      deletedThreadIdsRef.current.delete(thread.id);
      setDeleteCandidate(null);
      if (deletingActiveThread) await selectThread(thread.id);
      return;
    }
    const remainingThreads = threads.filter((item) => item.id !== thread.id);
    setDeleteCandidate(null);
    if (!deletingActiveThread) return;
    setActiveThreadId(null);
    setMessages([]);
    setInput("");
    setThreadStatus(null);
    setQueryError(null);
    setPhase("idle");
    setPostAnswerAction(null);
    if (remainingThreads[0]) {
      const nextPath = `/chat/${encodeURIComponent(remainingThreads[0].id)}${
        activeView === "chat" ? "" : `/${activeView}`
      }`;
      router.replace(nextPath);
      await selectThread(remainingThreads[0].id);
    } else {
      router.replace("/chat");
    }
  }, [
    activeThreadIdRef,
    activeView,
    deleteCandidate,
    deleteThread,
    deletingThreadId,
    deletedThreadIdsRef,
    pendingSubmissionRef,
    pollControllerRef,
    router,
    selectThread,
    selectionGenerationRef,
    setActiveThreadId,
    setDeleteCandidate,
    setInput,
    setMessages,
    setPendingFollowUp,
    setPhase,
    setPostAnswerAction,
    setQueryError,
    setThreadStatus,
    threads,
  ]);

  return { cancelDelete, confirmDelete };
}
