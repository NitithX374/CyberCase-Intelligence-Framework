import { Icon } from "@/components/common/icons";

interface EmptyStateCaseRequiredProps {
  title: string;
  subtitle: string;
  description: string;
  onOpenIntake: () => void;
}

export function EmptyStateCaseRequired({
  title,
  subtitle,
  description,
  onOpenIntake,
}: EmptyStateCaseRequiredProps) {
  return (
    <div className="flex min-h-0 flex-1 flex-col items-center justify-center bg-canvas p-6 text-center">
      <div className="workspace-card max-w-md space-y-4 p-8">
        <span className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-surface-nested text-ink-secondary">
          <Icon name="intake" className="h-5 w-5" />
        </span>
        <div className="space-y-1">
          <h2 className="text-base font-bold text-ink">{title}</h2>
          <p className="text-xs font-semibold text-ink-secondary">{subtitle}</p>
          <p className="pt-1 text-xs leading-relaxed text-ink-muted">{description}</p>
        </div>
        <button
          type="button"
          onClick={onOpenIntake}
          className="btn-primary inline-flex items-center gap-2 rounded-lg"
        >
          <Icon name="intake" className="h-3.5 w-3.5" />
          <span>Go to Case Intake · เปิดสำนวนคดี</span>
        </button>
      </div>
    </div>
  );
}

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
