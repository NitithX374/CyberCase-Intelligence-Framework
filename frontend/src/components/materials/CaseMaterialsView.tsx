"use client";

import { useState } from "react";
import type { PersistedChatMessage } from "@/lib/api";
import { buildCaseMaterials, type CaseMaterialItem } from "@/lib/case-materials";
import { Icon } from "@/components/common/icons";

interface CaseMaterialsViewProps {
  messages: PersistedChatMessage[];
  onOpenChat?: () => void;
  onOpenIntake?: () => void;
}

function MaterialRow({
  item,
  onOpenChat,
}: {
  item: CaseMaterialItem;
  onOpenChat?: () => void;
}) {
  const isLong = item.content.length > 350;
  const [isExpanded, setIsExpanded] = useState(!isLong);

  return (
    <article
      id={`material-${item.id}`}
      aria-label={`${item.typeLabel} (Item ${item.itemNumber})`}
      className="group relative rounded-xl border border-line bg-surface p-5 sm:p-6 transition-all duration-150 hover:border-line-strong hover:shadow-xs shadow-[0_1px_2px_rgba(39,39,39,0.03)]"
    >
      <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-2 border-b border-line/60 pb-3">
        <div className="flex items-center gap-3">
          <span className="font-mono text-xs font-bold text-ink-muted bg-surface-nested px-2 py-0.5 rounded">
            {item.itemNumber}
          </span>
          <h3 className="text-xs sm:text-sm font-bold text-ink tracking-tight">
            {item.typeLabel}
          </h3>
        </div>
        <div className="flex items-center gap-3 text-[11px] text-ink-muted">
          <span>Submitted {item.timestampDisplay}</span>
          {onOpenChat && (
            <button
              type="button"
              onClick={onOpenChat}
              className="font-medium text-primary hover:underline inline-flex items-center gap-0.5 ml-2"
              title="View in conversation"
            >
              <span>View in Chat</span>
              <span aria-hidden="true">↗</span>
            </button>
          )}
        </div>
      </div>

      <div className="pt-4">
        <div className="rounded-lg border border-line/50 bg-canvas/60 p-4">
          <p className="whitespace-pre-wrap text-xs sm:text-[13px] leading-relaxed text-ink font-normal select-text">
            {isExpanded || !isLong
              ? item.content
              : `${item.content.slice(0, 350)}…`}
          </p>
          {isLong && (
            <button
              type="button"
              onClick={() => setIsExpanded(!isExpanded)}
              className="mt-3 text-xs font-bold text-primary hover:underline inline-flex items-center gap-1"
            >
              <span>{isExpanded ? "Collapse · ย่อข้อความ" : "Show full text · แสดงข้อความฉบับเต็ม"}</span>
              <Icon
                name="chevron"
                className={`h-3 w-3 transform transition-transform duration-150 ${
                  isExpanded ? "rotate-180" : ""
                }`}
              />
            </button>
          )}
        </div>
      </div>
    </article>
  );
}

export function CaseMaterialsView({
  messages,
  onOpenChat,
  onOpenIntake,
}: CaseMaterialsViewProps) {
  const materialsData = buildCaseMaterials(messages);

  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-y-auto bg-canvas">
      <div className="mx-auto w-full max-w-4xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8 space-y-6">
        {/* Page Header */}
        <header className="space-y-2 border-b border-line pb-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <span className="inline-flex h-6 w-6 items-center justify-center rounded bg-[#356C8A]/10 text-[#356C8A]">
                  <Icon name="materials" className="h-3.5 w-3.5" />
                </span>
                <span className="font-mono text-[10px] font-extrabold uppercase tracking-widest text-[#356C8A]">
                  CASE MATERIALS · ข้อมูลสำนวนคดี
                </span>
              </div>
              <h1 className="mt-1 text-lg sm:text-xl font-bold tracking-tight text-ink">
                Submitted Case Information
              </h1>
            </div>
            {materialsData.hasMaterials && (
              <span className="rounded-full border border-line bg-surface px-3 py-1 text-xs font-semibold text-ink-secondary shadow-xs">
                {materialsData.totalCount} material{materialsData.totalCount > 1 ? "s" : ""}
              </span>
            )}
          </div>
          <p className="text-xs sm:text-[13px] text-ink-secondary leading-relaxed max-w-2xl">
            พยานหลักฐานและข้อเท็จจริงที่ผู้ใช้ส่งเข้าสู่ระบบเพื่อใช้เป็นฐานข้อมูลในการวิเคราะห์เหตุการณ์ (Authoritative user-authored incident evidence)
          </p>
        </header>

        {/* Empty State */}
        {!materialsData.hasMaterials ? (
          <div className="rounded-xl border border-line bg-surface p-12 text-center shadow-xs">
            <span className="mx-auto inline-flex h-12 w-12 items-center justify-center rounded-xl bg-surface-nested text-ink-secondary mb-3">
              <Icon name="materials" className="h-6 w-6" />
            </span>
            <h2 className="text-sm font-bold text-ink">No case information has been submitted yet.</h2>
            <p className="mt-1 text-xs text-ink-muted max-w-md mx-auto leading-relaxed">
              ยังไม่มีข้อมูลสำนวนคดีที่ส่งเข้าสู่ระบบ กรุณาเริ่มบันทึกข้อมูลเหตุการณ์ที่หน้า Case Intake เพื่อให้ระบบเริ่มการวิเคราะห์
            </p>
            {onOpenIntake && (
              <button
                type="button"
                onClick={onOpenIntake}
                className="mt-5 inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-xs font-bold text-ivory hover:bg-charcoal-hover transition-colors"
              >
                <Icon name="intake" className="h-3.5 w-3.5" />
                <span>Go to Case Intake · เปิดสำนวนคดี</span>
              </button>
            )}
          </div>
        ) : (
          /* Materials Document List */
          <div className="space-y-4">
            {materialsData.items.map((item) => (
              <MaterialRow key={item.id} item={item} onOpenChat={onOpenChat} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
