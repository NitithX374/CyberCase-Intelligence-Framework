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

  it("does not render raw HTML elements by default", () => {
    const { container } = render(
      <Markdown content='Hello <button id="unsafe-btn">Click me</button>' />,
    );

    expect(container.querySelector("#unsafe-btn")).toBeNull();
    expect(container.querySelector("button")).toBeNull();
  });

  it("renders embedded HTML tables into structured table elements when allowHtml is enabled", () => {
    const { container } = render(
      <Markdown
        allowHtml
        content={
          "## Header\n<table><tr><td>ครั้งที่ ๑</td><td>วันที่ ๑๐ ก.พ.</td></tr></table>"
        }
      />,
    );

    expect(screen.getByRole("heading", { level: 2 })).toHaveTextContent("Header");
    const table = container.querySelector("table");
    expect(table).not.toBeNull();
    const cells = container.querySelectorAll("td");
    expect(cells).toHaveLength(2);
    expect(cells[0]).toHaveTextContent("ครั้งที่ ๑");
    expect(cells[1]).toHaveTextContent("วันที่ ๑๐ ก.พ.");
  });

  it("handles broken HTML tags gracefully without rendering raw markup tags when allowHtml is enabled", () => {
    const { container } = render(
      <Markdown allowHtml content="ขึ้น</td><td> ประกันส่งตัว</td></tr><tr><td> ผัดฟ้อง</td>" />,
    );

    expect(container.textContent).toContain("ขึ้น");
    expect(container.textContent).toContain("ประกันส่งตัว");
    expect(container.textContent).toContain("ผัดฟ้อง");
    expect(container.textContent).not.toContain("</td>");
    expect(container.textContent).not.toContain("</tr>");
  });

  it("suppresses scripts and unsafe javascript links even when allowHtml is enabled", () => {
    const { container } = render(
      <Markdown
        allowHtml
        content={'<script>window.pwned=true</script><a href="javascript:alert(1)">Click</a>'}
      />,
    );

    expect(container.querySelector("script")).toBeNull();
    const link = screen.getByText("Click");
    expect(link.getAttribute("href")).toBeNull();
  });
});
