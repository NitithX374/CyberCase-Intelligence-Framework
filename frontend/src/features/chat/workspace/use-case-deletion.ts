"use client";

import { useCallback } from "react";
import type { CaseRead } from "@/lib/api";
import type { WorkspaceView } from "@/components/common/types";
import { casePath } from "../routing/workspaceRoutes";
import type { CaseChatSession } from "./use-case-chat-selection";

interface UseCaseDeletionOptions {
  session: CaseChatSession;
  deleteCandidate: CaseRead | null;
  deletingCaseId: string | null;
  activeView: WorkspaceView;
  activeCaseId?: string | null;
  isChatOpen?: boolean;
  cases: CaseRead[];
  deleteCase: (caseId: string) => Promise<void>;
  router: { replace(path: string): void };
  setDeleteCandidate: React.Dispatch<React.SetStateAction<CaseRead | null>>;
}

export function useCaseDeletion({
  session, deleteCandidate, deletingCaseId, activeView, cases,
  activeCaseId = null, isChatOpen = true, deleteCase, router, setDeleteCandidate,
}: UseCaseDeletionOptions) {
  const cancelDelete = useCallback(() => {
    if (deletingCaseId === null) setDeleteCandidate(null);
  }, [deletingCaseId, setDeleteCandidate]);

  const confirmDelete = useCallback(async () => {
    const caseRecord = deleteCandidate;
    if (!caseRecord || deletingCaseId !== null) return;
    const deletingActiveChat = session.suspendCaseChat(caseRecord.id);
    const deletingActiveCase = deletingActiveChat || activeCaseId === caseRecord.id;
    try {
      await deleteCase(caseRecord.id);
    } catch {
      session.restoreCaseChat(caseRecord.id);
      setDeleteCandidate(null);
      if (deletingActiveChat && session.getActiveCaseChatId() === null) {
        await session.selectCaseChat(caseRecord.id);
      }
      return;
    }
    session.removeCaseChat(caseRecord.id);
    setDeleteCandidate(null);
    if (!deletingActiveCase || session.getActiveCaseChatId() !== null) return;
    session.clearSelection();
    const remaining = cases.filter((item) => item.id !== caseRecord.id);
    if (remaining[0]) {
      router.replace(casePath(remaining[0].id, activeView));
      if (isChatOpen) await session.selectCaseChat(remaining[0].id);
    } else {
      router.replace("/case");
    }
  }, [activeCaseId, activeView, cases, deleteCandidate, deleteCase, deletingCaseId, isChatOpen, router, session, setDeleteCandidate]);

  return { cancelDelete, confirmDelete };
}
