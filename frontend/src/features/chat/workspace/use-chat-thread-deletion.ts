"use client";

import { useCallback } from "react";
import type { CaseRead } from "@/lib/api";
import type { WorkspaceRouteView } from "@/components/common/types";
import { casePath } from "../routing/workspaceRoutes";
import type { ChatSession } from "./use-chat-thread-selection";

interface UseChatThreadDeletionOptions {
  session: ChatSession;
  deleteCandidate: CaseRead | null;
  deletingCaseId: string | null;
  activeView: WorkspaceRouteView;
  activeCaseId?: string | null;
  isChatOpen?: boolean;
  cases: CaseRead[];
  deleteCase: (caseId: string) => Promise<void>;
  router: { replace(path: string): void };
  setDeleteCandidate: React.Dispatch<React.SetStateAction<CaseRead | null>>;
}

export function useChatThreadDeletion({
  session, deleteCandidate, deletingCaseId, activeView, cases,
  activeCaseId = null, isChatOpen = true, deleteCase, router, setDeleteCandidate,
}: UseChatThreadDeletionOptions) {
  const cancelDelete = useCallback(() => {
    if (deletingCaseId === null) setDeleteCandidate(null);
  }, [deletingCaseId, setDeleteCandidate]);

  const confirmDelete = useCallback(async () => {
    const caseRecord = deleteCandidate;
    if (!caseRecord || deletingCaseId !== null) return;
    const deletingActiveThread = session.suspendThread(caseRecord.id);
    const deletingActiveCase = deletingActiveThread || activeCaseId === caseRecord.id;
    try {
      await deleteCase(caseRecord.id);
    } catch {
      session.restoreThread(caseRecord.id);
      setDeleteCandidate(null);
      if (deletingActiveThread && session.getActiveThreadId() === null) {
        await session.selectThread(caseRecord.id);
      }
      return;
    }
    session.removeThread(caseRecord.id);
    setDeleteCandidate(null);
    if (!deletingActiveCase || session.getActiveThreadId() !== null) return;
    session.clearSelection();
    const remaining = cases.filter((item) => item.id !== caseRecord.id);
    if (remaining[0]) {
      router.replace(casePath(remaining[0].id, activeView));
      if (isChatOpen && remaining[0].chat_thread_id) await session.selectThread(remaining[0].chat_thread_id);
    } else {
      router.replace("/case");
    }
  }, [activeCaseId, activeView, cases, deleteCandidate, deleteCase, deletingCaseId, isChatOpen, router, session, setDeleteCandidate]);

  return { cancelDelete, confirmDelete };
}
