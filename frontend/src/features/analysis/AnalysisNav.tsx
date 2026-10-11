"use client";

import Link from "next/link";
import { useSelectedLayoutSegment } from "next/navigation";
import { analysisPath, type AnalysisSection } from "@/lib/casePaths";

const sections: Array<{ section?: AnalysisSection; label: string }> = [
  { label: "Summary" },
  { section: "findings", label: "Findings" },
  { section: "details", label: "Details" },
  { section: "questions", label: "Open questions" },
];

export function AnalysisNav({
  caseId,
  findingCount,
  questionCount,
}: {
  caseId: string;
  findingCount: number;
  questionCount: number;
}) {
  const segment = useSelectedLayoutSegment();
  const active = sections.find((item) => item.section === segment)?.section;
  const counts: Partial<Record<AnalysisSection, number>> = {
    findings: findingCount,
    questions: questionCount,
  };

  return (
    <nav aria-label="Analysis sections" className="-mb-px flex items-end gap-6 overflow-x-auto">
      {sections.map((item) => {
        const current = item.section === active;
        const count = item.section ? counts[item.section] : undefined;
        const attention = item.section === "questions" && Boolean(count) && !current;
        return (
          <Link
            key={item.label}
            href={analysisPath(caseId, item.section)}
            aria-current={current ? "page" : undefined}
            className={`inline-flex shrink-0 items-center gap-2 border-b-2 pb-3 text-sm font-semibold transition-colors ${
              current ? "border-ink text-ink" : "border-transparent text-ink-muted hover:text-ink"
            }`}
          >
            {item.label}
            {count !== undefined && (
              <span
                className={`text-[13px] font-medium ${attention ? "text-unresolved" : "text-ink-muted"}`}
              >
                {count}
              </span>
            )}
          </Link>
        );
      })}
    </nav>
  );
}
