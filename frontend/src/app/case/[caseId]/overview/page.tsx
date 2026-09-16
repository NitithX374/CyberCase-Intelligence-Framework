"use client";

import { useParams } from "next/navigation";
import { CaseOverviewView } from "@/components/overview/CaseOverviewView";

export default function OverviewPage() {
  const params = useParams();
  const caseId = (params?.caseId as string) ?? null;
  return <CaseOverviewView caseId={caseId} />;
}
