import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AnalysisPipeline } from "@/features/analysis/AnalysisPipeline";
import { claim, trace } from "@/test/fixtures";

describe("analysis preparation", () => {
  it("summarizes source traceability without internal IDs or verifier diagnostics", () => {
    const { container } = render(
      <AnalysisPipeline
        trace={trace({
          claims: [
            claim("John sent an email."),
            claim("A source is missing.", undefined, {
              claim_id: "A-02",
              supporting_citations: [],
              epistemic_status: "not_confirmed",
            }),
          ],
          involved_parties: [{ name: "John", role: null, claim_ids: ["A-01"] }],
          timeline: [{ time: null, event: "John sent an email.", claim_ids: ["A-01"] }],
        })}
      />,
    );
    expect(screen.getByText("How this analysis was prepared")).toBeInTheDocument();
    expect(container).toHaveTextContent("Findings2");
    expect(container).toHaveTextContent("Findings with linked sources1");
    expect(container).toHaveTextContent("Findings needing source review1");
    expect(container).toHaveTextContent("Timeline events1");
    expect(container.textContent).not.toMatch(
      /A-0|unit IDs|resolution rate|verifier|admitted|withheld/,
    );
    expect(container).toHaveTextContent("a link alone does not establish");
  });

  it("keeps a meaningful extraction failure visible without exposing model configuration", () => {
    const { container } = render(
      <AnalysisPipeline
        trace={trace({
          view_extraction: {
            method: "llm",
            model: "internal/model",
            input_claim_ids: ["A-01"],
            excluded_claim_ids: [],
            duration_ms: 230,
            status: "failed",
            warning: "case_views_invalid",
            items_dropped: 0,
          },
        })}
      />,
    );
    expect(
      screen.getByText(/People, timeline and impacts could not be prepared/),
    ).toBeInTheDocument();
    expect(container.textContent).not.toMatch(/internal\/model|case_views_invalid|230|thinking/);
  });

  it("shows incomplete details without exposing rejected Claim IDs", () => {
    const { container } = render(
      <AnalysisPipeline
        trace={trace({
          view_extraction: {
            method: "llm",
            model: "internal/model",
            input_claim_ids: ["A-01"],
            excluded_claim_ids: [],
            duration_ms: 0,
            status: "completed",
            items_dropped: 2,
          },
        })}
      />,
    );
    expect(screen.getByText(/Some case details were omitted/)).toBeInTheDocument();
    expect(container.textContent).not.toMatch(/A-01|invalid IDs/);
  });
});
