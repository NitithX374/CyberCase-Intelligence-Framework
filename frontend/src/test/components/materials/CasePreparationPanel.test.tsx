import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { CasePreparationPanel } from "@/components/materials/CasePreparationPanel";
import type { CaseSourceRead } from "@/lib/api";

const evidence: CaseSourceRead = {
  id: "source-1",
  case_id: "case-1",
  source_kind: "narrative",
  document_id: null,
  origin_message_id: null,
  exact_text: "Received case material",
  source_metadata_json: {},
  created_at: "2026-09-11T00:00:00Z",
  archived_at: null,
};

function renderPreparation(overrides: Partial<React.ComponentProps<typeof CasePreparationPanel>> = {}) {
  const props: React.ComponentProps<typeof CasePreparationPanel> = {
    caseId: "case-1",
    evidence: [],
    caseStatus: null,
    processingStatus: null,
    analysisResult: null,
    isSubmitting: false,
    isCaseDataLoading: false,
    isUploading: false,
    onSubmitCase: vi.fn(),
    ...overrides,
  };
  render(<CasePreparationPanel {...props} />);
  return props;
}

describe("Case preparation panel", () => {
  it("starts native analysis from received Case evidence without another narrative", () => {
    const onSubmitCase = vi.fn();
    renderPreparation({ evidence: [evidence], onSubmitCase });

    const analyzeButton = screen.getByRole("button", { name: /Analyze case/i });
    expect(analyzeButton).not.toBeDisabled();
    fireEvent.click(analyzeButton);
    expect(onSubmitCase).toHaveBeenCalledWith({ title: undefined, description: "" });
  });

  it("keeps analysis disabled while Case material is loading", () => {
    renderPreparation({ isCaseDataLoading: true });

    expect(screen.getByRole("status")).toHaveTextContent("Loading case material");
    expect(screen.getByRole("button", { name: /Analyze case/i })).toBeDisabled();
  });

  it("submits the saved case title and narrative from the same materials page", () => {
    const onSubmitCase = vi.fn();
    renderPreparation({ onSubmitCase });

    fireEvent.change(screen.getByLabelText(/Case title/i), { target: { value: "Incident 42" } });
    fireEvent.change(screen.getByLabelText("Case information"), { target: { value: "A suspicious login occurred." } });
    fireEvent.click(screen.getByRole("button", { name: /Analyze case/i }));

    expect(onSubmitCase).toHaveBeenCalledWith({ title: "Incident 42", description: "A suspicious login occurred." });
  });
});
