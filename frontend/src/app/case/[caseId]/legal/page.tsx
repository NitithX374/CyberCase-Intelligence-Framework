"use client";

import { useParams, useRouter } from "next/navigation";
import { LegalReferenceView } from "@/components/legal/LegalReferenceView";
import { useCaseAnalysis } from "@/hooks/useCaseQueries";
import { casePath } from "@/lib/workspaceRoutes";

/**
 * The Thai provisions the RAG service returned with the analysis.
 *
 * A page of its own rather than a section of Analysis, so that reaching them
 * is a deliberate step that passes the notice first.
 */
export default function CaseLegalPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = (params?.caseId as string) ?? null;
  const analysisQuery = useCaseAnalysis(caseId);

  return (
    <LegalReferenceView
      analysisResult={analysisQuery.data ?? null}
      isLoading={analysisQuery.isLoading}
      isError={analysisQuery.isError}
      onDecline={() => {
        if (caseId) router.push(casePath(caseId, "analysis"));
      }}
    />
  );
}
