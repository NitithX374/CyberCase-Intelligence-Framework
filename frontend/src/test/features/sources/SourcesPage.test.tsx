import { fireEvent, render, screen, within } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { refusal } from "@/test/httpErrors";
import { SourcesPage } from "@/features/sources/SourcesPage";

const caseId = "22222222-2222-4222-8222-222222222222";

const state = vi.hoisted(() => ({
  sourcesFailed: false,
  refetchSources: vi.fn(),
  upload: vi.fn(),
}));

vi.mock("next/navigation", () => ({ useParams: () => ({ caseId }) }));
vi.mock("@/features/cases/queries", () => ({ useCase: () => ({ data: undefined }) }));
vi.mock("@/features/analysis/queries", () => ({ useIsAnalysisUpdating: () => false }));
vi.mock("@/features/analysis/useRunCaseAnalysis", () => ({
  useRunCaseAnalysis: () => vi.fn(),
}));
vi.mock("@/features/chat/useCaseChat", () => ({
  useCaseChatQuery: () => ({ data: { case_id: caseId, messages: [] }, isLoading: false }),
}));
vi.mock("@/features/sources/queries", () => ({
  useCaseSources: () =>
    state.sourcesFailed
      ? { data: undefined, isLoading: false, isLoadingError: true, refetch: state.refetchSources }
      : { data: [], isLoading: false },
  useUploadCaseDocument: () => ({ isPending: false, mutateAsync: state.upload }),
}));

function renderPage() {
  render(
    <QueryClientProvider client={new QueryClient()}>
      <SourcesPage />
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  state.sourcesFailed = false;
  state.refetchSources.mockClear();
  state.upload.mockReset();
});

describe("SourcesPage", () => {
  it("offers to load failed sources again, never to add them again", () => {
    state.sourcesFailed = true;
    renderPage();

    expect(
      screen.getByRole("heading", { name: "Sources could not be loaded" }),
    ).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "No sources yet" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Upload file/ })).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Try again" }));
    expect(state.refetchSources).toHaveBeenCalledOnce();
  });

  it("says in Thai why a document was refused", async () => {
    state.upload.mockRejectedValue(
      refusal(422, "extraction_text_empty", "Document extraction text is empty"),
    );
    renderPage();

    fireEvent.change(screen.getByLabelText("Add file"), {
      target: { files: [new File(["%PDF"], "blank.pdf", { type: "application/pdf" })] },
    });

    const dialog = await screen.findByRole("dialog");
    expect(dialog.querySelector("#meaningful-error-message")).toHaveTextContent(
      "ไม่พบข้อความที่อ่านได้ในเอกสารนี้",
    );
    expect(dialog).toHaveTextContent("Reason: extraction_text_empty");
    expect(dialog).not.toHaveTextContent("เกิดข้อผิดพลาดที่ไม่คาดคิด");
  });

  it("tells the reader to split a file when the sources would be too large, with no retry", async () => {
    state.upload.mockRejectedValue(
      refusal(413, "source_too_large", "The case sources would exceed what the analysis can read"),
    );
    renderPage();

    fireEvent.change(screen.getByLabelText("Add file"), {
      target: { files: [new File(["%PDF"], "long.pdf", { type: "application/pdf" })] },
    });

    const dialog = await screen.findByRole("dialog");
    const message = dialog.querySelector("#meaningful-error-message");
    expect(message).toHaveTextContent("แบ่งไฟล์");
    expect(message).toHaveTextContent("ทั้งหมดของคดีนี้");
    expect(message).not.toHaveTextContent("exceed");
    expect(within(dialog).queryByRole("button", { name: "ลองอีกครั้ง" })).not.toBeInTheDocument();
  });

  it("says in Thai that the case is being analysed when a file is refused for it", async () => {
    state.upload.mockRejectedValue(
      refusal(
        409,
        "analysis_in_progress",
        "The case is being analysed, so a source cannot be added now",
      ),
    );
    renderPage();

    fireEvent.change(screen.getByLabelText("Add file"), {
      target: { files: [new File(["%PDF"], "late.pdf", { type: "application/pdf" })] },
    });

    const dialog = await screen.findByRole("dialog");
    expect(dialog.querySelector("#meaningful-error-message")).toHaveTextContent("กำลังวิเคราะห์");
    expect(within(dialog).queryByRole("button", { name: "ลองอีกครั้ง" })).not.toBeInTheDocument();
  });
});
