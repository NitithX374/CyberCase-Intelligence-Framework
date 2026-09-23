"use client";

import { useCallback } from "react";
import type { CaseRead } from "@/lib/api";
import type { WorkspaceView } from "@/features/workspace/views";
import { casePath } from "@/features/workspace/routes";

export interface UseCaseDeletionOptions {
  deleteCandidate: CaseRead | null;
  deletingCaseId: string | null;
  activeView: WorkspaceView;
  activeCaseId?: string | null;
  cases: CaseRead[];
  deleteCase: (caseId: string) => Promise<void>;
  router: { replace(path: string): void };
  setDeleteCandidate: React.Dispatch<React.SetStateAction<CaseRead | null>>;
  onDeleted?: (deletedCaseId: string) => void;
}

export function useCaseDeletion({
  deleteCandidate,
  deletingCaseId,
  activeView,
  cases,
  activeCaseId = null,
  deleteCase,
  router,
  setDeleteCandidate,
  onDeleted,
}: UseCaseDeletionOptions) {
  const cancelDelete = useCallback(() => {
    if (deletingCaseId === null) setDeleteCandidate(null);
  }, [deletingCaseId, setDeleteCandidate]);

  const confirmDelete = useCallback(async () => {
    const caseRecord = deleteCandidate;
    if (!caseRecord || deletingCaseId !== null) return;
    const isDeletingActiveCase = activeCaseId === caseRecord.id;
    try {
      await deleteCase(caseRecord.id);
    } catch {
      setDeleteCandidate(null);
      return;
    }
    setDeleteCandidate(null);
    onDeleted?.(caseRecord.id);
    if (!isDeletingActiveCase) return;
    const remaining = cases.filter((item) => item.id !== caseRecord.id);
    if (remaining[0]) {
      router.replace(casePath(remaining[0].id, activeView));
    } else {
      router.replace("/case");
    }
  }, [
    activeCaseId,
    activeView,
    cases,
    deleteCandidate,
    deleteCase,
    deletingCaseId,
    onDeleted,
    router,
    setDeleteCandidate,
  ]);

  return { cancelDelete, confirmDelete };
}
