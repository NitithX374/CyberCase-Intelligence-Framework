import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Markdown } from "@/components/Markdown";

const TRACKER = "https://tracker.example/pixel.png?d=the-summary-of-the-case";

describe("Markdown", () => {
  it("renders no image for an inline image and keeps its alt text readable", () => {
    const { container } = render(
      <Markdown content={`Before ![Quarterly chart](${TRACKER}) after`} />,
    );

    expect(container.querySelector("img")).toBeNull();
    expect(container).toHaveTextContent("Before Quarterly chart after");
    expect(container).not.toHaveTextContent("tracker.example");
  });

  it("renders no image for a reference style image", () => {
    const { container } = render(<Markdown content={`![Logo][pixel]\n\n[pixel]: ${TRACKER}`} />);

    expect(container.querySelector("img")).toBeNull();
    expect(screen.getByText("Logo")).toBeInTheDocument();
  });

  it("renders no image for an image inside a link, and keeps the link", () => {
    const { container } = render(
      <Markdown content={`[![Open the report](${TRACKER})](https://example.test/report)`} />,
    );

    expect(container.querySelector("img")).toBeNull();
    expect(screen.getByRole("link", { name: "Open the report" })).toHaveAttribute(
      "href",
      "https://example.test/report",
    );
  });

  it("leaves nothing behind for an image without alt text", () => {
    const { container } = render(<Markdown content={`![](${TRACKER})`} />);

    expect(container.querySelector("img")).toBeNull();
    expect(container).not.toHaveTextContent("tracker.example");
  });

  it("still renders the rest of the formatting", () => {
    render(<Markdown content="A **finding** with `code`." />);

    expect(screen.getByText("finding").tagName).toBe("STRONG");
    expect(screen.getByText("code").tagName).toBe("CODE");
  });
});
