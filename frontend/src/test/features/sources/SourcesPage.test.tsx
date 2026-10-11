import { fireEvent, render, screen, within } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { refusal } from "@/test/httpErrors";
import type { CaseSourceRead } from "@/lib/api/types";
import { SourcesPage } from "@/features/sources/SourcesPage";

const caseId = "22222222-2222-4222-8222-222222222222";

const narrative: CaseSourceRead = {
  id: "source-1",
  case_id: caseId,
  source_kind: "narrative",
  document_id: null,
  exact_text: "Files on the shared drive were reported encrypted.",
  provenance_json: {},
  source_metadata_json: {},
  created_at: "2026-09-11T00:00:00Z",
};

const state = vi.hoisted(() => ({
  sourcesFailed: false,
  sources: [] as CaseSourceRead[],
  freshness: undefined as "missing" | "current" | "stale" | undefined,
  canAnalyze: true,
  refetchSources: vi.fn(),
  upload: vi.fn(),
  push: vi.fn(),
  runAnalysis: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  useParams: () => ({ caseId }),
  useRouter: () => ({ push: state.push }),
}));
vi.mock("@/features/cases/queries", () => ({
  useCase: () => ({
    data: state.freshness ? { analysis_freshness: state.freshness } : undefined,
  }),
}));
vi.mock("@/features/analysis/queries", () => ({
  useAnalysisAvailability: () => ({
    isUpdating: false,
    isWaitingForFollowup: !state.canAnalyze,
    canAnalyze: state.canAnalyze,
  }),
}));
vi.mock("@/features/analysis/useRunCaseAnalysis", () => ({
  useRunCaseAnalysis: () => state.runAnalysis,
}));
vi.mock("@/features/chat/useCaseChat", () => ({
  useCaseChatQuery: () => ({ data: { case_id: caseId, messages: [] }, isLoading: false }),
}));
vi.mock("@/features/sources/queries", () => ({
  useCaseSources: () =>
    state.sourcesFailed
      ? { data: undefined, isLoading: false, isLoadingError: true, refetch: state.refetchSources }
      : { data: state.sources, isLoading: false },
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
  state.sources = [];
  state.freshness = undefined;
  state.canAnalyze = true;
  state.refetchSources.mockClear();
  state.upload.mockReset();
  state.push.mockClear();
  state.runAnalysis.mockClear();
});

describe("SourcesPage", () => {
  it("starts the analysis and opens the analysis page when Analyze is pressed", () => {
    state.sources = [narrative];
    state.freshness = "missing";
    renderPage();

    fireEvent.click(screen.getByRole("button", { name: "Analyze" }));

    expect(state.runAnalysis).toHaveBeenCalledOnce();
    expect(state.push).toHaveBeenCalledOnce();
    expect(state.push).toHaveBeenCalledWith(`/case/${caseId}/analysis`);
  });

  it("stays on the sources page while a follow-up question awaits an answer", () => {
    state.sources = [narrative];
    state.freshness = "stale";
    state.canAnalyze = false;
    renderPage();

    const button = screen.getByRole("button", { name: /^Analyze/ });
    expect(button).toBeDisabled();
    fireEvent.click(button);

    expect(state.runAnalysis).not.toHaveBeenCalled();
    expect(state.push).not.toHaveBeenCalled();
  });

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
