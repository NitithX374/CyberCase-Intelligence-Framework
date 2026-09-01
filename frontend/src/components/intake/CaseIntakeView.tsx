"use client";

import { useState, type FormEvent } from "react";
import { Icon } from "@/components/common/icons";
import { StatusPill } from "@/components/common/StatusPill";
import type {
  CaseIntakeSubmission,
  PersistedChatMessage,
} from "@/lib/api";
import { DocumentIngestionPreview } from "@/components/intake/DocumentIngestionPreview";
import { CaseNarrativeSourceNotice } from "@/components/intake/CaseNarrativeSourceNotice";
import {
  bindCaseNarrativeDocumentSource,
  type CaseNarrativeDraft,
} from "@/lib/case-narrative-document";
import { getCaseEvidenceKind, isCaseEvidenceMessage } from "@/lib/case-evidence";

interface CaseIntakeViewProps {
  caseKey?: string;
  threadId?: string | null;
  isSubmitting: boolean;
  error?: string | null;
  onSubmitCase: (data: CaseIntakeSubmission) => void;
  messages?: PersistedChatMessage[];
  onOpenOverview?: () => void;
  onOpenChat?: () => void;
  onOpenMaterials?: () => void;
}

export function CaseIntakeView({
  caseKey,
  threadId,
  isSubmitting,
  onSubmitCase,
  messages = [],
  onOpenOverview,
  onOpenChat,
  onOpenMaterials,
}: CaseIntakeViewProps) {
  const effectiveCaseKey =
    (caseKey ?? threadId ?? messages[0]?.thread_id ?? "draft").trim() || "draft";
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [documentDraft, setDocumentDraft] = useState<CaseNarrativeDraft | null>(null);
  const hasExistingEvidence = messages.some(isCaseEvidenceMessage);
  const initialEvidenceMessage =
    messages.find((message) => getCaseEvidenceKind(message) === "initial_case_narrative") ??
    messages.find((message) => message.role === "user");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = description.trim();
    if (!trimmed || isSubmitting) return;
    onSubmitCase({
      title: title.trim() || undefined,
      description: trimmed,
      documentSources: documentDraft
        ? [bindCaseNarrativeDocumentSource(documentDraft, trimmed)]
        : undefined,
    });
  };

  const useDocumentNarrative = (draft: CaseNarrativeDraft) => {
    setDescription(draft.text);
    setDocumentDraft(draft);
    requestAnimationFrame(() => document.getElementById("case-description-input")?.focus());
  };

  return (
    <div
      id="workspace-intake-panel"
      role="region"
      aria-label="New Case Intake"
      className="flex min-h-0 flex-1 flex-col overflow-y-auto bg-canvas"
    >
      <div className="mx-auto w-full max-w-5xl space-y-7 px-4 py-6 sm:px-7 sm:py-8 lg:px-9">
        <header className="flex flex-wrap items-start justify-between gap-5 border-b border-line pb-5">
          <div className="min-w-0 max-w-2xl">
            <p className="section-eyebrow">
              {hasExistingEvidence ? "CASE INTAKE RECORD" : "NEW INVESTIGATION"}
            </p>
            <h1 className="mt-1 text-2xl font-extrabold tracking-[-0.035em] text-ink sm:text-3xl">
              {hasExistingEvidence ? "บันทึกข้อมูลสำนวนคดี" : "เริ่มวิเคราะห์คดีใหม่"}
            </h1>
            <p className="mt-2 text-xs leading-relaxed text-ink-secondary sm:text-sm">
              {hasExistingEvidence
                ? "สำนวนคดีนี้มีข้อมูลนำเข้าเริ่มต้นแล้ว คุณสามารถดูภาพรวมคดี สนทนาสอบถาม หรือเพิ่มรายละเอียดหลักฐานเพิ่มเติมได้ในหน้าแชท"
                : "เริ่มจากข้อมูลที่ผู้ใช้ส่งมา CyberCase จะจัดทำสรุป ข้อค้นพบ และประเด็นที่ยังต้องตรวจสอบ โดยจะเสริมบริบททางเทคนิคเฉพาะเมื่อเกี่ยวข้อง"}
            </p>
          </div>
          <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.1em] text-ink-muted">
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-primary text-ivory">1</span>
            <span>Material → Analysis</span>
          </div>
        </header>

        {hasExistingEvidence ? (
          <ExistingCaseRecord
            message={initialEvidenceMessage}
            onOpenOverview={onOpenOverview}
            onOpenChat={onOpenChat}
            onOpenMaterials={onOpenMaterials}
          />
        ) : (
          <>
            {isSubmitting && (
              <div className="flex items-start gap-3 rounded-xl border border-evidence/25 bg-evidence/5 p-4 text-xs text-ink" role="status">
                <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-evidence motion-safe:animate-pulse motion-reduce:animate-none" />
                <div>
                  <p className="font-bold">กำลังวิเคราะห์ข้อมูลคดี...</p>
                  <p className="mt-1 text-ink-secondary">กำลังจัดทำสรุประดับคดี ข้อค้นพบ และประเด็นที่ยังต้องตรวจสอบ</p>
                </div>
              </div>
            )}

            <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_15rem]">
              <form onSubmit={handleSubmit} className="workspace-card space-y-6 p-5 sm:p-7">
                <div>
                  <StatusPill tone="evidence">Primary case material</StatusPill>
                  <h2 className="mt-2 text-lg font-extrabold tracking-tight text-ink">Describe what happened</h2>
                  <p className="mt-1 text-xs leading-relaxed text-ink-secondary">
                    ส่งรายละเอียดตามที่ปรากฏในสำนวนหรือเอกสารต้นฉบับ ระบบจะใช้ข้อความนี้เป็นฐานของ Case Overview
                  </p>
                </div>

                <div className="space-y-1.5">
                  <div className="flex items-baseline justify-between gap-2">
                    <label htmlFor="case-title-input" className="text-xs font-bold text-ink">
                      ชื่อคดี <span className="font-normal text-ink-muted">· ไม่บังคับ</span>
                    </label>
                    <span className="section-eyebrow">Optional</span>
                  </div>
                  <input
                    id="case-title-input"
                    type="text"
                    value={title}
                    onChange={(event) => setTitle(event.target.value)}
                    placeholder="เช่น การเข้าถึงระบบบริษัทโดยไม่ได้รับอนุญาต"
                    disabled={isSubmitting}
                    className="w-full rounded-lg border border-line bg-canvas px-3.5 py-2.5 text-sm text-ink placeholder:text-ink-muted outline-none transition-colors focus:border-primary focus-visible:ring-1 focus-visible:ring-primary disabled:bg-surface-nested"
                  />
                </div>

                <div className="space-y-2">
                  <div className="flex flex-wrap items-baseline justify-between gap-2">
                    <label htmlFor="case-description-input" className="text-xs font-bold text-ink">
                      รายละเอียดคดี <span className="text-accent">*</span>
                    </label>
                    <span className="section-eyebrow text-accent">Required</span>
                  </div>
                  <textarea
                    id="case-description-input"
                    rows={13}
                    value={description}
                    onChange={(event) => setDescription(event.target.value)}
                    placeholder="เช่น เมื่อวันที่ 12 พฤษภาคม 2566 ตรวจพบการเข้าถึงเซิร์ฟเวอร์ IIS โดยไม่ได้รับอนุญาต มีการรันสคริปต์ผ่าน PowerShell และสร้าง Scheduled task ชื่อ Updater.exe เพื่อฝังตัวในระบบ..."
                    required
                    disabled={isSubmitting}
                    className="min-h-[250px] w-full resize-y rounded-lg border border-line bg-canvas p-4 text-sm leading-relaxed text-ink placeholder:text-ink-muted outline-none transition-colors focus:border-primary focus-visible:ring-1 focus-visible:ring-primary disabled:bg-surface-nested"
                  />
                  {documentDraft && (
                    <CaseNarrativeSourceNotice
                      source={documentDraft.source}
                      onRemove={() => setDocumentDraft(null)}
                    />
                  )}
                </div>

                <div className="flex flex-wrap items-center justify-between gap-3 border-t border-line pt-4">
                  <p className="max-w-sm text-[11px] leading-relaxed text-ink-muted">
                    ผู้ใช้เป็นผู้กำหนดว่าข้อมูลใดควรเป็นส่วนหนึ่งของสำนวน
                  </p>
                  <button
                    type="submit"
                    disabled={!description.trim() || isSubmitting}
                    className="btn-primary inline-flex min-h-10 items-center gap-2 rounded-lg px-5"
                  >
                    {isSubmitting && <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-ivory/30 border-t-ivory" />}
                    <span>{isSubmitting ? "กำลังวิเคราะห์ข้อมูลคดี..." : "วิเคราะห์คดี · Analyze case"}</span>
                  </button>
                </div>
              </form>

              <IntakeGuidance />
            </div>

            <DocumentIngestionPreview
              caseKey={effectiveCaseKey}
              onUseAsNarrative={useDocumentNarrative}
            />
          </>
        )}

        {hasExistingEvidence && <DocumentIngestionPreview caseKey={effectiveCaseKey} />}
      </div>
    </div>
  );
}

