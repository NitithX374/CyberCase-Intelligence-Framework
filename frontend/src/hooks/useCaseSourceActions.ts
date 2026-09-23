"use client";

import { useCallback, useState } from "react";
import { addCaseSource, getApiErrorMessage } from "@/lib/api";
import { caseQueryKeys, useCaseMutations, useUploadCaseDocument } from "./useCaseQueries";
import { useQueryClient } from "@tanstack/react-query";

interface UseCaseSourceActionsOptions {
  caseId: string | null;
}

/**
 * Adding case material from the sources page. Analyzing it is the workspace's
 * `runAnalysis`, the same one the Analysis page uses.
 */
export function useCaseSourceActions({ caseId }: UseCaseSourceActionsOptions) {
  const queryClient = useQueryClient();
  const { upsertCase, updateMutation } = useCaseMutations();
  const uploadMutation = useUploadCaseDocument(caseId);
  const [actionError, setActionError] = useState<string | null>(null);
  const [isAddingNarrative, setIsAddingNarrative] = useState(false);

  const uploadDocument = useCallback(
    async (file: File) => {
      if (!caseId || uploadMutation.isPending) return;
      setActionError(null);
      try {
        await uploadMutation.mutateAsync(file);
      } catch (error) {
        setActionError(getApiErrorMessage(error, "The document could not be saved."));
      }
    },
    [caseId, uploadMutation],
  );

  const addNarrative = useCallback(
    async ({ title, text }: { title?: string; text: string }) => {
      if (!caseId || isAddingNarrative) return false;
      setActionError(null);
      setIsAddingNarrative(true);
      try {
        if (title) upsertCase(await updateMutation.mutateAsync({ caseId, title }));
        await addCaseSource(caseId, {
          exact_text: text,
          source_kind: "narrative",
          provenance_json: { interface: "case_sources" },
          source_metadata_json: { interface: "case_sources" },
        });
        void Promise.all([
          queryClient.invalidateQueries({ queryKey: caseQueryKeys.sources(caseId) }),
          queryClient.invalidateQueries({ queryKey: caseQueryKeys.case(caseId), exact: true }),
        ]);
        return true;
      } catch (error) {
        setActionError(getApiErrorMessage(error, "The case narrative could not be saved."));
        return false;
      } finally {
        setIsAddingNarrative(false);
      }
    },
    [caseId, isAddingNarrative, queryClient, updateMutation, upsertCase],
  );

  return {
    actionError,
    clearActionError: () => setActionError(null),
    isUploadingDocument: uploadMutation.isPending,
    uploadingFilename: uploadMutation.isPending ? (uploadMutation.variables?.name ?? null) : null,
    isAddingNarrative,
    uploadDocument,
    addNarrative,
  };
}
