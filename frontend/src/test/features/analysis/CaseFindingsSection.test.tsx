import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CaseFindingsSection } from "@/features/analysis/CaseFindingsSection";
import type { CaseFinding, ClaimType, EpistemicStatus } from "@/features/analysis/types";
import { groupCaseFindings } from "@/features/analysis/overview";

const caseId = "22222222-2222-4222-8222-222222222222";

function finding(
  id: string,
  claimType: ClaimType = "reported",
  epistemicStatus: EpistemicStatus = "reported",
): CaseFinding {
  return {
    id,
    text: `Original finding ${id}`,
    claimType,
    epistemicStatus,
    reasoningSummary: null,
    supportingSources: [],
    contradictingSources: [],
    techniqueIds: [],
    unverifiedQuotes: [],
  };
}

describe("Grouped case findings", () => {
  it("preserves all combinations of claim type and status without inventing certainty", () => {
    const types: ClaimType[] = ["reported", "analytical_inference", "unknown"];
    const statuses: EpistemicStatus[] = [
      "reported",
      "suspected",
      "contradicted",
      "not_established",
      "unknown",
      "not_confirmed",
    ];
    const findings = types.flatMap((type) =>
      statuses.map((status) => finding(`${type}-${status}`, type, status)),
    );
    const snapshot = structuredClone(findings);
    const groups = groupCaseFindings(findings);
    expect(
      groups.flatMap((group) => group.findings).sort((a, b) => a.id.localeCompare(b.id)),
    ).toEqual([...findings].sort((a, b) => a.id.localeCompare(b.id)));
    expect(new Set(groups.flatMap((group) => group.findings.map((item) => item.id))).size).toBe(18);
    expect(groups.find((group) => group.id === "not_established")?.findings).toHaveLength(3);
    expect(groups.find((group) => group.id === "reported")?.findings).toEqual([findings[0]]);
    expect(findings).toEqual(snapshot);
  });

  it("keeps uncertainty visible before long reported groups and exposes every remaining finding", () => {
    const reported = Array.from({ length: 12 }, (_, index) => finding(`reported-${index}`));
    const uncertain = Array.from({ length: 7 }, (_, index) =>
      finding(`uncertain-${index}`, "analytical_inference", "not_established"),
    );
    const { container } = render(
      <CaseFindingsSection
        caseId={caseId}
        findings={[...reported, ...uncertain]}
        onSelectSource={vi.fn()}
      />,
    );
    expect(container.querySelector("article")).toHaveTextContent("Original finding uncertain-0");
    const uncertainty = screen.getByRole("region", { name: "Not established 7" });
    expect(within(uncertainty).getAllByRole("article")).toHaveLength(7);
    expect(within(uncertainty).queryByRole("button", { name: /Show/ })).not.toBeInTheDocument();
    expect(screen.queryByText("Original finding reported-11")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Show all 12 reported information" }));
    expect(screen.getByText("Original finding reported-11")).toBeVisible();
    expect(screen.getAllByRole("article")).toHaveLength(19);
    fireEvent.click(screen.getByRole("button", { name: "Show fewer reported information" }));
    expect(screen.getAllByRole("article")).toHaveLength(12);
  });

  it("shows both axes for an inference without established support", () => {
    render(
      <CaseFindingsSection
        caseId={caseId}
        findings={[
          finding("inference", "analytical_inference", "not_established"),
          finding("missing", "unknown", "unknown"),
        ]}
        onSelectSource={vi.fn()}
      />,
    );
    const inference = screen.getByRole("region", { name: "Not established 1" });
    expect(within(inference).getByRole("article")).toHaveTextContent("Inference");
    expect(screen.getByRole("region", { name: "Unknown 1" })).toHaveTextContent(
      "Original finding missing",
    );
  });

  it("links a technique to its entry on the Details page, where the ATT&CK table lives", () => {
    render(
      <CaseFindingsSection
        caseId={caseId}
        findings={[{ ...finding("phishing"), techniqueIds: ["T1566"] }]}
        onSelectSource={vi.fn()}
      />,
    );

    expect(screen.getByRole("link", { name: "T1566" })).toHaveAttribute(
      "href",
      `/case/${caseId}/analysis/details#mitre-T1566`,
    );
  });

  const passage = {
    id: "narrative-1",
    label: "Case narrative #1",
    excerpt: "The transfer happened on 17 March 2026 at noon.",
    displayContent: "The transfer happened on 17 March 2026 at noon.",
    exactQuote: "The transfer happened on 17 March 2026",
    quoteContext: null,
    filename: null,
    pageNumbers: [],
    sourcePages: [],
    question: null,
    quoteLabel: "Nearest passage",
  };
  const unverified = {
    writtenQuote: "The transfer happened on 11 March 2026 quickly",
    places: [
      { written: "11", source: "17" },
      { written: "quickly", source: "" },
      { written: "", source: "at noon" },
    ],
    passage,
    meaningPassage: null,
  };

  it("says where a not-confirmed finding's quote differs from the source and opens the passage", () => {
    const onSelectSource = vi.fn();
    render(
      <CaseFindingsSection
        caseId={caseId}
        findings={[
          {
            ...finding("transfer", "reported", "not_confirmed"),
            unverifiedQuotes: [
              unverified,
              { writtenQuote: "Invented.", places: [], passage: null, meaningPassage: null },
            ],
          },
        ]}
        onSelectSource={onSelectSource}
      />,
    );
    const article = screen.getByRole("article");

    expect(within(article).getAllByText("Not found word for word in the source.")).toHaveLength(2);
    expect(article).toHaveTextContent("The analysis quotes «11»; the source says «17»");
    expect(article).toHaveTextContent("The analysis adds «quickly»");
    expect(article).toHaveTextContent("The source has «at noon», which the analysis leaves out");
    const buttons = within(article).getAllByRole("button", { name: "Show in source" });
    expect(buttons).toHaveLength(1);
    fireEvent.click(buttons[0]);
    expect(onSelectSource).toHaveBeenCalledWith(passage, buttons[0], "passage-transfer-0");
  });

  const meaningPassage = {
    ...passage,
    id: "narrative-1",
    exactQuote: "The attackers encrypted the file server on Monday night.",
    quoteLabel: "A passage in the source that may be related (found by meaning, not confirmed)",
  };

  it("points a quote the words cannot place at the passage found by meaning, and says how it was found", () => {
    const onSelectSource = vi.fn();
    render(
      <CaseFindingsSection
        caseId={caseId}
        findings={[
          {
            ...finding("encrypted", "reported", "not_confirmed"),
            unverifiedQuotes: [
              { writtenQuote: "Invented.", places: [], passage: null, meaningPassage },
            ],
          },
        ]}
        onSelectSource={onSelectSource}
      />,
    );
    const article = screen.getByRole("article");

    expect(article).toHaveTextContent(
      "A passage in the source that may be related (found by meaning, not confirmed)",
    );
    const button = within(article).getByRole("button", { name: "Show in source" });
    fireEvent.click(button);
    expect(onSelectSource).toHaveBeenCalledWith(
      meaningPassage,
      button,
      "passage-encrypted-0-meaning",
    );
  });

  it("draws no badge, icon or score for the passage", () => {
    const { container } = render(
      <CaseFindingsSection
        caseId={caseId}
        findings={[
          {
            ...finding("encrypted", "reported", "not_confirmed"),
            unverifiedQuotes: [
              { writtenQuote: "Invented.", places: [], passage: null, meaningPassage },
            ],
          },
        ]}
        onSelectSource={vi.fn()}
      />,
    );

    expect(container.querySelector("svg, img")).toBeNull();
    expect(container.textContent).not.toMatch(/\d\.\d|%|score/i);
  });

  it("says nothing about a meaning passage under a finding that stayed reported", () => {
    render(
      <CaseFindingsSection
        caseId={caseId}
        findings={[
          {
            ...finding("transfer"),
            unverifiedQuotes: [{ ...unverified, passage: null, meaningPassage }],
          },
        ]}
        onSelectSource={vi.fn()}
      />,
    );

    expect(screen.queryByText(/found by meaning/)).not.toBeInTheDocument();
  });

  it("says nothing about unverified quotes under a finding that stayed reported", () => {
    render(
      <CaseFindingsSection
        caseId={caseId}
        findings={[{ ...finding("transfer"), unverifiedQuotes: [unverified] }]}
        onSelectSource={vi.fn()}
      />,
    );

    expect(screen.queryByText("Not found word for word in the source.")).not.toBeInTheDocument();
  });
});

describe("Findings reached from a summary link", () => {
  const many = Array.from({ length: 12 }, (_, index) =>
    finding(`A-${String(index + 1).padStart(2, "0")}`),
  );

  it("gives each finding an anchor named by its claim ID", () => {
    const { container } = render(
      <CaseFindingsSection
        caseId={caseId}
        findings={[finding("A-01"), finding("A-02")]}
        onSelectSource={vi.fn()}
      />,
    );

    expect(container.querySelector("#finding-A-01")).toHaveTextContent("Original finding A-01");
    expect(container.querySelector("#finding-A-02")).toHaveTextContent("Original finding A-02");
  });

  it("opens the long group that holds the finding the link names and scrolls to it", async () => {
    const scrollIntoView = vi.fn();
    Element.prototype.scrollIntoView = scrollIntoView;

    const { container } = render(
      <CaseFindingsSection
        caseId={caseId}
        findings={many}
        focusId="A-10"
        onSelectSource={vi.fn()}
      />,
    );

    const target = container.querySelector("#finding-A-10");
    expect(target).not.toBeNull();
    expect(screen.getAllByRole("article")).toHaveLength(12);
    await waitFor(() => expect(scrollIntoView).toHaveBeenCalledTimes(1));
    expect(scrollIntoView.mock.contexts[0]).toBe(target);
  });

  it("keeps a long group short when no link names one of its findings", () => {
    const scrollIntoView = vi.fn();
    Element.prototype.scrollIntoView = scrollIntoView;

    const { container } = render(
      <CaseFindingsSection caseId={caseId} findings={many} onSelectSource={vi.fn()} />,
    );

    expect(container.querySelector("#finding-A-10")).toBeNull();
    expect(screen.getAllByRole("article")).toHaveLength(5);
    expect(scrollIntoView).not.toHaveBeenCalled();
  });

  it("does nothing when the link names a finding that is not there", async () => {
    const scrollIntoView = vi.fn();
    Element.prototype.scrollIntoView = scrollIntoView;

    render(
      <CaseFindingsSection
        caseId={caseId}
        findings={many}
        focusId="A-99"
        onSelectSource={vi.fn()}
      />,
    );

    expect(screen.getAllByRole("article")).toHaveLength(5);
    await new Promise((resolve) => requestAnimationFrame(() => resolve(null)));
    expect(scrollIntoView).not.toHaveBeenCalled();
  });
});

it("explains an unresolved evidence ID without claiming a quote mismatch", () => {
  render(
    <CaseFindingsSection
      caseId={caseId}
      findings={[
        {
          ...finding("A-01", "reported", "not_confirmed"),
          unverifiedQuotes: [
            {
              writtenQuote: "",
              evidenceUnitId: "unknown-id",
              places: [],
              passage: null,
              meaningPassage: null,
            },
          ],
        },
      ]}
      onSelectSource={vi.fn()}
    />,
  );
  expect(screen.getByText("The evidence reference could not be resolved.")).toBeInTheDocument();
  expect(screen.queryByText("Not found word for word in the source.")).not.toBeInTheDocument();
});
