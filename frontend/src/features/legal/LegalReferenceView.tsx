"use client";

import type { CaseAnalysisResultRead } from "@/lib/api/types";
import { legalLookupSkipped, readLegalReference } from "./legalReference";
import { LegalProvisions } from "./LegalProvisions";
import { LegalState } from "./LegalState";
import { LegalSkeleton } from "./LegalSkeleton";

interface LegalReferenceViewProps {
  analysisResult: CaseAnalysisResultRead | null;
  isLoading?: boolean;
  isError?: boolean;
  onDecline: () => void;
}

export function LegalReferenceView({
  analysisResult,
  isLoading = false,
  isError = false,
  onDecline,
}: LegalReferenceViewProps) {
  if (isLoading) return <LegalSkeleton />;
  if (isError) {
    return (
      <LegalState title="Analysis unavailable" description="The analysis could not be loaded." />
    );
  }
  if (!analysisResult) {
    return (
      <LegalState
        title="Not analyzed yet"
        description="Legal references are looked up when the case is analyzed."
      />
    );
  }

  const reference = readLegalReference(analysisResult);
  if (!reference) {
    return (
      <LegalState
        title="No legal references"
        description={
          legalLookupSkipped(analysisResult)
            ? "The legal lookup runs with the ATT&CK retrieval, and this case was judged not to need it."
            : "This analysis made no legal lookup."
        }
      />
    );
  }
  if (!reference.provisions.length) {
    return (
      <LegalState
        title="No provisions found"
        description={reference.degraded || "The legal service matched no provisions to this case."}
      />
    );
  }
  return <LegalProvisions reference={reference} onDecline={onDecline} />;
}
