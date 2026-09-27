"use client";

import { useCallback, useState } from "react";
import { addCaseSource } from "@/lib/api";
import { refreshAfterSourceChange, useUploadCaseDocument } from "@/features/sources/queries";
import { useQueryClient } from "@tanstack/react-query";

interface UseCaseSourceActionsOptions {
  caseId: string | null;
}

export function useCaseSourceActions({ caseId }: UseCaseSourceActionsOptions) {
  const queryClient = useQueryClient();
  const uploadMutation = useUploadCaseDocument(caseId);
  const [actionError, setActionError] = useState<unknown>(null);
  const [isAddingNarrative, setIsAddingNarrative] = useState(false);

  const uploadDocument = useCallback(
    async (file: File) => {
      if (!caseId || uploadMutation.isPending) return;
      setActionError(null);
      try {
        await uploadMutation.mutateAsync(file);
      } catch (error) {
        setActionError(error);
      }
    },
    [caseId, uploadMutation],
  );

  const addNarrative = useCallback(
    async ({ text }: { text: string }) => {
      if (!caseId || isAddingNarrative) return false;
      setActionError(null);
      setIsAddingNarrative(true);
      try {
        await addCaseSource(caseId, {
          exact_text: text,
          source_kind: "narrative",
          provenance_json: { interface: "case_sources" },
          source_metadata_json: { interface: "case_sources" },
        });
        void refreshAfterSourceChange(queryClient, caseId);
        return true;
      } catch (error) {
        setActionError(error);
        return false;
      } finally {
        setIsAddingNarrative(false);
      }
    },
    [caseId, isAddingNarrative, queryClient],
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
