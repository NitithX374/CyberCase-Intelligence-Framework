import type {
  CaseReportRead,
  ReportClaim,
  ReportSection,
  StructuredReport,
} from "./generated/reportTypes";

export type CaseReportClaim = Omit<
  ReportClaim,
  "source_message_ids" | "source_evidence_ids" | "mitre_technique_ids"
> & {
  source_message_ids: string[];
  source_evidence_ids: string[];
  mitre_technique_ids: string[];
};

export type CaseReportSection = Omit<ReportSection, "paragraphs" | "items"> & {
  paragraphs: string[];
  items: string[];
};

export type CaseStructuredReport = Omit<
  StructuredReport,
  "sections" | "claims" | "limitations"
> & {
  sections: CaseReportSection[];
  claims: CaseReportClaim[];
  limitations: string[];
};

export type CaseReport = Omit<CaseReportRead, "report"> & {
  report: CaseStructuredReport | null;
};

export function normalizeCaseReport(report: CaseReportRead): CaseReport {
  return {
    ...report,
    report: report.report
      ? {
          ...report.report,
          sections: report.report.sections.map((section) => ({
            ...section,
            paragraphs: section.paragraphs ?? [],
            items: section.items ?? [],
          })),
          claims: (report.report.claims ?? []).map((claim) => ({
            ...claim,
            source_message_ids: claim.source_message_ids ?? [],
            source_evidence_ids: claim.source_evidence_ids ?? [],
            mitre_technique_ids: claim.mitre_technique_ids ?? [],
          })),
          limitations: report.report.limitations ?? [],
        }
      : null,
  };
}
