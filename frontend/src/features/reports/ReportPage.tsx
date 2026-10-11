"use client";

import { useParams, useRouter } from "next/navigation";
import { useCaseAnalysis } from "@/features/analysis/queries";
import { EmptyState } from "@/components/EmptyState";
import { casePath } from "@/lib/casePaths";
import { CaseReportView } from "./CaseReportView";

const stateClassName =
  "mx-auto min-h-[420px] w-full max-w-[52rem] justify-center px-5 py-16 sm:px-8";

export function ReportPage() {
  const router = useRouter();
  const { caseId } = useParams<{ caseId: string }>();
  const analysisQuery = useCaseAnalysis(caseId);
  const analysisResult = analysisQuery.data ?? null;

  if (analysisResult) {
    return (
      <div className="pb-16">
        <CaseReportView
          key={`${caseId}:${analysisResult.id}`}
          caseId={caseId}
          analysisResult={analysisResult}
        />
      </div>
    );
  }

  if (analysisQuery.isLoading) {
    return (
      <div
        role="status"
        aria-label="Loading report"
        className="mx-auto w-full max-w-[52rem] px-5 pt-8 sm:px-8"
      >
        <div className="h-[420px] animate-pulse rounded-xl bg-surface-nested" />
      </div>
    );
  }

  if (analysisQuery.isLoadingError) {
    return (
      <EmptyState
        title="The report could not be opened"
        description="A report is made from the saved analysis, which could not be read. Nothing was changed."
        className={stateClassName}
      >
        <button
          type="button"
          onClick={() => void analysisQuery.refetch()}
          className="btn-secondary mt-5"
        >
          Try again
        </button>
      </EmptyState>
    );
  }

  return (
    <EmptyState
      title="No report yet"
      description="A report is made from an analysis. Analyze the case first."
      className={stateClassName}
    >
      <button
        type="button"
        onClick={() => router.push(casePath(caseId, "analysis"))}
        className="btn-primary mt-5"
      >
        Open analysis
      </button>
    </EmptyState>
  );
}
