"use client";

import { useParams, useRouter } from "next/navigation";
import { TechnicalContextView } from "@/components/technical-context/TechnicalContextView";
import { useCaseAnalysis, useCaseSources } from "@/hooks/useCaseQueries";
import { casePath } from "@/lib/workspaceRoutes";

export default function TechnicalContextPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params?.caseId as string;

  const analysisQuery = useCaseAnalysis(caseId ?? null);
  const sourcesQuery = useCaseSources(caseId ?? null);

  return (
    <TechnicalContextView
      analysisResult={analysisQuery.data ?? null}
      sources={sourcesQuery.data ?? null}
      onOpenSources={() => router.push(casePath(caseId, "sources"))}
      onNavigateToSource={() => router.push(casePath(caseId, "sources"))}
    />
  );
}
