"use client";

import { useMemo } from "react";
import { useCaseChatMessages } from "@/features/chat/useCaseChat";
import { mergeCaseSourceRows } from "./followupSources";
import { useCaseSources } from "./queries";

/**
 * The case's sources as the reader sees them: what was written or uploaded,
 * followed by the follow-up answers given in the chat.
 *
 * `caseSources` is the first part on its own, for questions only a real
 * source answers, such as whether there is anything to analyze.
 */
export function useCaseSourceRows(caseId: string | null) {
  const sourcesQuery = useCaseSources(caseId);
  const chatQuery = useCaseChatMessages({ caseId });
  const caseSources = useMemo(() => sourcesQuery.data ?? [], [sourcesQuery.data]);
  const rows = useMemo(
    () => mergeCaseSourceRows(caseSources, chatQuery.data?.messages ?? []),
    [caseSources, chatQuery.data?.messages],
  );
  return { caseSources, rows, isLoading: sourcesQuery.isLoading };
}
