"use client";

import { useCallback, useState, type Dispatch, type SetStateAction } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  admitCaseDocument,
  admitCaseEvidence,
  getApiErrorMessage,
  getCase,
  startCaseAnalysis,
  uploadCaseDocument,
  type CaseIntakeSubmission,
  type CaseRead,
} from "@/lib/api";
import { caseQueryKeys } from "./useCaseQueries";
import { useCaseAnalysisSubmission } from "./useCaseAnalysisSubmission";
import { casePath } from "@/features/chat/routing/workspaceRoutes";
import type { WorkspaceView } from "@/components/common/types";
import type { CaseChatSession } from "@/features/chat/workspace/use-case-chat-selection";

interface UseCaseWorkspaceActionsOptions {
  activeCaseId: string | null;
  activeCase: CaseRead | null;
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
  activeCase,
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
  const [admittingExtractionId, setAdmittingExtractionId] = useState<string | null>(null);
  const [pendingSubmission, setPendingSubmission] = useCaseAnalysisSubmission(activeCaseId);

  const invalidateCaseData = useCallback(async (caseId: string) => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: caseQueryKeys.cases() }),
      queryClient.invalidateQueries({ queryKey: caseQueryKeys.documents(caseId) }),
      queryClient.invalidateQueries({ queryKey: caseQueryKeys.evidence(caseId) }),
      queryClient.invalidateQueries({ queryKey: caseQueryKeys.analysis(caseId) }),
      queryClient.invalidateQueries({ queryKey: caseQueryKeys.clarifications(caseId) }),
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
  }, [activeCase, activeCaseId, isChatOpen, session, setIsChatOpen, upsertCase]);

  const uploadDocument = useCallback(async (file: File) => {
    if (!activeCaseId || isUploadingDocument) return;
    setActionError(null);
    setIsUploadingDocument(true);
    try {
      await uploadCaseDocument(activeCaseId, file);
      await queryClient.invalidateQueries({ queryKey: caseQueryKeys.documents(activeCaseId) });
    } catch (error) {
      setActionError(getApiErrorMessage(error, "The document could not be saved."));
    } finally {
      setIsUploadingDocument(false);
    }
  }, [activeCaseId, isUploadingDocument, queryClient]);

  const admitExtraction = useCallback(async (documentId: string, extractionId: string) => {
    if (!activeCaseId || admittingExtractionId !== null) return;
    setActionError(null);
    setAdmittingExtractionId(extractionId);
    try {
      await admitCaseDocument(activeCaseId, documentId, extractionId);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: caseQueryKeys.documents(activeCaseId) }),
        queryClient.invalidateQueries({ queryKey: caseQueryKeys.evidence(activeCaseId) }),
      ]);
    } catch (error) {
      setActionError(getApiErrorMessage(error, "The reviewed document text could not be admitted."));
    } finally {
      setAdmittingExtractionId(null);
    }
  }, [activeCaseId, admittingExtractionId, queryClient]);

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
        admissionCompleted: false,
      };
    setPendingSubmission(submission);
    try {
      let currentCase = await getCase(activeCaseId);
      if (normalizedTitle && normalizedTitle !== currentCase.title) {
        currentCase = await updateCase({ caseId: activeCaseId, title: normalizedTitle });
      }
      if (normalizedDescription && !submission.admissionCompleted) {
        await admitCaseEvidence(activeCaseId, {
          exact_text: normalizedDescription,
          source_kind: "narrative",
          provenance_json: { interface: "case_intake" },
          source_metadata_json: { interface: "case_intake" },
        });
        submission = { ...submission, admissionCompleted: true };
        setPendingSubmission(submission);
        currentCase = await getCase(activeCaseId);
      }
      if (!submission.admissionCompleted || submission.expectedEvidenceRevision === null) {
        submission = {
          ...submission,
          admissionCompleted: true,
          expectedEvidenceRevision: requiredEvidenceRevision(currentCase),
        };
        setPendingSubmission(submission);
      }
      const accepted = await startCaseAnalysis(activeCaseId, {
        idempotency_key: submission.idempotencyKey,
        response_language: "english",
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
    admittingExtractionId,
    toggleChat,
    uploadDocument,
    admitExtraction,
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
