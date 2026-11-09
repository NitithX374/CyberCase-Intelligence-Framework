import { render, screen, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { CaseSidebar } from "@/features/workspace/CaseSidebar";
import type { CaseAnalysisClaim } from "@/lib/api/types";
import {
  analysisResult,
  caseId,
  claim,
  narrativeSource,
  sourcesRead,
  trace,
} from "@/test/fixtures";

const source = narrativeSource("Room 503 was broken into.");
const base = `/case/${caseId}`;

const state = vi.hoisted(() => ({
  pathname: "",
  claims: [] as CaseAnalysisClaim[],
  analysed: true,
}));

vi.mock("next/navigation", () => ({ usePathname: () => state.pathname }));
vi.mock("@/features/analysis/queries", () => ({
  useCaseAnalysis: () => ({
    data: state.analysed
      ? analysisResult({
          trace_json: trace({
            summary: "A theft.",
            claims: state.claims,
            involved_parties: [{ name: "Tenant A", role: "Suspect", claim_ids: ["A-01"] }],
          }),
          external_context_json: { sources_read: sourcesRead(source.id) },
        })
      : null,
    isLoading: false,
  }),
}));
vi.mock("@/features/sources/queries", () => ({
  useCaseSources: () => ({ data: [source], isLoading: false }),
}));

beforeEach(() => {
  state.pathname = `${base}/analysis`;
  state.analysed = true;
  state.claims = [
    claim("Room 503 was broken into.", source.id, {
      semantic_grounding: { verdict: "not_supported", reason: "lr_not_supported" },
    }),
    claim("The safe was empty.", source.id, { claim_id: "A-02" }),
  ];
});

const casePages = () => within(screen.getByRole("navigation", { name: "Case pages" }));
const material = () => within(screen.getByRole("navigation", { name: "Case material" }));

describe("CaseSidebar", () => {
  it("lists Timeline, People and Impact as pages of their own", () => {
    render(<CaseSidebar caseId={caseId} caseTitle="Dormitory theft" />);

    expect(casePages().getByRole("link", { name: /^Reading/ })).toHaveAttribute(
      "href",
      `${base}/analysis`,
    );
    expect(casePages().getByRole("link", { name: /^Timeline/ })).toHaveAttribute(
      "href",
      `${base}/analysis/timeline`,
    );
    expect(casePages().getByRole("link", { name: /^People/ })).toHaveAttribute(
      "href",
      `${base}/analysis/people`,
    );
    expect(casePages().getByRole("link", { name: /^Impact/ })).toHaveAttribute(
      "href",
      `${base}/analysis/impact`,
    );
    expect(casePages().getByRole("link", { name: "Outside references" })).toHaveAttribute(
      "href",
      `${base}/analysis#section-references`,
    );
    expect(material().getByRole("link", { name: /^Sources/ })).toHaveAttribute(
      "href",
      `${base}/sources`,
    );
    expect(material().getByRole("link", { name: "Report" })).toHaveAttribute(
      "href",
      `${base}/report`,
    );
  });

  it("marks the reading page as current on the overview", () => {
    render(<CaseSidebar caseId={caseId} caseTitle="Dormitory theft" />);

    const current = screen
      .getAllByRole("link")
      .filter((link) => link.getAttribute("aria-current") === "page");
    expect(current).toHaveLength(1);
    expect(current[0]).toHaveAccessibleName(/^Reading\s*2$/);
  });

  it("marks a fact page as current, not the reading page", () => {
    state.pathname = `${base}/analysis/people`;
    render(<CaseSidebar caseId={caseId} caseTitle="Dormitory theft" />);

    expect(casePages().getByRole("link", { name: /^People/ })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(casePages().getByRole("link", { name: /^Reading/ })).not.toHaveAttribute("aria-current");
  });

  it("marks the sources page as current", () => {
    state.pathname = `${base}/sources`;
    render(<CaseSidebar caseId={caseId} caseTitle="Dormitory theft" />);

    expect(material().getByRole("link", { name: /^Sources\s*1$/ })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(casePages().getByRole("link", { name: /^Reading/ })).not.toHaveAttribute("aria-current");
  });

  it("counts the findings to check", () => {
    render(<CaseSidebar caseId={caseId} caseTitle="Dormitory theft" />);

    expect(screen.getByText("Dormitory theft")).toBeInTheDocument();
    expect(screen.getByText("1 of 2 findings to check")).toBeInTheDocument();
    expect(casePages().getByRole("link", { name: /^People\s*1$/ })).toBeInTheDocument();
  });

  it("says when a case has not been analyzed", () => {
    state.analysed = false;
    render(<CaseSidebar caseId={caseId} caseTitle="Dormitory theft" />);

    expect(screen.getByText("Not analyzed yet")).toBeInTheDocument();
    expect(screen.queryByText(/findings to check/)).not.toBeInTheDocument();
  });
});
