"use client";

import { useParams, useRouter } from "next/navigation";
import { useState, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { CaseMaterialsView } from "@/components/materials/CaseMaterialsView";
import {
  useCaseDocuments,
  caseQueryKeys,
} from "@/hooks/useCaseQueries";
import { uploadCaseDocument } from "@/lib/api";
import { casePath } from "@/features/chat/routing/workspaceRoutes";

export default function MaterialsPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const caseId = params?.caseId as string;

  const documentsQuery = useCaseDocuments(caseId ?? null);

  const [isUploading, setIsUploading] = useState(false);

  const handleUploadDocument = useCallback(
    async (file: File) => {
      if (!caseId || isUploading) return;
      setIsUploading(true);
      try {
        await uploadCaseDocument(caseId, file);
        await Promise.all([
          queryClient.invalidateQueries({ queryKey: caseQueryKeys.documents(caseId) }),
          queryClient.invalidateQueries({ queryKey: caseQueryKeys.evidence(caseId) }),
        ]);
      } finally {
        setIsUploading(false);
      }
    },
    [caseId, isUploading, queryClient],
  );

  return (
    <CaseMaterialsView
      caseId={caseId}
      documents={documentsQuery.data ?? []}
      isUploading={isUploading}
      onUploadDocument={(file) => void handleUploadDocument(file)}
      onOpenIntake={() => router.push(casePath(caseId, "intake"))}
    />
  );
}
