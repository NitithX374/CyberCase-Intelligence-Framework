"use client";

import { useParams, useRouter } from "next/navigation";
import { TechnicalContextView } from "@/components/technical/TechnicalContextView";
import { useCaseAnalysis, useCaseEvidence } from "@/hooks/useCaseQueries";
import { casePath } from "@/lib/workspaceRoutes";

export default function TechnicalContextPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params?.caseId as string;

  const analysisQuery = useCaseAnalysis(caseId ?? null);
  const evidenceQuery = useCaseEvidence(caseId ?? null);

  return (
    <TechnicalContextView
      analysisResult={analysisQuery.data ?? null}
      evidenceSources={evidenceQuery.data ?? null}
      onOpenMaterials={() => router.push(casePath(caseId, "materials"))}
      onNavigateToSource={() => router.push(casePath(caseId, "materials"))}
    />
  );
}
