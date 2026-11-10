import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import CaseLegalPage from "@/app/case/[caseId]/legal/page";

const navigation = vi.hoisted(() => ({ replace: vi.fn(), push: vi.fn() }));

vi.mock("next/navigation", () => ({
  useParams: () => ({ caseId: "case 1" }),
  useRouter: () => navigation,
}));

describe("the legal route", () => {
  it("sends the reader to the outside references of the case", () => {
    const { container } = render(<CaseLegalPage />);

    expect(navigation.replace).toHaveBeenCalledWith("/case/case%201/analysis/legal");
    expect(navigation.push).not.toHaveBeenCalled();
    expect(container).toBeEmptyDOMElement();
  });
});
