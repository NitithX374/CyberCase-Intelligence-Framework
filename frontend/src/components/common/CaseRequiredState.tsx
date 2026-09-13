export function EmptyChatIntakeNotice({ onOpenIntake }: { onOpenIntake: () => void }) {
  return (
    <div className="flex items-center justify-between gap-3 border-b border-line bg-surface px-4 py-3 text-xs text-ink-secondary">
      <p className="truncate">
        ยังไม่ได้บันทึกรายละเอียดสำนวนคดี — เริ่มที่หน้า Intake เพื่อให้ระบบจัดทำภาพรวมคดี
      </p>
      <button
        type="button"
        onClick={onOpenIntake}
        className="shrink-0 text-[11px] font-bold text-ink hover:text-accent hover:underline"
      >
        เปิด Case Intake →
      </button>
    </div>
  );
}
