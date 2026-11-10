"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect } from "react";
import { analysisPath } from "@/lib/casePaths";

export default function CaseLegalPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params?.caseId as string;

  useEffect(() => {
    if (caseId) {
      router.replace(analysisPath(caseId, "legal"));
    }
  }, [caseId, router]);

  return null;
}
