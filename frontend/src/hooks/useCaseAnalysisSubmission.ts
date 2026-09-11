"use client";

import { useEffect, useRef, useState } from "react";
import { readAccountValue, writeAccountValue } from "@/lib/account-storage";

export interface PendingCaseAnalysisSubmission {
  inputFingerprint: string;
  idempotencyKey: string;
  expectedEvidenceRevision: number | null;
  admissionCompleted: boolean;
}

export function useCaseAnalysisSubmission(caseId: string | null) {
  const storageKey = `case-analysis-submission:${caseId ?? "none"}`;
  const loadedKey = useRef(storageKey);
  const [value, setValue] = useState<PendingCaseAnalysisSubmission | null>(() => readSubmission(storageKey));
  useEffect(() => {
    if (loadedKey.current !== storageKey) {
      loadedKey.current = storageKey;
      setValue(readSubmission(storageKey));
      return;
    }
    writeAccountValue(storageKey, JSON.stringify(value));
  }, [storageKey, value]);
  return [value, setValue] as const;
}

function readSubmission(storageKey: string): PendingCaseAnalysisSubmission | null {
  const saved = readAccountValue(storageKey);
  return saved === null ? null : JSON.parse(saved) as PendingCaseAnalysisSubmission;
}
