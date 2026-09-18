"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect } from "react";
import { casePath } from "@/lib/workspaceRoutes";

export default function CaseIndexPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params?.caseId as string;

  useEffect(() => {
    if (caseId) {
      router.replace(casePath(caseId, "materials"));
    }
  }, [caseId, router]);

  return null;
}
