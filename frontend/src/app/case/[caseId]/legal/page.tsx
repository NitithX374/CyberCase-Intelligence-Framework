"use client";

import { useParams, useRouter } from "next/navigation";
import { LegalReferenceView } from "@/features/legal/LegalReferenceView";
import { useCaseAnalysis } from "@/features/analysis/queries";
import { casePath } from "@/features/workspace/routes";

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
