"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect } from "react";
import { analysisPath } from "@/lib/casePaths";

export default function CaseAnalysisDetailsRedirectPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params?.caseId as string;

  useEffect(() => {
    if (caseId) {
      router.replace(`${analysisPath(caseId, "technical")}${window.location.hash}`);
    }
  }, [caseId, router]);

  return null;
}
