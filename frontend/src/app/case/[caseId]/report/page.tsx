"use client";

import { useParams, useRouter } from "next/navigation";
import { CaseReportView } from "@/components/report/CaseReportView";
import { useCase, useCaseAnalysis } from "@/hooks/useCaseQueries";
import { casePath } from "@/lib/workspaceRoutes";

export default function ReportPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params?.caseId as string;

  const caseQuery = useCase(caseId ?? null);
  const activeCase = caseQuery.data ?? null;

  const analysisQuery = useCaseAnalysis(caseId ?? null);

  return (
    <CaseReportView
      key={`${caseId}:${analysisQuery.data?.id ?? "empty"}`}
      caseId={caseId}
      caseTitle={activeCase?.title || "New case"}
      analysisResult={analysisQuery.data ?? null}
      onOpenOverview={() =>
        router.push(
          casePath(caseId, activeCase?.latest_analysis_result_id ? "overview" : "sources"),
        )
      }
    />
  );
}
