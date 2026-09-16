"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  addCaseEvidence,
  detectResponseLanguage,
  getApiErrorMessage,
  getCase,
  type CaseIntakeSubmission,
  type CaseRead,
} from "@/lib/api";
import { readAccountValue, writeAccountValue } from "@/lib/account-storage";
import { casePath } from "@/lib/workspaceRoutes";
import { useStartCaseAnalysis, useUploadCaseDocument } from "./useCaseQueries";

interface UseCaseIntakeActionsOptions {
  activeCaseId: string | null;
  upsertCase: (caseRecord: CaseRead) => void;
  updateCase: (input: { caseId: string; title: string }) => Promise<CaseRead>;
  router: { push(path: string): void };
}

export function useCaseIntakeActions({
  activeCaseId,
  upsertCase,
  updateCase,
  router,
}: UseCaseIntakeActionsOptions) {
  const [actionError, setActionError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [pendingSubmission, setPendingSubmission] = useCaseAnalysisSubmission(activeCaseId);

  const uploadMutation = useUploadCaseDocument(activeCaseId);
  const startAnalysisMutation = useStartCaseAnalysis(activeCaseId);

  const uploadDocument = useCallback(async (file: File) => {
    if (!activeCaseId || uploadMutation.isPending) return;
    setActionError(null);
    try {
      await uploadMutation.mutateAsync(file);
    } catch (error) {
      setActionError(getApiErrorMessage(error, "The document could not be saved."));
    }
  }, [activeCaseId, uploadMutation]);

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
      const accepted = await startAnalysisMutation.mutateAsync({
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
      router.push(casePath(activeCaseId, "overview"));
    } catch (error) {
      setActionError(getApiErrorMessage(error, "The Case analysis could not be started."));
    } finally {
      setIsSubmitting(false);
    }
  }, [activeCaseId, isSubmitting, pendingSubmission, router, setPendingSubmission, startAnalysisMutation, updateCase, upsertCase]);

  return {
    actionError,
    clearActionError: () => setActionError(null),
    isSubmitting,
    isUploadingDocument: uploadMutation.isPending,
    uploadingFilename: uploadMutation.isPending ? uploadMutation.variables?.name ?? null : null,
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
