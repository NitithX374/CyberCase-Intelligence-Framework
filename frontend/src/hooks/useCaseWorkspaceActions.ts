"use client";

import { useCallback, useEffect, useRef, useState, type Dispatch, type SetStateAction } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  addCaseEvidence,
  detectResponseLanguage,
  getApiErrorMessage,
  getCase,
  startCaseAnalysis,
  uploadCaseDocument,
  type CaseIntakeSubmission,
  type CaseRead,
} from "@/lib/api";
import { readAccountValue, writeAccountValue } from "@/lib/account-storage";
import { caseQueryKeys } from "./useCaseQueries";
import { casePath } from "@/features/chat/routing/workspaceRoutes";
import type { WorkspaceView } from "@/components/common/types";
import type { CaseChatSession } from "@/features/chat/workspace/use-case-chat-selection";

interface UseCaseWorkspaceActionsOptions {
  activeCaseId: string | null;
  isChatOpen?: boolean;
  setIsChatOpen?: Dispatch<SetStateAction<boolean>>;
  session?: CaseChatSession;
  upsertCase: (caseRecord: CaseRead) => void;
  updateCase: (input: { caseId: string; title: string }) => Promise<CaseRead>;
  router: { push(path: string): void };
  setActiveView?: Dispatch<SetStateAction<WorkspaceView>>;
}

export function useCaseWorkspaceActions({
  activeCaseId,
  isChatOpen = false,
  setIsChatOpen,
  session,
  upsertCase,
  updateCase,
  router,
  setActiveView,
}: UseCaseWorkspaceActionsOptions) {
  const queryClient = useQueryClient();
  const [actionError, setActionError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isUploadingDocument, setIsUploadingDocument] = useState(false);
  const [pendingSubmission, setPendingSubmission] = useCaseAnalysisSubmission(activeCaseId);

  const invalidateCaseData = useCallback(async (caseId: string) => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: caseQueryKeys.cases() }),
      queryClient.invalidateQueries({ queryKey: caseQueryKeys.documents(caseId) }),
      queryClient.invalidateQueries({ queryKey: caseQueryKeys.evidence(caseId) }),
      queryClient.invalidateQueries({ queryKey: caseQueryKeys.analysis(caseId) }),
      queryClient.invalidateQueries({ queryKey: caseQueryKeys.followups(caseId) }),
    ]);
  }, [queryClient]);

  const toggleChat = useCallback(async () => {
    if (!setIsChatOpen) return;
    if (isChatOpen) {
      setIsChatOpen(false);
      session?.clearSelection();
      return;
    }
    setActionError(null);
    setIsChatOpen(true);
    if (!activeCaseId) return;
    try {
      await session?.selectCaseChat(activeCaseId);
    } catch (error) {
      setIsChatOpen(false);
      setActionError(getApiErrorMessage(error, "The Case Chat could not be opened."));
    }
  }, [activeCaseId, isChatOpen, session, setIsChatOpen]);

  const uploadDocument = useCallback(async (file: File) => {
    if (!activeCaseId || isUploadingDocument) return;
    setActionError(null);
    setIsUploadingDocument(true);
    try {
      await uploadCaseDocument(activeCaseId, file);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: caseQueryKeys.documents(activeCaseId) }),
        queryClient.invalidateQueries({ queryKey: caseQueryKeys.evidence(activeCaseId) }),
      ]);
    } catch (error) {
      setActionError(getApiErrorMessage(error, "The document could not be saved."));
    } finally {
      setIsUploadingDocument(false);
    }
  }, [activeCaseId, isUploadingDocument, queryClient]);

  const submitCase = useCallback(async ({ title, description }: CaseIntakeSubmission) => {
    if (!activeCaseId || isSubmitting) return;
    setActionError(null);
    setIsSubmitting(true);
    const normalizedTitle = title?.trim() || undefined;
    const normalizedDescription = description.trim();
    const inputFingerprint = JSON.stringify({
      title: normalizedTitle ?? null,
      description: normalizedDescription,
    });
    let submission = pendingSubmission?.inputFingerprint === inputFingerprint
      ? pendingSubmission
      : {
        inputFingerprint,
        idempotencyKey: createIdempotencyKey(),
        expectedEvidenceRevision: null,
        evidenceAdded: false,
      };
    setPendingSubmission(submission);
    try {
      let currentCase = await getCase(activeCaseId);
      if (normalizedTitle && normalizedTitle !== currentCase.title) {
        currentCase = await updateCase({ caseId: activeCaseId, title: normalizedTitle });
      }
      if (normalizedDescription && !submission.evidenceAdded) {
        await addCaseEvidence(activeCaseId, {
          exact_text: normalizedDescription,
          source_kind: "narrative",
          provenance_json: { interface: "case_intake" },
          source_metadata_json: { interface: "case_intake" },
        });
        submission = { ...submission, evidenceAdded: true };
        setPendingSubmission(submission);
        currentCase = await getCase(activeCaseId);
      }
      if (!submission.evidenceAdded || submission.expectedEvidenceRevision === null) {
        submission = {
          ...submission,
          evidenceAdded: true,
          expectedEvidenceRevision: requiredEvidenceRevision(currentCase),
        };
        setPendingSubmission(submission);
      }
      const accepted = await startCaseAnalysis(activeCaseId, {
        idempotency_key: submission.idempotencyKey,
        response_language: detectResponseLanguage(normalizedDescription),
        expected_evidence_revision: submission.expectedEvidenceRevision,
      });
      setPendingSubmission(null);
      upsertCase({
        ...currentCase,
        status: "processing",
        active_run_id: accepted.run.id,
        latest_run_id: accepted.run.id,
        processing_status: "queued",
      });
      queryClient.setQueryData(caseQueryKeys.run(activeCaseId, accepted.run.id), accepted.run);
      await invalidateCaseData(activeCaseId);
      if (setActiveView) setActiveView("overview");
      router.push(casePath(activeCaseId, "overview"));
    } catch (error) {
      setActionError(getApiErrorMessage(error, "The Case analysis could not be started."));
    } finally {
      setIsSubmitting(false);
    }
  }, [activeCaseId, invalidateCaseData, isSubmitting, pendingSubmission, queryClient, router, setActiveView, setPendingSubmission, updateCase, upsertCase]);

  return {
    actionError,
    clearActionError: () => setActionError(null),
    isSubmitting,
    isUploadingDocument,
    toggleChat,
    uploadDocument,
    submitCase,
  };
}

