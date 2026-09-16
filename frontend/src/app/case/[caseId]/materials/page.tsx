"use client";

import { useParams, useRouter } from "next/navigation";
import { useCallback } from "react";
import { CaseMaterialsView } from "@/components/materials/CaseMaterialsView";
import {
  useCaseDocuments,
  useUploadCaseDocument,
} from "@/hooks/useCaseQueries";
import { casePath } from "@/lib/workspaceRoutes";

export default function MaterialsPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params?.caseId as string;

  const documentsQuery = useCaseDocuments(caseId ?? null);
  const uploadMutation = useUploadCaseDocument(caseId ?? null);

  const handleUploadDocument = useCallback(
    async (file: File) => {
      if (!caseId || uploadMutation.isPending) return;
      try {
        await uploadMutation.mutateAsync(file);
      } catch {
      }
    },
    [caseId, uploadMutation],
  );

  return (
    <CaseMaterialsView
      caseId={caseId}
      documents={documentsQuery.data ?? []}
      isUploading={uploadMutation.isPending}
      onUploadDocument={(file) => void handleUploadDocument(file)}
      onOpenIntake={() => router.push(casePath(caseId, "intake"))}
    />
  );
}
