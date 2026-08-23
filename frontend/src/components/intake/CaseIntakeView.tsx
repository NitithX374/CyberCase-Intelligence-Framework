"use client";

import { useState, type FormEvent } from "react";
import { Icon } from "@/components/common/icons";
import type { PersistedChatMessage } from "@/lib/api";

interface CaseIntakeViewProps {
  isSubmitting: boolean;
  error: string | null;
  onSubmitCase: (data: { title?: string; description: string }) => void;
  messages?: PersistedChatMessage[];
  onOpenOverview?: () => void;
  onOpenChat?: () => void;
}

export function CaseIntakeView({
  isSubmitting,
  error,
  onSubmitCase,
  messages = [],
  onOpenOverview,
  onOpenChat,
}: CaseIntakeViewProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const hasExistingEvidence = messages.length > 0;
  const initialEvidenceMessage = messages.find((m) => m.role === "user");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = description.trim();
    if (!trimmed || isSubmitting) return;
    onSubmitCase({
      title: title.trim() || undefined,
      description: trimmed,
    });
    setDescription("");
  };

  return (
    <div
      id="workspace-intake-panel"
      role="region"
      aria-label="New Case Intake"
      className="flex min-h-0 flex-1 flex-col overflow-y-auto bg-canvas"
    >
      <div className="mx-auto w-full max-w-3xl space-y-6 px-4 py-8 sm:px-8">
        {/* Editorial Header */}
        <header className="border-b border-line pb-4 space-y-1">
          <span className="font-mono text-[10px] font-bold tracking-widest text-ink-muted uppercase">
            {hasExistingEvidence ? "CASE INTAKE RECORD" : "NEW INVESTIGATION"}
          </span>
          <h1 className="text-xl font-bold tracking-tight text-ink sm:text-2xl">
            {hasExistingEvidence ? "บันทึกข้อมูลสำนวนคดี" : "เริ่มวิเคราะห์คดีใหม่"}
          </h1>
          <p className="text-xs leading-relaxed text-ink-secondary sm:text-sm">
            {hasExistingEvidence
              ? "สำนวนคดีนี้มีข้อมูลนำเข้าเริ่มต้นแล้ว คุณสามารถดูภาพรวมคดี สนทนาสอบถาม หรือเพิ่มรายละเอียดหลักฐานเพิ่มเติมได้ที่นี่"
              : "นำรายละเอียดจากสำนวนหรือข้อมูลเหตุการณ์ที่มีอยู่ในขณะนี้ มาให้ CyberCase ช่วยจัดภาพรวม อธิบายพฤติกรรมทางเทคนิค และเชื่อมโยงกับ MITRE ATT&CK"}
          </p>
        </header>

        {/* Existing Case Notice (if case already has evidence) */}
        {hasExistingEvidence && (
          <div className="rounded-lg border border-line bg-surface p-4 space-y-3">
            <div className="flex items-center justify-between gap-2 border-b border-line/60 pb-2.5">
              <span className="font-mono text-[10.5px] font-bold uppercase tracking-wider text-ink-secondary">
                Submitted Case Narrative · รายละเอียดเริ่มต้น
              </span>
              <span className="rounded bg-surface-nested px-2 py-0.5 font-mono text-[10px] font-bold text-ink-muted">
                ACTIVE CASE
              </span>
            </div>
            {initialEvidenceMessage && (
              <p className="text-xs leading-relaxed text-ink whitespace-pre-wrap line-clamp-6 bg-canvas/60 rounded p-3 border border-line/40">
                {initialEvidenceMessage.content}
              </p>
            )}
            <div className="flex flex-wrap items-center gap-2 pt-1">
              {onOpenOverview && (
                <button
                  type="button"
                  onClick={onOpenOverview}
                  className="inline-flex items-center gap-1.5 rounded bg-primary px-3.5 py-1.5 text-xs font-bold text-ivory hover:bg-charcoal-hover active:bg-charcoal-pressed transition-colors"
                >
                  <Icon name="overview" className="h-3.5 w-3.5" />
                  <span>View Case Overview · ดูภาพรวมคดี</span>
                </button>
              )}
              {onOpenChat && (
                <button
                  type="button"
                  onClick={onOpenChat}
                  className="inline-flex items-center gap-1.5 rounded border border-line bg-surface px-3.5 py-1.5 text-xs font-bold text-ink hover:bg-surface-hover transition-colors"
                >
                  <Icon name="chat" className="h-3.5 w-3.5" />
                  <span>Ask in Chat · ถาม-ตอบในแชท</span>
                </button>
              )}
            </div>
          </div>
        )}

        {error && (
          <div
            role="alert"
            className="rounded-lg border border-accent/30 bg-accent-soft p-4 text-xs text-accent space-y-1"
          >
            <p className="font-bold">ไม่สามารถวิเคราะห์คดีได้ในขณะนี้</p>
            <p className="text-ink-secondary">
              ข้อมูลที่กรอกไว้ยังคงอยู่: {error}
            </p>
          </div>
        )}

        {isSubmitting && (
          <div className="rounded border border-line bg-surface p-4 text-xs text-ink space-y-1">
            <div className="flex items-center gap-2 font-bold text-ink">
              <span className="h-2 w-2 rounded-full bg-primary motion-safe:animate-pulse" />
              <span>กำลังวิเคราะห์ข้อมูลคดี...</span>
            </div>
            <p className="text-ink-secondary pl-4">
              กำลังจัดภาพรวมเหตุการณ์และค้นหาข้อมูล MITRE ATT&amp;CK ที่เกี่ยวข้อง
            </p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Optional Title (Only shown for new case) */}
          {!hasExistingEvidence && (
            <div className="space-y-1.5">
              <div className="flex items-baseline justify-between gap-2">
                <label
                  htmlFor="case-title-input"
                  className="block text-xs font-bold text-ink"
                >
                  ชื่อคดี <span className="font-normal text-ink-muted">· ไม่บังคับ</span>
                </label>
                <span className="font-mono text-[10px] font-bold uppercase text-ink-muted">
                  OPTIONAL
                </span>
              </div>
              <input
                id="case-title-input"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="เช่น การเข้าถึงระบบบริษัทโดยไม่ได้รับอนุญาต"
                disabled={isSubmitting}
                className="w-full rounded border border-line bg-surface px-3.5 py-2 text-sm text-ink placeholder:text-ink-muted outline-none transition-colors focus:border-primary focus-visible:ring-1 focus-visible:ring-primary disabled:bg-surface-nested"
              />
            </div>
          )}

          {/* Case Description — Primary Control */}
          <div className="space-y-2">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <label
                htmlFor="case-description-input"
                className="block text-xs font-bold uppercase tracking-wider text-ink"
              >
                {hasExistingEvidence ? "เพิ่มรายละเอียดหรือพยานหลักฐาน" : "รายละเอียดคดี"}{" "}
                <span className="text-red-700">*</span>
              </label>
              <span className="font-mono text-[10px] font-bold uppercase text-red-700">
                REQUIRED
              </span>
            </div>
            <p className="text-xs text-ink-secondary leading-relaxed">
              {hasExistingEvidence
                ? "หากมีพยานหลักฐานเพิ่มเติม ข้อมูลจากไฟล์ล็อก หรือข้อสังเกตใหม่ สามารถกรอกเพื่อผนวกเข้ากับสำนวนคดีได้"
                : "วางรายละเอียดจากสำนวน หรืออธิบายเหตุการณ์ที่ต้องการวิเคราะห์ สามารถใช้ข้อความและศัพท์ทางเทคนิคจากเอกสารต้นฉบับได้ CyberCase จะช่วยอธิบายให้อยู่ในรูปแบบที่อ่านง่าย"}
            </p>
            <textarea
              id="case-description-input"
              rows={hasExistingEvidence ? 6 : 11}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder={
                hasExistingEvidence
                  ? "เพิ่มข้อมูลพยานหลักฐานหรือลำดับเหตุการณ์ใหม่ที่ตรวจพบ..."
                  : "เช่น เมื่อวันที่ 12 พฤษภาคม 2566 ตรวจพบการเข้าถึงเซิร์ฟเวอร์ IIS โดยไม่ได้รับอนุญาต มีการรันสคริปต์ผ่าน PowerShell และสร้าง Scheduled task ชื่อ Updater.exe เพื่อฝังตัวในระบบ..."
              }
              required
              disabled={isSubmitting}
              className="w-full min-h-[200px] rounded border border-line bg-surface p-3.5 text-sm leading-relaxed text-ink placeholder:text-ink-muted outline-none transition-colors focus:border-primary focus-visible:ring-1 focus-visible:ring-primary disabled:bg-surface-nested"
            />

            {/* Input Guidance */}
            <div className="rounded border border-line/60 bg-surface-nested/30 p-3 text-xs text-ink-secondary space-y-1.5">
              <p className="font-bold text-ink text-[11.5px]">ข้อมูลที่ใส่ได้ เช่น</p>
              <ul className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-1 text-[11px] text-ink-secondary list-disc list-inside">
                <li>ลำดับเหตุการณ์ที่ปรากฏในสำนวน</li>
                <li>ระบบ เครื่อง หรือบัญชีที่เกี่ยวข้อง</li>
                <li>พฤติกรรมทางเทคนิคที่ตรวจพบ</li>
                <li>ผลกระทบที่มีการรายงาน</li>
                <li className="sm:col-span-2">สิ่งที่ผู้สอบสวนยังไม่แน่ใจ</li>
              </ul>
            </div>
          </div>

          {/* Optional Document Upload Area (Disabled) */}
          <div className="space-y-1.5">
            <div className="flex items-baseline justify-between gap-2">
              <label className="block text-xs font-bold text-ink">
                เอกสารเพิ่มเติม <span className="font-normal text-ink-muted">· ไม่บังคับ</span>
              </label>
              <span className="font-mono text-[10px] font-bold uppercase text-ink-muted">
                OPTIONAL
              </span>
            </div>
            <div className="flex items-start gap-3 rounded border border-dashed border-line bg-surface-nested/30 p-3.5 text-xs text-ink-muted">
              <Icon name="report" className="h-4 w-4 shrink-0 mt-0.5 text-ink-muted" />
              <div className="space-y-0.5 min-w-0 flex-1">
                <p className="font-medium text-ink-secondary">
                  Document upload is not available yet.
                </p>
                <p className="text-[11px] text-ink-muted">
                  ขณะนี้สามารถคัดลอกข้อความสำคัญจากเอกสารมาใส่ในรายละเอียดคดีด้านบนได้
                </p>
              </div>
            </div>
          </div>

          {/* Primary Action Button */}
          <div className="flex flex-wrap items-center justify-between gap-3 border-t border-line pt-4">
            <p className="text-[11px] text-ink-muted">
              Evidence is grounded directly into the Case Overview dossier.
            </p>
            <button
              type="submit"
              disabled={!description.trim() || isSubmitting}
              className="inline-flex min-h-10 items-center gap-2 rounded bg-primary px-6 py-2.5 text-xs font-bold text-ivory transition-colors hover:bg-charcoal-hover active:bg-charcoal-pressed focus-visible:ring-2 focus-visible:ring-primary disabled:cursor-not-allowed disabled:bg-control-disabled disabled:text-ink-disabled shadow-xs"
            >
              {isSubmitting ? (
                <>
                  <span
                    className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-ivory/30 border-t-ivory"
                    aria-hidden="true"
                  />
                  <span>กำลังวิเคราะห์ข้อมูลคดี...</span>
                </>
              ) : (
                <span>{hasExistingEvidence ? "วิเคราะห์ข้อมูลเพิ่มเติม · Analyze updates" : "วิเคราะห์คดี · Analyze case"}</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
