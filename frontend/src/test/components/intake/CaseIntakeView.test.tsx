import { render, screen, fireEvent } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { CaseIntakeView } from "@/components/intake/CaseIntakeView";
import type { PersistedChatMessage } from "@/lib/api";
import {
  resetDocumentIngestionState,
  setDocumentIngestionFile,
  setDocumentIngestionResult,
} from "@/lib/document-ingestion-store";
import type { IngestedDocumentPreview } from "@/lib/document-ingestion";

describe("CaseIntakeView component", () => {
  beforeEach(() => {
    resetDocumentIngestionState();
  });

  it("renders the new case intake screen with required description and document preview", () => {
    const handleSubmit = vi.fn();

    render(
      <CaseIntakeView
        isSubmitting={false}
        error={null}
        onSubmitCase={handleSubmit}
      />,
    );

    expect(screen.getByText(/CASE INTAKE/i)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Case preparation" })).toBeInTheDocument();
    expect(screen.getByLabelText(/Case title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Case narrative/i)).toBeInTheDocument();
    expect(
      screen.getByLabelText(/Document for OCR preview/i),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /Extract text/i }),
    ).toBeDisabled();

    const submitBtn = screen.getByRole("button", { name: /Analyze case/i });
    expect(submitBtn).toBeDisabled();
  });

  it("submits case with title and description when form is valid and preserves draft description", () => {
    const handleSubmit = vi.fn();

    render(
      <CaseIntakeView
        isSubmitting={false}
        error={null}
        onSubmitCase={handleSubmit}
      />,
    );

    const titleInput = screen.getByLabelText(/Case title/i) as HTMLInputElement;
    const descInput = screen.getByLabelText(/Case narrative/i) as HTMLTextAreaElement;
    const submitBtn = screen.getByRole("button", { name: /Analyze case/i });

    fireEvent.change(titleInput, { target: { value: "IIS Server Intrusion" } });
    fireEvent.change(descInput, {
      target: { value: "Malicious scheduled task created on public server." },
    });

    expect(submitBtn).not.toBeDisabled();
    fireEvent.click(submitBtn);

    expect(handleSubmit).toHaveBeenCalledWith({
      title: "IIS Server Intrusion",
      description: "Malicious scheduled task created on public server.",
    });

    // Draft description must NOT be prematurely cleared on submit
    expect(descInput.value).toBe("Malicious scheduled task created on public server.");
  });

  it("shows loading state and disables inputs when isSubmitting is true", () => {
    render(
      <CaseIntakeView
        isSubmitting={true}
        error={null}
        onSubmitCase={vi.fn()}
      />,
    );

    expect(screen.getAllByText(/Analyzing case/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByLabelText(/Case title/i)).toBeDisabled();
    expect(screen.getByLabelText(/Case narrative/i)).toBeDisabled();
  });

  it("fills an editable narrative and submits document quality metadata", () => {
    const result: IngestedDocumentPreview = {
      document_id: "DOC-OCR-1",
      filename: "statement.pdf",
      media_type: "application/pdf",
      extraction_method: "document_recognition",
      mode: "unified",
      pages: [
        {
          page_number: 1,
          merged_text: "OCR merged narrative",
          routing_summary: {
            native: 0,
            unified: 1,
            ocr: 0,
            htr: 0,
            mixed: 0,
            unknown: 0,
          },
          regions: [
            {
              region_id: "DOC-OCR-1-P001-R001",
              page_number: 1,
              bbox: null,
              region_type: "unknown",
              recognition_method: "unified",
              recognizer: "typhoon-ocr",
              text: "OCR merged narrative",
              segmentation_confidence: null,
              recognition_confidence: null,
              words: [],
              verification_status: "machine_read",
              content_role: "transcribed_text",
              contains_handwriting: null,
              candidates: [],
              selected_candidate_index: null,
              generated_contents: [],
              warning: null,
            },
          ],
        },
      ],
      full_text: "OCR merged narrative",
      warnings: [],
    };
    const handleSubmit = vi.fn();
    setDocumentIngestionFile(
      new File(["pdf"], "statement.pdf", { type: "application/pdf" }),
    );
    setDocumentIngestionResult(result);
    render(
      <CaseIntakeView
        isSubmitting={false}
        error={null}
        onSubmitCase={handleSubmit}
      />,
    );

    fireEvent.click(
      screen.getByRole("button", { name: /Use reviewed text/i }),
    );
    expect(screen.getByLabelText("Reviewed narrative text")).toHaveTextContent("OCR merged narrative");
    fireEvent.click(screen.getByRole("tab", { name: "Raw Text" }));
    const narrative = screen.getByLabelText("Edit raw narrative");
    expect(narrative).toHaveValue("OCR merged narrative");
    expect(screen.getByText(/did not report confidence/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Analyze case/i }));

    expect(handleSubmit).toHaveBeenCalledWith({
      title: undefined,
      description: "OCR merged narrative",
      documentSources: [
        expect.objectContaining({
          document_id: "DOC-OCR-1",
          confidence_status: "not_reported",
          verification_status: "machine_read",
        }),
      ],
    });
  });

  it("renders active case intake record and navigation when case already has evidence, without rendering additional submission form", async () => {
    const existingMessages: PersistedChatMessage[] = [
      {
        id: "msg-1",
        thread_id: "thread-1",
        ordinal: 1,
        role: "user",
        content: "รายละเอียดสำนวนคดีเริ่มต้นเรื่องเซิร์ฟเวอร์ถูกบุกรุก",
        retrieval_context_id: null,
        metadata_json: { evidence_kind: "initial_case_narrative" },
        created_at: "2026-08-24T06:00:00Z",
      },
    ];

    const onOpenOverview = vi.fn();
    const onOpenChat = vi.fn();
    const onOpenMaterials = vi.fn();

    render(
      <CaseIntakeView
        isSubmitting={false}
        error={null}
        onSubmitCase={vi.fn()}
        messages={existingMessages}
        onOpenOverview={onOpenOverview}
        onOpenChat={onOpenChat}
        onOpenMaterials={onOpenMaterials}
      />,
    );

    expect(screen.getByText(/CASE INTAKE/i)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Case preparation" })).toBeInTheDocument();
    expect(screen.getByLabelText("Case narrative text")).toHaveTextContent("รายละเอียดสำนวนคดีเริ่มต้นเรื่องเซิร์ฟเวอร์ถูกบุกรุก");
    expect(screen.queryByText(/ACTIVE CASE/i)).not.toBeInTheDocument();

    const chatBtn = screen.getByRole("button", { name: /Open analysis in Chat/i });
    const materialsBtn = screen.getByRole("button", { name: /Open case materials/i });
    expect(
      screen.getByLabelText(/Document for OCR preview/i),
    ).toBeInTheDocument();

    fireEvent.click(chatBtn);
    expect(onOpenChat).toHaveBeenCalled();

    fireEvent.click(materialsBtn);
    expect(onOpenMaterials).toHaveBeenCalled();

    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Analyze updates/i })).not.toBeInTheDocument();
  }, 15000);
});
