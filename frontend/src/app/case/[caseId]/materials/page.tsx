"use client";

import { useParams, useRouter } from "next/navigation";
import { useState, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { CaseMaterialsView } from "@/components/materials/CaseMaterialsView";
import {
  useCaseDocuments,
  useCaseEvidence,
  caseQueryKeys,
} from "@/hooks/useCaseQueries";
import { uploadCaseDocument, admitCaseDocument } from "@/lib/api";
import { casePath } from "@/features/chat/routing/workspaceRoutes";

export default function MaterialsPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const caseId = params?.caseId as string;

  const documentsQuery = useCaseDocuments(caseId ?? null);
  const evidenceQuery = useCaseEvidence(caseId ?? null);

  const [isUploading, setIsUploading] = useState(false);
  const [admittingExtractionId, setAdmittingExtractionId] = useState<string | null>(null);

  const handleUploadDocument = useCallback(
    async (file: File) => {
      if (!caseId || isUploading) return;
      setIsUploading(true);
      try {
        await uploadCaseDocument(caseId, file);
        await queryClient.invalidateQueries({ queryKey: caseQueryKeys.documents(caseId) });
      } finally {
        setIsUploading(false);
      }
    },
    [caseId, isUploading, queryClient],
  );

  const handleAdmitExtraction = useCallback(
    async (documentId: string, extractionId: string) => {
      if (!caseId || admittingExtractionId !== null) return;
      setAdmittingExtractionId(extractionId);
      try {
        await admitCaseDocument(caseId, documentId, extractionId);
        await Promise.all([
          queryClient.invalidateQueries({ queryKey: caseQueryKeys.documents(caseId) }),
          queryClient.invalidateQueries({ queryKey: caseQueryKeys.evidence(caseId) }),
        ]);
      } finally {
        setAdmittingExtractionId(null);
      }
    },
    [caseId, admittingExtractionId, queryClient],
  );

  return (
    <CaseMaterialsView
      caseId={caseId}
      documents={documentsQuery.data ?? []}
      evidence={evidenceQuery.data ?? []}
      isUploading={isUploading}
      admittingExtractionId={admittingExtractionId}
      onUploadDocument={(file) => void handleUploadDocument(file)}
      onAdmitExtraction={(docId, extId) => void handleAdmitExtraction(docId, extId)}
      onOpenIntake={() => router.push(casePath(caseId, "intake"))}
    />
  );
}
