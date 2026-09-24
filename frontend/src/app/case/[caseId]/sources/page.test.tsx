import { fireEvent, render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { refusal } from "@/test/httpErrors";
import SourcesPage from "./page";

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
  useCaseChatMessages: () => ({ data: [], isLoading: false }),
}));
vi.mock("@/features/sources/queries", () => ({
  useCaseDocuments: () => ({ data: [], isLoading: false }),
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
});
