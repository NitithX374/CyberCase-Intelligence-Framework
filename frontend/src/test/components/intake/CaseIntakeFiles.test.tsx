import { act, fireEvent, render, screen, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { CaseIntakeView } from "@/components/intake/CaseIntakeView";
import type { PersistedChatMessage } from "@/lib/api";
import * as ingestionApi from "@/lib/document-ingestion";
import { resetDocumentIngestionState } from "@/lib/document-ingestion-store";

const previewResult: ingestionApi.IngestedDocumentPreview = {
  document_id: "DOC-1",
  filename: "statement.pdf",
  media_type: "application/pdf",
  extraction_method: "native_pdf",
  mode: "unified",
  full_text: "Reviewed case narrative",
  pages: [],
  warnings: [],
};

function chooseDocument(filename: string) {
  fireEvent.change(screen.getByLabelText(/Document for OCR preview/i), {
    target: { files: [new File(["pdf"], filename, { type: "application/pdf" })] },
  });
}

function filesPanel() {
  return within(screen.getByRole("complementary", { name: "Case Materials" }));
}

function evidenceMessage(
  id: string,
  evidenceKind: PersistedChatMessage["metadata_json"]["evidence_kind"],
  documentSources: NonNullable<PersistedChatMessage["metadata_json"]["document_sources"]>,
  role: PersistedChatMessage["role"] = "user",
): PersistedChatMessage {
  return {
    id,
    thread_id: "saved-case",
    ordinal: 1,
    role,
    content: "Case narrative",
    retrieval_context_id: null,
    metadata_json: { evidence_kind: evidenceKind, document_sources: documentSources },
    created_at: "2026-09-03T00:00:00Z",
  };
}

describe("Intake files integration", () => {
  beforeEach(() => {
    resetDocumentIngestionState();
    vi.restoreAllMocks();
  });

  it("updates filenames when selecting, replacing and clearing without submitting the narrative", () => {
    const submit = vi.fn();
    render(<CaseIntakeView isSubmitting={false} onSubmitCase={submit} />);
    fireEvent.change(screen.getByLabelText(/Case narrative/i), {
      target: { value: "A manually entered narrative" },
    });
    expect(filesPanel().getByText(/No documents added/)).toBeInTheDocument();

    chooseDocument("first.pdf");
    expect(filesPanel().getByText("first.pdf")).toBeInTheDocument();
    expect(filesPanel().getByText("Selected for extraction")).toBeInTheDocument();
    chooseDocument("replacement.pdf");
    expect(filesPanel().queryByText("first.pdf")).not.toBeInTheDocument();
    expect(filesPanel().getByText("replacement.pdf")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Clear preview" }));
    expect(filesPanel().getByText(/No documents added/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Case narrative/i)).toHaveValue("A manually entered narrative");
    expect(submit).not.toHaveBeenCalled();
  });

  it("keeps extraction separate from submission and lists a reviewed document only once", async () => {
    let finishExtraction!: (result: ingestionApi.IngestedDocumentPreview) => void;
    vi.spyOn(ingestionApi, "previewDocumentIngestion").mockImplementation(
      () => new Promise((resolve) => { finishExtraction = resolve; }),
    );
    const submit = vi.fn();
    render(<CaseIntakeView isSubmitting={false} onSubmitCase={submit} />);
    fireEvent.change(screen.getByLabelText(/Case narrative/i), {
      target: { value: "A manually entered narrative" },
    });
    chooseDocument("statement.pdf");
    fireEvent.click(screen.getByRole("button", { name: "Extract text" }));
    expect(filesPanel().getByRole("listitem")).toHaveTextContent("Extracting text…");
    expect(screen.getByRole("button", { name: /Analyze case/i })).toBeDisabled();

    await act(async () => { finishExtraction(previewResult); });
    expect(filesPanel().getByText("Text extraction complete")).toBeInTheDocument();
    expect(screen.getByLabelText(/Case narrative/i)).toHaveValue("A manually entered narrative");
    fireEvent.click(screen.getByRole("button", { name: /Use reviewed text/i }));
    expect(filesPanel().getAllByRole("listitem")).toHaveLength(1);
    expect(filesPanel().getByText("Reviewed narrative draft")).toBeInTheDocument();
    expect(screen.getByLabelText("Reviewed narrative text")).toHaveTextContent("Reviewed case narrative");

    fireEvent.click(screen.getByRole("button", { name: "Clear preview" }));
    expect(filesPanel().getByText("statement.pdf")).toBeInTheDocument();
    expect(submit).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: /Analyze case/i }));
    expect(submit).toHaveBeenCalledWith(expect.objectContaining({
      description: "Reviewed case narrative",
      documentSources: [expect.objectContaining({ document_id: "DOC-1" })],
    }));
  });

  it("lists unique saved evidence documents and excludes analytical or malformed metadata", () => {
    const source = { document_id: "DOC-1", filename: "statement.pdf" };
    const messages = [
      evidenceMessage("initial", "initial_case_narrative", [source, null as unknown as typeof source, { filename: "invalid.pdf" }]),
      evidenceMessage("added", "added_case_information", [source, { document_id: "DOC-2", filename: "receipt.pdf" }]),
      evidenceMessage("ask", "analyst_question", [{ document_id: "ASK", filename: "question.pdf" }]),
      evidenceMessage("assistant", "initial_case_narrative", [{ document_id: "AI", filename: "analysis.pdf" }], "assistant"),
    ];
    render(<CaseIntakeView messages={messages} isSubmitting={false} onSubmitCase={vi.fn()} />);
    expect(filesPanel().getAllByRole("listitem")).toHaveLength(2);
    expect(filesPanel().getByText("statement.pdf")).toBeInTheDocument();
    expect(filesPanel().getByText("receipt.pdf")).toBeInTheDocument();
    expect(filesPanel().queryByText("question.pdf")).not.toBeInTheDocument();
    expect(filesPanel().queryByText("analysis.pdf")).not.toBeInTheDocument();
  });

  it("keeps a case's selected file and narrative out of another case", () => {
    const props = { isSubmitting: false, onSubmitCase: vi.fn() };
    const { rerender } = render(<CaseIntakeView {...props} caseKey="case-A" />);
    chooseDocument("case-A.pdf");
    fireEvent.change(screen.getByLabelText(/Case narrative/i), { target: { value: "Case A only" } });

    rerender(<CaseIntakeView {...props} caseKey="case-B" />);
    expect(filesPanel().getByText(/No documents added/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Case narrative/i)).toHaveValue("");

    rerender(<CaseIntakeView {...props} caseKey="case-A" />);
    expect(filesPanel().getByText("case-A.pdf")).toBeInTheDocument();
  });
});
