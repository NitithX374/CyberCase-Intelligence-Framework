"use client";

import { useState } from "react";
import type { PersistedChatMessage } from "@/lib/api";
import { Icon } from "@/components/common/icons";
import { StatusPill } from "@/components/common/StatusPill";
import { buildCaseMaterials, type CaseMaterialItem } from "@/lib/case-materials";

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
    <article id={`material-${item.id}`} className="border-b border-line py-5 first:pt-1 last:border-b-0">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex min-w-0 items-center gap-3">
          <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-surface-nested font-mono text-[10px] font-bold text-ink-secondary">
            {item.itemNumber}
          </span>
          <div className="min-w-0">
            <h2 className="truncate text-sm font-extrabold tracking-tight text-ink">{item.typeLabel}</h2>
            <p className="mt-0.5 text-[10px] text-ink-muted">Submitted {item.timestampDisplay}</p>
          </div>
        </div>
        {onOpenChat && (
          <button
            type="button"
            onClick={onOpenChat}
            className="inline-flex items-center gap-1 text-[11px] font-bold text-ink transition-colors hover:text-accent hover:underline"
          >
            View in Chat <span aria-hidden="true">↗</span>
          </button>
        )}
      </div>
      <div className="mt-4 border-l-2 border-evidence/35 pl-4">
        <p className="whitespace-pre-wrap text-sm leading-relaxed text-ink select-text">
          {isExpanded || !isLong ? item.content : `${item.content.slice(0, 350)}…`}
        </p>
        {isLong && (
          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="mt-3 inline-flex items-center gap-1 text-[11px] font-bold text-ink hover:text-accent hover:underline"
          >
            {isExpanded ? "Collapse · ย่อข้อความ" : "Show full text · แสดงข้อความฉบับเต็ม"}
            <Icon name="chevron" className={`h-3 w-3 transition-transform ${isExpanded ? "rotate-180" : ""}`} />
          </button>
        )}
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
      <div className="mx-auto w-full max-w-4xl space-y-7 px-4 py-6 sm:px-7 sm:py-8 lg:px-9">
        <header className="border-b border-line pb-5">
          <p className="section-eyebrow">CASE MATERIALS · ข้อมูลสำนวนคดี</p>
          <div className="mt-1 flex flex-wrap items-center justify-between gap-3">
            <h1 className="text-2xl font-extrabold tracking-[-0.035em] text-ink sm:text-3xl">
              Submitted Case Information
            </h1>
            {materialsData.hasMaterials && <StatusPill>{materialsData.totalCount} material{materialsData.totalCount > 1 ? "s" : ""}</StatusPill>}
          </div>
          <p className="mt-2 max-w-2xl text-xs leading-relaxed text-ink-secondary sm:text-sm">
            พยานหลักฐานและข้อเท็จจริงที่ผู้ใช้ส่งเข้าสู่ระบบเพื่อใช้เป็นฐานข้อมูลในการวิเคราะห์เหตุการณ์
          </p>
        </header>

        {!materialsData.hasMaterials ? (
          <div className="workspace-card p-10 text-center sm:p-12">
            <span className="mx-auto flex h-11 w-11 items-center justify-center rounded-xl bg-surface-nested text-ink-secondary">
              <Icon name="materials" className="h-5 w-5" />
            </span>
            <h2 className="mt-4 text-sm font-extrabold text-ink">No case information has been submitted yet.</h2>
            <p className="mx-auto mt-1 max-w-md text-xs leading-relaxed text-ink-muted">
              ยังไม่มีข้อมูลสำนวนคดีที่ส่งเข้าสู่ระบบ กรุณาเริ่มบันทึกข้อมูลเหตุการณ์ที่หน้า Case Intake เพื่อให้ระบบเริ่มการวิเคราะห์
            </p>
            {onOpenIntake && (
              <button type="button" onClick={onOpenIntake} className="btn-primary mt-5 inline-flex items-center gap-2 rounded-lg">
                <Icon name="intake" className="h-3.5 w-3.5" />
                Go to Case Intake · เปิดสำนวนคดี
              </button>
            )}
          </div>
        ) : (
          <div>{materialsData.items.map((item) => <MaterialRow key={item.id} item={item} onOpenChat={onOpenChat} />)}</div>
        )}
      </div>
    </div>
  );
}
