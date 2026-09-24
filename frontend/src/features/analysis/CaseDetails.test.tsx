import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CaseDetails } from "./CaseDetails";
import type { SourceMessageRef } from "@/features/sources/types";

const statement: SourceMessageRef = {
  id: "source-1",
  ordinal: 1,
  label: "statement.pdf",
  excerpt: "received 52,000 baht",
  sourceType: "case_description",
  sourceTypeLabel: "Case narrative",
  fullContent: "received 52,000 baht",
  displayContent: "received 52,000 baht",
  exactQuote: "received 52,000 baht",
  documentId: "doc-1",
  filename: "statement.pdf",
  pageNumbers: [4],
  sourcePages: [],
};

const events = (count: number) =>
  Array.from({ length: count }, (_, index) => ({
    time: `09:0${index}`,
    event: `Event ${index + 1}`,
    sources: [],
    inferred: false,
  }));

describe("CaseDetails", () => {
  it("lists the timeline, parties and impacts under their own headings", () => {
    const onSelectSource = vi.fn();
    render(
      <CaseDetails
        timeline={[
          {
            time: "12 Sep, morning",
            event: "The attachment was opened",
            sources: [statement],
            inferred: false,
          },
        ]}
        parties={[{ name: "Somchai", role: "Account holder", sources: [], inferred: true }]}
        impacts={[{ description: "52,000 baht left the account", sources: [], inferred: false }]}
        onSelectSource={onSelectSource}
        activeSourceKey={null}
      />,
    );

    const timeline = screen.getByRole("region", { name: "Timeline 1" });
    expect(within(timeline).getByText("12 Sep, morning")).toBeInTheDocument();
    expect(within(timeline).getByText("The attachment was opened")).toBeInTheDocument();

    const parties = screen.getByRole("region", { name: "Parties 1" });
    expect(within(parties).getByText("Account holder")).toBeInTheDocument();
    expect(within(parties).getByText("Inference")).toBeInTheDocument();

    expect(screen.getByRole("region", { name: "Impact 1" })).toHaveTextContent(
      "52,000 baht left the account",
    );

    fireEvent.click(within(timeline).getByRole("button", { name: "p. 4" }));
    expect(onSelectSource).toHaveBeenCalledWith(
      statement,
      expect.any(HTMLElement),
      "timeline-0-source-1-0",
      undefined,
    );
  });

  it("folds a long timeline and opens it on request", () => {
    render(
      <CaseDetails
        timeline={events(8)}
        parties={[]}
        impacts={[]}
        onSelectSource={vi.fn()}
        activeSourceKey={null}
      />,
    );

    expect(screen.getAllByRole("listitem")).toHaveLength(6);
    fireEvent.click(screen.getByRole("button", { name: "Show all 8 events" }));
    expect(screen.getAllByRole("listitem")).toHaveLength(8);
  });

  it("renders nothing when the analysis wrote none of them", () => {
    const { container } = render(
      <CaseDetails
        timeline={[]}
        parties={[]}
        impacts={[]}
        onSelectSource={vi.fn()}
        activeSourceKey={null}
      />,
    );
    expect(container).toBeEmptyDOMElement();
  });
});
