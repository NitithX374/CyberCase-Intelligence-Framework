"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect } from "react";
import { casePath } from "@/lib/casePaths";

export default function CaseLegalPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params?.caseId as string;

  useEffect(() => {
    if (caseId) {
      router.replace(`${casePath(caseId, "analysis")}#section-references`);
    }
  }, [caseId, router]);

  return null;
}
