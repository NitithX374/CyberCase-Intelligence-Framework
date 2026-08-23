import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CaseIntakeView } from "@/components/intake/CaseIntakeView";

describe("CaseIntakeView component", () => {
  it("renders the new case intake screen with required description and disabled material control", () => {
    const handleSubmit = vi.fn();

    render(
      <CaseIntakeView
        isSubmitting={false}
        error={null}
        onSubmitCase={handleSubmit}
      />,
    );

    expect(screen.getByText(/NEW INVESTIGATION/i)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /เริ่มวิเคราะห์คดีใหม่/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/ชื่อคดี/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/รายละเอียดคดี/i)).toBeInTheDocument();
    expect(screen.getByText(/Document upload is not available yet/i)).toBeInTheDocument();

    const submitBtn = screen.getByRole("button", { name: /Analyze case/i });
    expect(submitBtn).toBeDisabled();
  });

  it("submits case with title and description when form is valid", () => {
    const handleSubmit = vi.fn();

    render(
      <CaseIntakeView
        isSubmitting={false}
        error={null}
        onSubmitCase={handleSubmit}
      />,
    );

    const titleInput = screen.getByLabelText(/ชื่อคดี/i);
    const descInput = screen.getByLabelText(/รายละเอียดคดี/i);
    const submitBtn = screen.getByRole("button", { name: /Analyze case/i });

    fireEvent.change(titleInput, { target: { value: "IIS Server Intrusion" } });
    fireEvent.change(descInput, {
      target: { value: "Malicious scheduled task created on public server." },
    });

    expect(submitBtn).not.toBeDisabled();
    fireEvent.click(submitBtn);

    expect(handleSubmit).toHaveBeenCalledWith({
      title: "IIS Server Intrusion",
      description: "Malicious scheduled task created on public server.",
    });
  });

  it("shows loading state and disables inputs when isSubmitting is true", () => {
    render(
      <CaseIntakeView
        isSubmitting={true}
        error={null}
        onSubmitCase={vi.fn()}
      />,
    );

    expect(screen.getAllByText(/กำลังวิเคราะห์ข้อมูลคดี/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByLabelText(/ชื่อคดี/i)).toBeDisabled();
    expect(screen.getByLabelText(/รายละเอียดคดี/i)).toBeDisabled();
  });
});
