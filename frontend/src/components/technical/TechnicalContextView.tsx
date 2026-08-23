"use client";

import { useState } from "react";
import type { PersistedChatMessage } from "@/lib/api";
import {
  buildTechnicalContext,
  type TechnicalContextCard,
} from "@/lib/technical-context";
import { type SourceMessageRef } from "@/lib/case-overview";
import { SourceEvidencePopover } from "@/components/overview/SourceEvidencePopover";
import { Icon } from "@/components/common/icons";

interface TechnicalContextViewProps {
  messages: PersistedChatMessage[];
  onOpenIntake?: () => void;
  onNavigateToSource?: (messageId: string) => void;
}

function TechnicalItem({
  item,
  onSelectSource,
  activeSourceKey,
}: {
  item: TechnicalContextCard;
  onSelectSource: (
    source: SourceMessageRef,
    element: HTMLElement,
    key: string,
  ) => void;
  activeSourceKey: string | null;
}) {
  const [isDefinitionOpen, setIsDefinitionOpen] = useState(false);

  return (
    <article
      id={`mitre-${item.techniqueId}`}
      className="py-6 first:pt-3 last:pb-3 space-y-3.5"
    >
      {/* Technique Heading & Tactic */}
      <div>
        <div className="flex flex-wrap items-baseline gap-2.5">
          <span className="font-mono text-xs font-bold text-[#6654A3]">
            {item.techniqueId}
          </span>
          <h2 className="text-sm font-bold text-ink">
            {item.techniqueName}
          </h2>
        </div>
        {item.tactic && (
          <p className="text-xs text-ink-muted mt-0.5 font-medium">
            {item.tactic}
          </p>
        )}
      </div>

      {/* ความหมายโดยย่อ */}
      {item.shortPlainMeaning && (
        <div className="space-y-1">
          <h3 className="text-xs font-bold text-ink">
            ความหมายโดยย่อ
          </h3>
          <p className="text-xs leading-relaxed text-ink-secondary">
            {item.shortPlainMeaning}
          </p>
        </div>
      )}

      {/* เหตุผลที่เกี่ยวข้องกับคดี */}
      <div className="space-y-1">
        <h3 className="text-xs font-bold text-ink">
          เหตุผลที่เกี่ยวข้องกับคดี
        </h3>
        <p className="text-xs leading-relaxed text-ink">
          {item.whyRelevantHere}
        </p>
      </div>

      {/* แหล่งข้อมูล */}
      {item.caseBasisSources.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 pt-0.5 text-xs">
          <span className="text-[11px] text-ink-muted">แหล่งข้อมูล:</span>
          {item.caseBasisSources.map((source) => {
            const buttonKey = `${item.techniqueId}-source-${source.id}`;
            const isActive = activeSourceKey === buttonKey;
            return (
              <button
                key={source.id}
                type="button"
                onClick={(e) => onSelectSource(source, e.currentTarget, buttonKey)}
                aria-haspopup="dialog"
                className={`inline-flex items-center gap-1 text-xs transition-colors rounded px-1.5 py-0.5 font-medium ${
                  isActive
                    ? "bg-[#356C8A] text-white"
                    : "text-ink hover:text-primary hover:underline bg-surface-nested"
                }`}
              >
                <span>Source — {source.label}</span>
                <span aria-hidden="true" className="text-[10px]">↗</span>
              </button>
            );
          })}
        </div>
      )}

      {/* คำอธิบายทางเทคนิค (Expandable) */}
      {item.fullTechnicalDefinition &&
        item.fullTechnicalDefinition !== item.shortPlainMeaning && (
          <div className="pt-0.5">
            <button
              type="button"
              onClick={() => setIsDefinitionOpen(!isDefinitionOpen)}
              className="text-[11.5px] font-medium text-ink-muted hover:text-ink inline-flex items-center gap-1 transition-colors"
            >
              <span>คำอธิบายทางเทคนิค</span>
              <span aria-hidden="true" className="text-[10px]">
                {isDefinitionOpen ? "▴" : "▾"}
              </span>
            </button>
            {isDefinitionOpen && (
              <p className="mt-2 text-xs leading-relaxed text-ink-secondary bg-surface-nested/60 p-3 rounded border border-line/40 select-text">
                {item.fullTechnicalDefinition}
              </p>
            )}
          </div>
        )}
    </article>
  );
}

export function TechnicalContextView({
  messages,
  onOpenIntake,
  onNavigateToSource,
}: TechnicalContextViewProps) {
  const contextData = buildTechnicalContext(messages);

  const [activePopover, setActivePopover] = useState<{
    source: SourceMessageRef;
    element: HTMLElement;
  } | null>(null);
  const [activeSourceKey, setActiveSourceKey] = useState<string | null>(null);

  const handleSelectSource = (
    source: SourceMessageRef,
    element: HTMLElement,
    key: string,
  ) => {
    if (activeSourceKey === key) {
      setActivePopover(null);
      setActiveSourceKey(null);
    } else {
      setActivePopover({ source, element });
      setActiveSourceKey(key);
    }
  };

  const handleClosePopover = () => {
    setActivePopover(null);
    setActiveSourceKey(null);
  };

  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-y-auto bg-canvas">
      <div className="mx-auto w-full max-w-3xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8 space-y-6">
        {/* Page Header */}
        <header className="space-y-2 border-b border-line pb-5">
          <h1 className="text-lg sm:text-xl font-bold tracking-tight text-ink">
            MITRE ATT&amp;CK Context
          </h1>
          <p className="text-xs font-semibold text-ink-secondary">
            External technical reference · not case evidence
          </p>
          <p className="text-xs text-ink-muted leading-relaxed max-w-2xl">
            MITRE ATT&amp;CK is used here to help explain technical behavior described in the case.
          </p>
          <p className="text-[11.5px] text-ink-muted italic pt-1">
            การเชื่อมโยงต่อไปนี้เป็นข้อเสนอเชิงวิเคราะห์ ไม่ใช่ข้อเท็จจริงจากคดี
          </p>
        </header>

        {/* Empty State */}
        {!contextData.hasContext ? (
          <div className="rounded-xl border border-line bg-surface p-12 text-center shadow-xs">
            <span className="mx-auto inline-flex h-12 w-12 items-center justify-center rounded-xl bg-surface-nested text-ink-secondary mb-3">
              <Icon name="technical" className="h-6 w-6" />
            </span>
            <h2 className="text-sm font-bold text-ink">
              No relevant MITRE ATT&amp;CK context is currently available.
            </h2>
            <p className="mt-1 text-xs text-ink-muted max-w-md mx-auto leading-relaxed">
              ยังไม่มีข้อมูลบริบททางเทคนิค MITRE ATT&amp;CK ในขณะนี้ กรุณาส่งรายละเอียดเหตุการณ์ในหน้า Case Intake เพื่อให้ระบบทำการสืบค้นและเชื่อมโยง
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
          /* Flattened Techniques List separated by dividers */
          <div className="divide-y divide-line/60">
            {contextData.techniques.map((item) => (
              <TechnicalItem
                key={item.techniqueId}
                item={item}
                onSelectSource={handleSelectSource}
                activeSourceKey={activeSourceKey}
              />
            ))}
          </div>
        )}
      </div>

      {/* Anchored Source Popover */}
      {activePopover && (
        <SourceEvidencePopover
          sourceRef={activePopover.source}
          anchorElement={activePopover.element}
          onClose={handleClosePopover}
          onNavigateToSource={onNavigateToSource}
        />
      )}
    </div>
  );
}
