import type { SourceMessageRef } from "@/lib/case-overview-contracts";

export function formatPageReference(pageNumbers: number[]): string {
  if (pageNumbers.length === 1) return `p. ${pageNumbers[0]}`;
  return `pp. ${formatPageList(pageNumbers)}`;
}

export function formatEvidenceCitationText(
  sourceRef: Pick<SourceMessageRef, "label" | "pageNumbers" | "sourceType" | "isNativeEvidence">,
): string {
  if (sourceRef.pageNumbers.length > 0) return formatPageReference(sourceRef.pageNumbers);
  if (sourceRef.isNativeEvidence) return sourceRef.label;
  if (sourceRef.sourceType === "case_description") return "Case narrative";
  if (sourceRef.sourceType === "clarification_response") return "Clarification";
  return sourceRef.label;
}

function formatPageList(pageNumbers: number[]): string {
  const consecutive = pageNumbers.every(
    (page, index) => index === 0 || page === pageNumbers[index - 1] + 1,
  );
  return consecutive
    ? `${pageNumbers[0]}–${pageNumbers[pageNumbers.length - 1]}`
    : pageNumbers.join(", ");
}
