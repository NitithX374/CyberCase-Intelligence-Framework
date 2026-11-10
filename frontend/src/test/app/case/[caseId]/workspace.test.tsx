import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type {
  CaseAnalysisResultRead,
  CaseChatRead,
  CaseRead,
  CaseSourceRead,
  ChatMessageRead,
} from "@/lib/api/types";
import { deferred } from "@/test/chat";
import { networkError, refusal, timeoutError } from "@/test/httpErrors";
import {
  analysisResult,
  caseId,
  claim,
  narrativeSource,
  sourceId,
  sourcesRead,
  trace,
} from "@/test/fixtures";
import CaseAnalysisLayout from "@/app/case/[caseId]/analysis/layout";
import CaseAnalysisPage from "@/app/case/[caseId]/analysis/page";
import CaseShellLayout from "@/app/case/[caseId]/layout";
import SourcesPage from "@/app/case/[caseId]/sources/page";

const backend = vi.hoisted(() => ({
  segment: "analysis",
  title: "Old title",
  revision: 1,
  analysis: null as CaseAnalysisResultRead | null,
  sources: [] as CaseSourceRead[],
  chat: { case_id: "", messages: [], pending_question_id: null } as CaseChatRead,
  add: vi.fn(),
  upload: vi.fn(),
  send: vi.fn(),
  start: vi.fn(),
  push: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  useParams: () => ({ caseId }),
  useRouter: () => ({ push: backend.push, replace: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
  useSelectedLayoutSegment: () => backend.segment,
  usePathname: () => `/case/${caseId}/${backend.segment}`,
}));

function storedCase(): CaseRead {
  return {
    id: caseId,
    title: backend.title,
    source_revision: backend.revision,
    latest_analysis_result_id: backend.analysis?.id ?? null,
    analysis_freshness: freshness(),
    created_at: "2026-09-10T00:00:00Z",
    updated_at: "2026-09-10T00:00:00Z",
  };
}

function freshness(): CaseRead["analysis_freshness"] {
  if (!backend.analysis) return "missing";
  return backend.analysis.source_revision === backend.revision ? "current" : "stale";
}

vi.mock("@/features/auth/api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/features/auth/api")>()),
  getSession: async () => ({ id: "user-1", email: "analyst@example.com", name: "Analyst" }),
}));

vi.mock("@/features/cases/api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/features/cases/api")>()),
  getCase: async () => storedCase(),
  updateCase: async (_caseId: string, title: string) => {
    backend.title = title;
    return storedCase();
  },
}));

vi.mock("@/features/chat/api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/features/chat/api")>()),
  getCaseChat: async () => backend.chat,
  createCaseChatMessage: (...args: unknown[]) => backend.send(...args),
}));

vi.mock("@/features/analysis/api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/features/analysis/api")>()),
  getCaseAnalysis: async () =>
    backend.analysis ? { ...backend.analysis, freshness: freshness() } : null,
  startCaseAnalysis: (...args: unknown[]) => backend.start(...args),
}));

vi.mock("@/features/sources/api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/features/sources/api")>()),
  listCaseSources: async () => [...backend.sources],
  addCaseSource: (...args: unknown[]) => backend.add(...args),
  uploadCaseDocument: (...args: unknown[]) => backend.upload(...args),
}));

vi.mock("@/features/reports/api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/features/reports/api")>()),
  listCaseReports: async () => [],
}));

const narrative = "Payroll files were encrypted overnight.";

async function addNarrative(_caseId: string, request: { exact_text: string }) {
  backend.revision += 1;
  const added = narrativeSource(request.exact_text, { id: `source-${backend.revision}` });
  backend.sources.push(added);
  return added;
}

function storedAnalysis(): CaseAnalysisResultRead {
  return analysisResult({
    summary: narrative,
    source_revision: backend.revision,
    trace_json: trace({ summary: narrative, claims: [claim(narrative)] }),
    external_context_json: { sources_read: sourcesRead(sourceId) },
  });
}

const question: ChatMessageRead = {
  id: "question-1",
  case_id: caseId,
  ordinal: 1,
  role: "assistant",
  content: "When did the encryption start?",
  message_kind: "followup_question",
  gap_key: "topic:incident-time",
  qa_id: "QA-01",
  analysis_result_id: null,
  in_reply_to_message_id: null,
  metadata_json: {},
  created_at: "2026-09-10T00:00:00Z",
};

function renderWorkspace(page: () => ReactNode) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { refetchOnWindowFocus: false, staleTime: 15_000, retry: false },
      mutations: { retry: false },
    },
  });
  const tree = (content: ReactNode) => (
    <QueryClientProvider client={queryClient}>
      <CaseShellLayout>{content}</CaseShellLayout>
    </QueryClientProvider>
  );
  const view = render(tree(page()));
  return {
    show: (segment: string, next: () => ReactNode) => {
      backend.segment = segment;
      view.rerender(tree(next()));
    },
  };
}

