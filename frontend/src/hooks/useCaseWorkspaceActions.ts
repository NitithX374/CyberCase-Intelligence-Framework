"use client";

import { useCallback, useRef, useState, type Dispatch, type SetStateAction } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  admitCaseDocument,
  admitCaseEvidence,
  answerCaseClarification as submitCaseClarificationAnswer,
  ensureCaseChat,
  getApiErrorMessage,
  getCase,
  startCaseAnalysis,
  uploadCaseDocument,
  type CaseIntakeSubmission,
  type CaseRead,
} from "@/lib/api";
import { sha256Hex } from "@/lib/sha256";
import { caseQueryKeys } from "./useCaseQueries";
import { useCaseAnalysisSubmission } from "./useCaseAnalysisSubmission";
import { casePath } from "@/features/chat/routing/workspaceRoutes";
import type { WorkspaceRouteView } from "@/components/common/types";
import type { ChatSession } from "@/features/chat/workspace/use-chat-thread-selection";

interface UseCaseWorkspaceActionsOptions {
  activeCaseId: string | null;
  activeCase: CaseRead | null;
  isChatOpen: boolean;
  setIsChatOpen: Dispatch<SetStateAction<boolean>>;
  session: ChatSession;
  upsertCase: (caseRecord: CaseRead) => void;
  updateCase: (input: { caseId: string; title: string }) => Promise<CaseRead>;
  router: { push(path: string): void };
  setActiveView: Dispatch<SetStateAction<WorkspaceRouteView>>;
}

export function useCaseWorkspaceActions({
  activeCaseId,
  activeCase,
  isChatOpen,
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
  const [answeringClarificationId, setAnsweringClarificationId] = useState<string | null>(null);
  const [pendingSubmission, setPendingSubmission] = useCaseAnalysisSubmission(activeCaseId);
  const clarificationKeys = useRef(new Map<string, { answer: string; key: string }>());

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
    if (isChatOpen) {
      setIsChatOpen(false);
      session.clearSelection();
      return;
    }
    setActionError(null);
    setIsChatOpen(true);
    if (!activeCaseId) return;
    try {
      const threadId = activeCase?.chat_thread_id ?? (await ensureCaseChat(activeCaseId)).id;
      if (!activeCase?.chat_thread_id) {
        const current = activeCase ?? await getCase(activeCaseId);
        upsertCase({ ...current, chat_thread_id: threadId });
      }
      await session.selectThread(threadId);
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
      await invalidateCaseData(activeCaseId);
    } catch (error) {
      setActionError(getApiErrorMessage(error, "The document could not be saved."));
    } finally {
      setIsUploadingDocument(false);
    }
  }, [activeCaseId, invalidateCaseData, isUploadingDocument]);

  const admitExtraction = useCallback(async (documentId: string, extractionId: string) => {
    if (!activeCaseId || admittingExtractionId !== null) return;
    setActionError(null);
    setAdmittingExtractionId(extractionId);
    try {
      await admitCaseDocument(activeCaseId, documentId, extractionId);
      await invalidateCaseData(activeCaseId);
    } catch (error) {
      setActionError(getApiErrorMessage(error, "The reviewed document text could not be admitted."));
    } finally {
      setAdmittingExtractionId(null);
    }
  }, [activeCaseId, admittingExtractionId, invalidateCaseData]);

  const answerClarification = useCallback(async (clarificationId: string, answer: string) => {
    if (!activeCaseId || answeringClarificationId !== null || !answer.trim()) return;
    setActionError(null);
    setAnsweringClarificationId(clarificationId);
    const normalizedAnswer = answer.trim();
    const previous = clarificationKeys.current.get(clarificationId);
    const submission = previous?.answer === normalizedAnswer
      ? previous
      : { answer: normalizedAnswer, key: createIdempotencyKey() };
    clarificationKeys.current.set(clarificationId, submission);
    try {
      const currentCase = activeCase ?? await getCase(activeCaseId);
      const accepted = await submitCaseClarificationAnswer(activeCaseId, clarificationId, {
        answer: normalizedAnswer,
        idempotency_key: submission.key,
        response_language: "english",
      });
      clarificationKeys.current.delete(clarificationId);
      upsertCase({
        ...currentCase,
        status: "processing",
        active_run_id: accepted.run.id,
        latest_run_id: accepted.run.id,
        processing_status: "queued",
      });
      queryClient.setQueryData(caseQueryKeys.run(activeCaseId, accepted.run.id), accepted.run);
      await invalidateCaseData(activeCaseId);
    } catch (error) {
      setActionError(getApiErrorMessage(error, "The clarification answer could not be submitted."));
    } finally {
      setAnsweringClarificationId(null);
    }
  }, [activeCase, activeCaseId, answeringClarificationId, invalidateCaseData, queryClient, upsertCase]);

  const submitCase = useCallback(async ({ title, description }: CaseIntakeSubmission) => {
    if (!activeCaseId || isSubmitting) return;
    setActionError(null);
    setIsSubmitting(true);
    const normalizedTitle = title?.trim() || undefined;
    const normalizedDescription = description.trim();
    const inputFingerprint = sha256Hex(JSON.stringify({
      title: normalizedTitle ?? null,
      description: normalizedDescription,
    }));
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
      setActiveView("overview");
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
    answeringClarificationId,
    toggleChat,
    uploadDocument,
    admitExtraction,
    answerClarification,
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