function requiredEvidenceRevision(caseRecord: CaseRead): number {
  if (typeof caseRecord.evidence_revision !== "number") {
    throw new Error("The Case evidence revision is unavailable.");
  }
  return caseRecord.evidence_revision;
}

function createIdempotencyKey(): string {
  if (typeof globalThis.crypto?.randomUUID !== "function") throw new Error("The browser does not provide a Case analysis idempotency key generator.");
  return globalThis.crypto.randomUUID();
}

interface PendingCaseAnalysisSubmission {
  inputFingerprint: string;
  idempotencyKey: string;
  expectedEvidenceRevision: number | null;
  evidenceAdded: boolean;
}

function useCaseAnalysisSubmission(caseId: string | null) {
  const storageKey = `case-analysis-submission:${caseId ?? "none"}`;
  const loadedKey = useRef(storageKey);
  const [value, setValue] = useState<PendingCaseAnalysisSubmission | null>(() => readSubmission(storageKey));

  useEffect(() => {
    if (loadedKey.current !== storageKey) {
      loadedKey.current = storageKey;
      setValue(readSubmission(storageKey));
      return;
    }
    writeAccountValue(storageKey, JSON.stringify(value));
  }, [storageKey, value]);

  return [value, setValue] as const;
}

function readSubmission(storageKey: string): PendingCaseAnalysisSubmission | null {
  const saved = readAccountValue(storageKey);
  return saved === null ? null : JSON.parse(saved) as PendingCaseAnalysisSubmission;
}