beforeEach(() => {
  localStorage.clear();
  localStorage.setItem("cybercase:account", "user-1");
  backend.segment = "analysis";
  backend.title = "Old title";
  backend.revision = 1;
  backend.sources = [narrativeSource(narrative)];
  backend.analysis = null;
  backend.chat = { case_id: caseId, messages: [], pending_question_id: null };
  backend.add.mockReset().mockImplementation(addNarrative);
  backend.upload.mockReset();
  backend.send.mockReset();
  backend.start.mockReset();
  backend.push.mockReset();
});

function narrativeDialog() {
  return document.querySelector<HTMLDialogElement>(
    'dialog[aria-labelledby="case-narrative-title"]',
  )!;
}

function topBar() {
  return within(
    screen
      .getByRole("navigation", { name: "Case workspace views" })
      .closest("header") as HTMLElement,
  );
}

function openNarrative() {
  const opener = screen
    .getAllByRole("button", { name: "Add narrative" })
    .find((button) => !narrativeDialog()?.contains(button))!;
  fireEvent.click(opener);
}

function writeNarrative(text: string) {
  openNarrative();
  fireEvent.change(screen.getByLabelText("Narrative"), { target: { value: text } });
  fireEvent.click(within(narrativeDialog()).getByRole("button", { name: "Add narrative" }));
}

