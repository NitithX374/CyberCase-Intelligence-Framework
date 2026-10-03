import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CaseDetails } from "@/features/analysis/CaseDetails";
import type { SourceMessageRef } from "@/features/citations/types";

const statement: SourceMessageRef = {
  id: "source-1",
  label: "statement.pdf · p. 4",
  excerpt: "received 52,000 baht",
  displayContent: "received 52,000 baht",
  exactQuote: "received 52,000 baht",
  quoteContext: null,
  filename: "statement.pdf",
  pageNumbers: [4],
  sourcePages: [{ pageNumber: 4, text: "received 52,000 baht" }],
  question: null,
};

const events = (count: number) =>
  Array.from({ length: count }, (_, index) => ({
    time: `09:0${index}`,
    event: `Event ${index + 1}`,
    sources: [],
    inferred: false,
    unconfirmed: [],
  }));

describe("CaseDetails", () => {
  it("prints both lines for a row whose claim is not confirmed and whose citation was not found", () => {
    render(
      <CaseDetails
        timeline={[
          {
            time: "Monday",
            event: "The account was frozen",
            sources: [],
            inferred: false,
            unconfirmed: ["not_confirmed"],
            supportNote: "No cited quotation was found in the sources.",
          },
        ]}
        parties={[]}
        impacts={[]}
        onSelectSource={vi.fn()}
        activeSourceKey={null}
      />,
    );

    expect(screen.getByText("ยังไม่ยืนยัน ไม่มี quote ที่ตรวจแล้ว")).toBeInTheDocument();
    expect(screen.getByText("No cited quotation was found in the sources.")).toBeInTheDocument();
  });

  it("prints the line for an item whose cited quotations were not found, even with no source to show", () => {
    render(
      <CaseDetails
        timeline={[
          {
            time: "Monday",
            event: "The account was frozen",
            sources: [],
            inferred: false,
            unconfirmed: [],
            supportNote: "No cited quotation was found in the sources.",
          },
        ]}
        parties={[
          {
            name: "Somchai",
            role: "Account holder",
            sources: [statement],
            inferred: false,
            unconfirmed: [],
            supportNote: "Some cited quotations were not found in the sources.",
          },
        ]}
        impacts={[
          {
            description: "A transfer was made",
            sources: [],
            inferred: false,
            unconfirmed: [],
            supportNote: "Not linked to any claim.",
          },
          {
            description: "A bound impact",
            sources: [statement],
            inferred: false,
            unconfirmed: [],
          },
        ]}
        onSelectSource={vi.fn()}
        activeSourceKey={null}
      />,
    );

    expect(screen.getByText("No cited quotation was found in the sources.")).toBeInTheDocument();
    expect(
      screen.getByText("Some cited quotations were not found in the sources."),
    ).toBeInTheDocument();
    expect(screen.getByText("Not linked to any claim.")).toBeInTheDocument();
    expect(screen.getAllByText(/quotation|claim\./)).toHaveLength(3);
  });

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
            unconfirmed: [],
          },
        ]}
        parties={[
          { name: "Somchai", role: "Account holder", sources: [], inferred: true, unconfirmed: [] },
        ]}
        impacts={[
          {
            description: "52,000 baht left the account",
            sources: [],
            inferred: false,
            unconfirmed: [],
          },
        ]}
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

    fireEvent.click(within(timeline).getByRole("button", { name: "statement.pdf · p. 4" }));
    expect(onSelectSource).toHaveBeenCalledWith(
      statement,
      expect.any(HTMLElement),
      "timeline-0-source-1-0",
      undefined,
    );
  });

  it("says in words that a row rests on a claim that is not confirmed or only suspected", () => {
    render(
      <CaseDetails
        timeline={[
          {
            time: "09:00",
            event: "A transfer left the account",
            sources: [],
            inferred: false,
            unconfirmed: ["not_confirmed"],
          },
        ]}
        parties={[
          {
            name: "Somchai",
            role: "Account holder",
            sources: [statement],
            inferred: false,
            unconfirmed: ["not_confirmed", "suspected"],
          },
        ]}
        impacts={[
          {
            description: "52,000 baht left the account",
            sources: [],
            inferred: true,
            unconfirmed: ["suspected"],
          },
        ]}
        onSelectSource={vi.fn()}
        activeSourceKey={null}
      />,
    );

    const timeline = within(screen.getByRole("region", { name: "Timeline 1" }));
    expect(timeline.getByText("ยังไม่ยืนยัน ไม่มี quote ที่ตรวจแล้ว")).toBeInTheDocument();
    expect(timeline.queryByRole("button")).not.toBeInTheDocument();

    const parties = within(screen.getByRole("region", { name: "Parties 1" }));
    expect(parties.getByText("ยังไม่ยืนยัน ไม่มี quote ที่ตรวจแล้ว")).toBeInTheDocument();
    expect(parties.getByText("อยู่ระหว่างตรวจสอบ")).toBeInTheDocument();
    expect(parties.getByRole("button", { name: "statement.pdf · p. 4" })).toBeInTheDocument();

    const impacts = within(screen.getByRole("region", { name: "Impact 1" }));
    expect(impacts.getByText("อยู่ระหว่างตรวจสอบ")).toBeInTheDocument();
    expect(impacts.getByText("Inference")).toBeInTheDocument();
  });

  it("adds no note to a row whose claims are all settled", () => {
    render(
      <CaseDetails
        timeline={events(1)}
        parties={[]}
        impacts={[]}
        onSelectSource={vi.fn()}
        activeSourceKey={null}
      />,
    );

    expect(screen.queryByText(/ยังไม่ยืนยัน|อยู่ระหว่างตรวจสอบ/)).not.toBeInTheDocument();
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
