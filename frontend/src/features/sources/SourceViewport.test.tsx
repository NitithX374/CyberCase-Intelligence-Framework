import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { StrictMode, useState } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { CaseSourceRead } from "@/lib/api/types";
import { narrativeSource } from "@/test/fixtures";
import type { RailItem } from "./SourceRail";
import { SourceViewport, type PreviewMode } from "./SourceViewport";

vi.mock("./api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("./api")>()),
  fetchCaseDocumentContent: async () => new Blob(["original"]),
}));

const urls = { created: [] as string[], revoked: new Set<string>() };
const originalCreate = URL.createObjectURL;
const originalRevoke = URL.revokeObjectURL;

beforeEach(() => {
  urls.created = [];
  urls.revoked = new Set();
  URL.createObjectURL = vi.fn(() => {
    const url = `blob:test/${urls.created.length + 1}`;
    urls.created.push(url);
    return url;
  });
  URL.revokeObjectURL = vi.fn((url: string) => {
    urls.revoked.add(url);
  });
});

afterEach(() => {
  URL.createObjectURL = originalCreate;
  URL.revokeObjectURL = originalRevoke;
});

function fileItem(filename: string, mimeType: string): RailItem {
  const source: CaseSourceRead = narrativeSource("Extracted text", {
    id: `source-${filename}`,
    source_kind: "document",
    document_id: `document-${filename}`,
    filename,
    mime_type: mimeType,
  });
  return { id: source.id, kind: "file", documentId: source.document_id!, source };
}

function Viewer({ item }: { item: RailItem }) {
  const [mode, setMode] = useState<PreviewMode>("original");
  return <SourceViewport caseId="case-1" item={item} mode={mode} onModeChange={setMode} />;
}

function renderViewer(item: RailItem) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <StrictMode>
      <QueryClientProvider client={queryClient}>
        <Viewer item={item} />
      </QueryClientProvider>
    </StrictMode>,
  );
}

function expectLive(url: string | null) {
  expect(url).toMatch(/^blob:test\//);
  expect(urls.revoked.has(url!)).toBe(false);
}

describe("the original file of a source", () => {
  it("keeps the download link live after switching to the text and back", async () => {
    renderViewer(fileItem("statement.docx", "application/octet-stream"));
    const first = await screen.findByRole("link", { name: "Download file" });
    expectLive(first.getAttribute("href"));

    fireEvent.click(screen.getByRole("tab", { name: "Text" }));
    fireEvent.click(screen.getByRole("tab", { name: "Original" }));

    const again = await screen.findByRole("link", { name: "Download file" });
    expectLive(again.getAttribute("href"));
  });

  it("keeps an embedded file live after switching to the text and back", async () => {
    renderViewer(fileItem("statement.pdf", "application/pdf"));
    expectLive((await screen.findByTitle("Original file: statement.pdf")).getAttribute("src"));

    fireEvent.click(screen.getByRole("tab", { name: "Text" }));
    fireEvent.click(screen.getByRole("tab", { name: "Original" }));

    expectLive((await screen.findByTitle("Original file: statement.pdf")).getAttribute("src"));
  });

  it("releases every URL it made once the preview closes", async () => {
    const view = renderViewer(fileItem("statement.docx", "application/octet-stream"));
    await screen.findByRole("link", { name: "Download file" });

    view.unmount();

    await waitFor(() => expect(urls.revoked.size).toBe(urls.created.length));
  });
});