function IntakeGuidance() {
  return (
    <aside className="workspace-card p-4 sm:p-5">
      <p className="section-eyebrow">WHAT TO INCLUDE</p>
      <h2 className="mt-1 text-sm font-extrabold tracking-tight text-ink">Start with the record</h2>
      <p className="mt-2 text-xs leading-relaxed text-ink-secondary">
        ข้อมูลไม่จำเป็นต้องสมบูรณ์ ระบบจะแยกสิ่งที่รายงานออกจากข้อสรุปและสิ่งที่ยังไม่แน่นอน
      </p>
      <ul className="mt-4 space-y-2 border-t border-line pt-4 text-[11px] leading-relaxed text-ink-secondary">
        <li>ลำดับเหตุการณ์หรือช่วงเวลาที่ทราบ</li>
        <li>บุคคล ระบบ เครื่อง หรือบัญชีที่เกี่ยวข้อง</li>
        <li>พฤติกรรมหรือผลกระทบที่มีการรายงาน</li>
        <li>สิ่งที่ผู้สอบสวนยังไม่แน่ใจ</li>
      </ul>
    </aside>
  );
}

function ExistingCaseRecord({
  message,
  onOpenOverview,
  onOpenChat,
  onOpenMaterials,
}: {
  message?: PersistedChatMessage;
  onOpenOverview?: () => void;
  onOpenChat?: () => void;
  onOpenMaterials?: () => void;
}) {
  return (
    <div className="space-y-5">
      <section className="workspace-card p-5 sm:p-7">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line pb-4">
          <div>
            <p className="section-eyebrow">SUBMITTED CASE NARRATIVE</p>
            <h2 className="mt-1 text-lg font-extrabold tracking-tight text-ink">ข้อมูลตั้งต้นของคดี</h2>
          </div>
          <StatusPill tone="positive">Active case</StatusPill>
        </div>
        {message ? (
          <div className="pt-5">
            <p className="whitespace-pre-wrap border-l-2 border-evidence/40 pl-4 text-sm leading-relaxed text-ink select-text">
              {message.content}
            </p>
            <p className="mt-3 text-[11px] text-ink-muted">
              บันทึกเมื่อ: {new Date(message.created_at).toLocaleString("th-TH")}
            </p>
          </div>
        ) : (
          <p className="pt-5 text-xs italic text-ink-muted">ไม่มีบันทึกข้อความเริ่มต้น</p>
        )}
        <div className="mt-5 flex flex-wrap items-center gap-2 border-t border-line pt-4">
          {onOpenOverview && (
            <button type="button" onClick={onOpenOverview} className="btn-primary inline-flex items-center gap-1.5 rounded-lg">
              <Icon name="overview" className="h-3.5 w-3.5" />
              View Case Overview · ดูภาพรวมคดี
            </button>
          )}
          {onOpenChat && (
            <button type="button" onClick={onOpenChat} className="btn-secondary inline-flex items-center gap-1.5 rounded-lg">
              <Icon name="chat" className="h-3.5 w-3.5" />
              Ask in Chat · ถาม-ตอบในแชท
            </button>
          )}
          {onOpenMaterials && (
            <button type="button" onClick={onOpenMaterials} className="btn-secondary inline-flex items-center gap-1.5 rounded-lg">
              <Icon name="materials" className="h-3.5 w-3.5" />
              Case Materials · รายการข้อมูล
            </button>
          )}
        </div>
      </section>
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-line bg-surface-nested/35 p-4 text-xs text-ink-secondary">
        <p>ต้องการเพิ่มข้อมูลใหม่หรือไม่? เลือก “Add case information” ในหน้าแชทเพื่อผนวกข้อมูลเข้ากับสำนวน</p>
        {onOpenChat && (
          <button type="button" onClick={onOpenChat} className="font-bold text-ink hover:text-accent hover:underline">
            Add case information in Chat →
          </button>
        )}
      </div>
    </div>
  );
}