describe("the case workspace", () => {
  it("shows the new title in the header once a rename is saved", async () => {
    backend.segment = "sources";
    renderWorkspace(() => <SourcesPage />);

    expect(await screen.findByRole("heading", { name: "Old title" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Rename case" }));
    const field = screen.getByLabelText("Case title");
    fireEvent.change(field, { target: { value: "New title" } });
    fireEvent.submit(field.closest("form")!);

    expect(await screen.findByRole("heading", { name: "New title" })).toBeInTheDocument();
  });

  it("waits for an answer being analysed instead of offering a first analysis beside it", async () => {
    localStorage.setItem("cybercase:ask-open", "true");
    backend.chat = { case_id: caseId, messages: [question], pending_question_id: question.id };
    backend.send.mockReturnValue(deferred().promise);
    renderWorkspace(() => (
      <CaseAnalysisLayout>
        <CaseAnalysisPage />
      </CaseAnalysisLayout>
    ));

    expect(
      await screen.findByRole("heading", { name: "Waiting for your answer" }),
    ).toBeInTheDocument();
    const analyzeButtons = screen.getAllByRole("button", { name: "Analyze" });
    expect(analyzeButtons).toHaveLength(2);
    analyzeButtons.forEach((button) => expect(button).toBeDisabled());
    expect(screen.getByText("Waiting for your answer in Ask")).toBeInTheDocument();
    await screen.findByText(question.content);
    const composer = screen.getByLabelText("Chat message");
    fireEvent.change(composer, { target: { value: "Around 02:00." } });
    fireEvent.submit(composer.closest("form")!);
    await waitFor(() => expect(backend.send).toHaveBeenCalledOnce());

    expect(await screen.findByRole("heading", { name: "Analyzing…" })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Not analyzed yet" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Analyze" })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Analyzing…" })).toBeDisabled();
    expect(backend.start).not.toHaveBeenCalled();
  });

  it("marks the analysis out of date as soon as a source is added", async () => {
    backend.analysis = storedAnalysis();
    const workspace = renderWorkspace(() => (
      <CaseAnalysisLayout>
        <CaseAnalysisPage />
      </CaseAnalysisLayout>
    ));
    expect(await screen.findByText("Up to date")).toBeInTheDocument();
    expect(screen.getByText("Analysis up to date")).toBeInTheDocument();
    expect(topBar().getByRole("button", { name: "Analyze again" })).toBeEnabled();

    workspace.show("sources", () => <SourcesPage />);
    await screen.findByRole("button", { name: "Upload file" });
    writeNarrative("A second narrative.");
    expect(await screen.findByText("Sources changed since the analysis")).toBeInTheDocument();
    expect(topBar().getByRole("button", { name: "Analyze" })).toBeEnabled();

    workspace.show("analysis", () => (
      <CaseAnalysisLayout>
        <CaseAnalysisPage />
      </CaseAnalysisLayout>
    ));
    await act(async () => {});

    await waitFor(() =>
      expect(screen.getAllByText("Sources changed since the analysis")).toHaveLength(2),
    );
    expect(screen.getAllByRole("button", { name: /Analyze/ })).toHaveLength(1);
  });

  it("runs the analysis from the top bar and opens the case", async () => {
    backend.segment = "sources";
    backend.start.mockImplementation(async () => {
      backend.analysis = storedAnalysis();
      return { ...backend.analysis, freshness: "current" };
    });
    renderWorkspace(() => <SourcesPage />);

    const analyze = await topBar().findByRole("button", {
      name: "Analyze",
    });
    await waitFor(() => expect(analyze).toBeEnabled());
    expect(topBar().getByRole("status")).toHaveTextContent("Not analyzed yet");
    fireEvent.click(analyze);

    await waitFor(() => expect(backend.start).toHaveBeenCalledOnce());
    expect(backend.push).toHaveBeenCalledWith(`/case/${caseId}/analysis`);
  });

  it("opens the narrative again after the browser closed it during a save that failed", async () => {
    backend.segment = "sources";
    const saving = deferred<never>();
    backend.add.mockReturnValue(saving.promise);
    renderWorkspace(() => <SourcesPage />);
    await screen.findByRole("button", { name: "Add narrative" });

    writeNarrative("A second narrative.");
    await waitFor(() => expect(backend.add).toHaveBeenCalledOnce());
    const dialog = narrativeDialog();
    expect(fireEvent(dialog, new Event("cancel", { cancelable: true }))).toBe(false);
    expect(dialog).toHaveAttribute("open");
    fireEvent(dialog, new Event("cancel"));
    dialog.close();
    fireEvent(dialog, new Event("close"));

    await act(async () => saving.reject(networkError()));
    fireEvent.click(await screen.findByRole("button", { name: "ปิด" }));

    openNarrative();
    await waitFor(() => expect(narrativeDialog()).toHaveAttribute("open"));
    expect(screen.getByLabelText("Narrative")).toBeInTheDocument();
  });

  it("shows an analysis the server stored although the request that asked for it failed", async () => {
    backend.start.mockImplementation(async () => {
      backend.analysis = storedAnalysis();
      throw timeoutError();
    });
    renderWorkspace(() => (
      <CaseAnalysisLayout>
        <CaseAnalysisPage />
      </CaseAnalysisLayout>
    ));

    const analyzeButtons = await screen.findAllByRole("button", { name: "Analyze" });
    fireEvent.click(analyzeButtons.find((button) => !button.closest("header"))!);

    expect(await screen.findByRole("heading", { name: "What happened" })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Not analyzed yet" })).not.toBeInTheDocument();
    expect(backend.start).toHaveBeenCalledOnce();
  });

  it("lists a document the server kept although its upload timed out", async () => {
    backend.segment = "sources";
    backend.upload.mockImplementation(async () => {
      backend.revision += 1;
      backend.sources.push(
        narrativeSource("Page text", {
          id: "source-document",
          source_kind: "document",
          document_id: "document-1",
          filename: "statement.pdf",
          mime_type: "application/pdf",
        }),
      );
      throw timeoutError();
    });
    renderWorkspace(() => <SourcesPage />);
    await screen.findByRole("button", { name: "Upload file" });

    fireEvent.change(screen.getByLabelText("Add file"), {
      target: { files: [new File(["%PDF"], "statement.pdf", { type: "application/pdf" })] },
    });

    expect(await screen.findByText("การดำเนินการใช้เวลานานกว่าที่กำหนด")).toBeInTheDocument();
    expect(await screen.findByRole("button", { name: /statement\.pdf/ })).toBeInTheDocument();
  });

  it("shows what the server kept of a failed answer, and retries it as the same message", async () => {
    localStorage.setItem("cybercase:ask-open", "true");
    backend.chat = { case_id: caseId, messages: [question], pending_question_id: question.id };
    const answer: ChatMessageRead = {
      ...question,
      id: "answer-1",
      ordinal: 2,
      role: "user",
      content: "Around 02:00.",
      message_kind: "followup_answer",
      in_reply_to_message_id: question.id,
    };
    const analysing = deferred<void>();
    backend.send
      .mockImplementationOnce(async () => {
        backend.chat = { case_id: caseId, messages: [question, answer], pending_question_id: null };
        throw refusal(502, "analysis_provider_down", "The analysis provider is unavailable");
      })
      .mockImplementationOnce(async () => {
        await analysing.promise;
        backend.analysis = storedAnalysis();
        return {
          messages: [answer],
          analysis: { ...backend.analysis, freshness: "current" },
          pending_question_id: null,
        };
      });
    renderWorkspace(() => (
      <CaseAnalysisLayout>
        <CaseAnalysisPage />
      </CaseAnalysisLayout>
    ));

    await screen.findByText(question.content);
    const composer = screen.getByLabelText("Chat message");
    fireEvent.change(composer, { target: { value: answer.content } });
    fireEvent.submit(composer.closest("form")!);

    const retry = await screen.findByRole("button", { name: "ลองอีกครั้ง" });
    await waitFor(() => expect(composer).toHaveAttribute("placeholder", "Ask about this case…"));
    expect(screen.getByText(answer.content, { ignore: "textarea" })).toBeInTheDocument();

    fireEvent.click(retry);

    expect(await screen.findByText("Updating the analysis with your answer…")).toBeInTheDocument();
    expect(screen.getAllByText(answer.content, { ignore: "textarea" })).toHaveLength(1);

    await act(async () => analysing.resolve());
    expect(await screen.findByRole("heading", { name: "What happened" })).toBeInTheDocument();
    expect(backend.send).toHaveBeenCalledTimes(2);
    const [first, second] = backend.send.mock.calls;
    expect(second[1].idempotencyKey).toBe(first[1].idempotencyKey);
  });
});
