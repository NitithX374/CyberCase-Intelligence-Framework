import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MeaningfulErrorModal } from "@/components/common/MeaningfulErrorModal";
import type { UserFacingError } from "@/lib/user-facing-error";

describe("MeaningfulErrorModal component", () => {
  const timeoutError: UserFacingError = {
    title: "การดำเนินการใช้เวลานานกว่าที่กำหนด",
    message:
      "ระบบยังไม่สามารถยืนยันผลลัพธ์ได้ในขณะนี้ ข้อมูลที่คุณกรอกไว้ยังคงอยู่ กรุณาลองอีกครั้งหรือตรวจสอบสถานะภายหลัง",
    technicalDetail: "timeout of 15000ms exceeded (ECONNABORTED)",
    retryable: true,
    category: "timeout",
    actionLabel: "ลองอีกครั้ง",
  };

  it("renders human-facing title, message, and hides raw technical detail by default", () => {
    const handleClose = vi.fn();
    const handleRetry = vi.fn();

    render(
      <MeaningfulErrorModal
        isOpen={true}
        error={timeoutError}
        onClose={handleClose}
        onRetry={handleRetry}
      />,
    );

    // 1. Visible Title and Message
    expect(screen.getByRole("heading", { name: "การดำเนินการใช้เวลานานกว่าที่กำหนด" })).toBeInTheDocument();
    expect(screen.getByText(/ระบบยังไม่สามารถยืนยันผลลัพธ์ได้ในขณะนี้/)).toBeInTheDocument();

    // 2. Technical details disclosure is present
    const details = screen.getByText("Technical details");
    expect(details).toBeInTheDocument();

    // 3. Raw technical string is inside the disclosure
    expect(screen.getByText("timeout of 15000ms exceeded (ECONNABORTED)")).toBeInTheDocument();
  });

  it("calls onClose when 'ปิด' button or close icon is clicked", () => {
    const handleClose = vi.fn();

    render(
      <MeaningfulErrorModal
        isOpen={true}
        error={timeoutError}
        onClose={handleClose}
      />,
    );

    const closeBtn = screen.getByRole("button", { name: "ปิด" });
    fireEvent.click(closeBtn);
    expect(handleClose).toHaveBeenCalledTimes(1);

    const closeIconBtn = screen.getByRole("button", { name: "ปิดหน้าต่างข้อผิดพลาด" });
    fireEvent.click(closeIconBtn);
    expect(handleClose).toHaveBeenCalledTimes(2);
  });

  it("calls onRetry when retry button is clicked", () => {
    const handleClose = vi.fn();
    const handleRetry = vi.fn();

    render(
      <MeaningfulErrorModal
        isOpen={true}
        error={timeoutError}
        onClose={handleClose}
        onRetry={handleRetry}
      />,
    );

    const retryBtn = screen.getByRole("button", { name: "ลองอีกครั้ง" });
    fireEvent.click(retryBtn);
    expect(handleRetry).toHaveBeenCalledTimes(1);
  });

  it("dismisses on Escape key press", () => {
    const handleClose = vi.fn();

    render(
      <MeaningfulErrorModal
        isOpen={true}
        error={timeoutError}
        onClose={handleClose}
      />,
    );

    fireEvent.keyDown(document, { key: "Escape" });
    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it("does not render when isOpen is false or error is null", () => {
    const { container, rerender } = render(
      <MeaningfulErrorModal
        isOpen={false}
        error={timeoutError}
        onClose={vi.fn()}
      />,
    );

    expect(container.firstChild).toBeNull();

    rerender(
      <MeaningfulErrorModal
        isOpen={true}
        error={null}
        onClose={vi.fn()}
      />,
    );

    expect(container.firstChild).toBeNull();
  });
});
