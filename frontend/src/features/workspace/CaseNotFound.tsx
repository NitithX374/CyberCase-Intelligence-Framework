import Link from "next/link";
import { EmptyState } from "@/components/EmptyState";

export function CaseNotFound() {
  return (
    <main className="flex h-dvh flex-col justify-center bg-surface px-6 py-16 text-ink">
      <EmptyState
        title="ไม่พบคดีนี้"
        description="คดีนี้อาจถูกลบไปแล้ว หรือลิงก์ไม่ถูกต้อง กรุณากลับไปเลือกคดีจากรายการคดี"
      >
        <Link href="/case" className="btn-primary mt-5">
          กลับไปที่รายการคดี
        </Link>
      </EmptyState>
    </main>
  );
}
