"use client";

import { useCallback, useState } from "react";
import {
  addCaseSource,
  detectResponseLanguage,
  getApiErrorMessage,
  type CaseSourceRead,
} from "@/lib/api";
import {
  caseQueryKeys,
  useCaseMutations,
  useStartCaseAnalysis,
  useUploadCaseDocument,
} from "./useCaseQueries";
import { useQueryClient } from "@tanstack/react-query";
import { casePath } from "@/lib/workspaceRoutes";

interface UseCaseSourceActionsOptions {
  caseId: string | null;
  sources: CaseSourceRead[];
  router: { push(path: string): void };
}

/** Adding case material and running the analysis over it, from the sources page. */
export function useCaseSourceActions({ caseId, sources, router }: UseCaseSourceActionsOptions) {
  const queryClient = useQueryClient();
  const { upsertCase, updateMutation } = useCaseMutations();
  const uploadMutation = useUploadCaseDocument(caseId);
  const analysisMutation = useStartCaseAnalysis(caseId);
  const [actionError, setActionError] = useState<string | null>(null);
  const [isAddingNarrative, setIsAddingNarrative] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

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
        await Promise.all([
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

  const analyze = useCallback(async () => {
    if (!caseId || isAnalyzing) return;
    setActionError(null);
    setIsAnalyzing(true);
    try {
      await analysisMutation.mutateAsync({
        response_language: detectResponseLanguage(
          sources.map((source) => source.exact_text).join("\n"),
        ),
      });
      router.push(casePath(caseId, "overview"));
    } catch (error) {
      setActionError(getApiErrorMessage(error, "The Case analysis could not be started."));
    } finally {
      setIsAnalyzing(false);
    }
  }, [analysisMutation, caseId, isAnalyzing, router, sources]);

  return {
    actionError,
    clearActionError: () => setActionError(null),
    isUploadingDocument: uploadMutation.isPending,
    uploadingFilename: uploadMutation.isPending ? (uploadMutation.variables?.name ?? null) : null,
    isAddingNarrative,
    isAnalyzing,
    uploadDocument,
    addNarrative,
    analyze,
  };
}
