import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AnalysisPipeline } from "@/features/analysis/AnalysisPipeline";
import { claim, trace } from "@/test/fixtures";
import { sourceMetrics } from "@/test/features/analysis/validationFixtures";

describe("the saved Analysis pipeline", () => {
  it("displays structural resolution without a semantic projection stage", () => {
    const { container } = render(<AnalysisPipeline trace={trace({ grounding: sourceMetrics })} />);
    const binding = screen.getByRole("region", { name: "Source binding" });
    expect(binding).toHaveTextContent("Resolved IDs3");
    expect(binding).toHaveTextContent("Invalid IDs1");
    expect(binding).toHaveTextContent("ID resolution rate75.0%");
    expect(binding).toHaveTextContent("They do not establish semantic support.");
    expect(container.textContent).not.toMatch(/evidence/i);
    expect(
      screen.getByText("Reading → Source binding → Claim views → Judgement"),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("region", { name: "Saved description checks" }),
    ).not.toBeInTheDocument();
  });
  it("preserves earlier unavailable checks as saved history", () => {
    render(
      <AnalysisPipeline
        trace={trace({
          claims: [claim("John sent an email.")],
          involved_parties: [
            {
              name: "John",
              role: "Attacker",
              support: "bound",
              projection_grounding: {
                verdict: "not_supported",
                reason: "neutral",
              },
            },
          ],
          impacts: [
            {
              description: "A loss",
              projection_grounding: {
                verdict: "unassessed",
                reason: "model_unavailable:weights_missing",
              },
            },
          ],
        })}
      />,
    );
    const saved = screen.getByRole("region", { name: "Saved description checks" });
    expect(saved).toHaveTextContent("0 descriptions admitted; 2 withheld.");
    expect(saved).toHaveTextContent("New analyses record those facts in claims.");
    const input = screen.getByRole("region", { name: "Judgement input" });
    expect(input).toHaveTextContent("New analyses supply canonical claims");
    expect(screen.getByText(/model files are missing/)).toBeInTheDocument();
    expect(
      screen.getByText(/does not verify that the text supports every claim/),
    ).toBeInTheDocument();
    expect(screen.getByText("No source unit ID metrics were recorded.")).toBeInTheDocument();
    expect(input).not.toHaveTextContent(/confirmed/i);
  });

  it("does not describe historical unchecked items as admitted or rejected", () => {
    render(
      <AnalysisPipeline
        trace={trace({ impacts: [{ description: "Historic loss", support: "bound" }] })}
      />,
    );
    const checked = screen.getByRole("region", { name: "Saved description checks" });
    expect(within(checked).getByText("Check not recorded")).toBeInTheDocument();
    expect(checked).toHaveTextContent("Judgement use was not recorded for 1 descriptions");
  });

  it("distinguishes extracted views from historical semantic checks and Judgement input", () => {
    render(
      <AnalysisPipeline
        trace={trace({
          view_extraction: {
            method: "gliner2",
            model: "fastino/gliner2-multi-v1",
            revision: "c".repeat(40),
            library_version: "1.3.2",
            device: "cpu",
            threshold: 0.5,
            input_claim_ids: ["A-01"],
            excluded_claim_ids: ["A-02"],
            duration_ms: 120,
          },
          involved_parties: [
            {
              name: "John",
              role: null,
              claim_ids: ["A-01"],
              field_spans: { name: { claim_id: "A-01", start: 0, end: 4 } },
            },
          ],
        })}
      />,
    );
    const extracted = screen.getByRole("region", { name: "Claim views" });
    expect(extracted).toHaveTextContent("Claims processed1");
    expect(extracted).toHaveTextContent("These views are not supplied to Judgement");
    expect(extracted).toHaveTextContent("no semantic verdict");
    expect(
      screen.queryByRole("region", { name: "Saved description checks" }),
    ).not.toBeInTheDocument();
  });
});
