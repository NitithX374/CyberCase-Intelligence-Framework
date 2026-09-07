"use client";

import { useCallback } from "react";
import type { ChatThreadRead } from "@/lib/api";
import type { WorkspaceRouteView } from "@/components/common/types";
import { chatPath } from "../routing/chat-route";
import type { ChatSession } from "./use-chat-thread-selection";

interface UseChatThreadDeletionOptions {
  session: ChatSession;
  deleteCandidate: ChatThreadRead | null;
  deletingThreadId: string | null;
  activeView: WorkspaceRouteView;
  threads: ChatThreadRead[];
  deleteThread: (threadId: string) => Promise<void>;
  router: { replace(path: string): void };
  setDeleteCandidate: React.Dispatch<React.SetStateAction<ChatThreadRead | null>>;
}

export function useChatThreadDeletion({
  session, deleteCandidate, deletingThreadId, activeView, threads,
  deleteThread, router, setDeleteCandidate,
}: UseChatThreadDeletionOptions) {
  const cancelDelete = useCallback(() => {
    if (deletingThreadId === null) setDeleteCandidate(null);
  }, [deletingThreadId, setDeleteCandidate]);

  const confirmDelete = useCallback(async () => {
    const thread = deleteCandidate;
    if (!thread || deletingThreadId !== null) return;
    const deletingActiveThread = session.suspendThread(thread.id);
    try {
      await deleteThread(thread.id);
    } catch {
      session.restoreThread(thread.id);
      setDeleteCandidate(null);
      if (deletingActiveThread && session.getActiveThreadId() === null) {
        await session.selectThread(thread.id);
      }
      return;
    }
    session.removeThread(thread.id);
    setDeleteCandidate(null);
    if (!deletingActiveThread || session.getActiveThreadId() !== null) return;
    session.clearSelection();
    const remaining = threads.filter((item) => item.id !== thread.id);
    if (remaining[0]) {
      router.replace(chatPath(remaining[0].id, activeView));
      await session.selectThread(remaining[0].id);
    } else {
      router.replace("/chat");
    }
  }, [activeView, deleteCandidate, deleteThread, deletingThreadId, router, session, setDeleteCandidate, threads]);

  return { cancelDelete, confirmDelete };
}
