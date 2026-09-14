"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef } from "react";
import { useCases, useCaseMutations } from "@/hooks/useCaseQueries";
import { casePath } from "@/features/chat/routing/workspaceRoutes";

export default function CaseRootPage() {
  const router = useRouter();
  const casesQuery = useCases();
  const { createMutation } = useCaseMutations();
  const bootstrapDoneRef = useRef(false);

  useEffect(() => {
    if (casesQuery.isLoading || bootstrapDoneRef.current) return;

    const cases = casesQuery.data ?? [];
    if (cases[0]) {
      bootstrapDoneRef.current = true;
      router.replace(casePath(cases[0].id, "overview"));
    } else if (!createMutation.isPending) {
      bootstrapDoneRef.current = true;
      void createMutation.mutateAsync().then((newCase) => {
        router.replace(casePath(newCase.id, "intake"));
      });
    }
  }, [casesQuery.data, casesQuery.isLoading, createMutation, router]);

  return null;
}
