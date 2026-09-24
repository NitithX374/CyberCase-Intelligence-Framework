"use client";

import { useMemo } from "react";
import { useCaseChatMessages } from "@/features/chat/useCaseChat";
import { mergeCaseSourceRows } from "./followupSources";
import { useCaseSources } from "./queries";

export function useCaseSourceRows(caseId: string | null) {
  const sourcesQuery = useCaseSources(caseId);
  const chatQuery = useCaseChatMessages({ caseId });
  const caseSources = useMemo(() => sourcesQuery.data ?? [], [sourcesQuery.data]);
  const rows = useMemo(
    () => mergeCaseSourceRows(caseSources, chatQuery.data?.messages ?? []),
    [caseSources, chatQuery.data?.messages],
  );
  return { caseSources, rows, isLoading: sourcesQuery.isLoading || chatQuery.isLoading };
}
