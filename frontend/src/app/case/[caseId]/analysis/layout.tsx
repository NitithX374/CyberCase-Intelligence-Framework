import type { ReactNode } from "react";
import { AnalysisLayout } from "@/features/analysis/AnalysisLayout";

export default function CaseAnalysisLayout({ children }: { children: ReactNode }) {
  return <AnalysisLayout>{children}</AnalysisLayout>;
}
