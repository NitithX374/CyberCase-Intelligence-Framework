"use client";

import { useState } from "react";
import type { PersistedChatMessage } from "@/lib/api";
import { Icon } from "@/components/common/icons";
import { SourceEvidencePopover } from "@/components/overview/SourceEvidencePopover";
import type { SourceMessageRef } from "@/lib/case-overview";
import { buildTechnicalContext, type TechnicalContextCard } from "@/lib/technical-context";

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
  onSelectSource: (source: SourceMessageRef, element: HTMLElement, key: string) => void;
  activeSourceKey: string | null;
}) {
  const [isDefinitionOpen, setIsDefinitionOpen] = useState(false);

  return (
    <article id={`mitre-${item.techniqueId}`} className="space-y-4 py-6 first:pt-2 last:pb-2">
      <div>
        <div className="flex flex-wrap items-baseline gap-2.5">
          <span className="font-mono text-[11px] text-mitre">
            {item.techniqueId}
          </span>
          <h2 className="text-sm font-extrabold text-ink">{item.techniqueName}</h2>
        </div>
        {item.tactic && <p className="mt-1 text-xs font-medium text-ink-muted">{item.tactic}</p>}
      </div>

      {item.shortPlainMeaning && (
        <div className="space-y-1">
          <h3 className="text-[11px] font-bold uppercase tracking-[0.08em] text-ink-muted">ความหมายโดยย่อ</h3>
          <p className="text-xs leading-relaxed text-ink-secondary">{item.shortPlainMeaning}</p>
        </div>
      )}

      <div className="space-y-1">
        <h3 className="text-[11px] font-bold uppercase tracking-[0.08em] text-ink-muted">เหตุผลที่เกี่ยวข้องกับคดี</h3>
        <p className="text-xs leading-relaxed text-ink">{item.whyRelevantHere}</p>
      </div>

      {item.caseBasisSources.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="text-[11px] text-ink-muted">แหล่งข้อมูล:</span>
          {item.caseBasisSources.map((source) => {
            const buttonKey = `${item.techniqueId}-source-${source.id}`;
            const isActive = activeSourceKey === buttonKey;
            return (
              <button
                key={source.id}
                type="button"
                onClick={(event) => onSelectSource(source, event.currentTarget, buttonKey)}
                aria-haspopup="dialog"
                className={`inline-flex max-w-full items-center gap-1 rounded-sm py-1 text-[11px] font-medium underline decoration-current/40 underline-offset-4 transition-colors focus-visible:ring-2 focus-visible:ring-primary ${
                  isActive
                    ? "text-ink decoration-current"
                    : "text-ink-secondary hover:text-ink hover:decoration-current"
                }`}
              >
                Source — {source.label} <span aria-hidden="true">↗</span>
              </button>
            );
          })}
        </div>
      )}

      {item.fullTechnicalDefinition && item.fullTechnicalDefinition !== item.shortPlainMeaning && (
        <details className="group border-t border-line/70 pt-3" open={isDefinitionOpen}>
          <summary
            className="flex cursor-pointer list-none items-center justify-between gap-2 text-[11px] font-bold text-ink-muted outline-none marker:hidden focus-visible:ring-2 focus-visible:ring-primary"
            onClick={(event) => {
              event.preventDefault();
              setIsDefinitionOpen((open) => !open);
            }}
          >
            <span>คำอธิบายทางเทคนิค</span>
            <Icon name="chevron" className="h-3 w-3 transition-transform group-open:rotate-180" />
          </summary>
          {isDefinitionOpen && (
            <p className="mt-2 rounded-lg border border-line bg-canvas/60 p-3 text-xs leading-relaxed text-ink-secondary select-text">
              {item.fullTechnicalDefinition}
            </p>
          )}
        </details>
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

  const handleSelectSource = (source: SourceMessageRef, element: HTMLElement, key: string) => {
    if (activeSourceKey === key) {
      setActivePopover(null);
      setActiveSourceKey(null);
      return;
    }
    setActivePopover({ source, element });
    setActiveSourceKey(key);
  };

  const handleClosePopover = () => {
    setActivePopover(null);
    setActiveSourceKey(null);
  };

  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-y-auto bg-canvas">
      <div className="mx-auto w-full max-w-4xl space-y-7 px-4 py-6 sm:px-7 sm:py-8 lg:px-9">
        <header className="border-b border-line pb-5">
          <p className="section-eyebrow">OPTIONAL TECHNICAL CONTEXT</p>
          <div className="mt-1 flex flex-wrap items-center justify-between gap-3">
            <h1 className="text-2xl font-extrabold tracking-[-0.035em] text-ink sm:text-3xl">MITRE ATT&amp;CK Context</h1>
          </div>
          <p className="mt-2 text-xs font-bold text-ink-secondary">External technical reference · not case evidence</p>
          <p className="mt-1 max-w-2xl text-xs leading-relaxed text-ink-muted">
            MITRE ATT&amp;CK is used here to help explain technical behavior described in the case. การเชื่อมโยงเป็นข้อเสนอเชิงวิเคราะห์ ไม่ใช่ข้อเท็จจริงจากคดี
          </p>
        </header>

        {!contextData.hasContext ? (
          <div className="workspace-card p-10 text-center sm:p-12">
            <span className="mx-auto flex h-11 w-11 items-center justify-center rounded-xl bg-mitre/10 text-mitre">
              <Icon name="technical" className="h-5 w-5" />
            </span>
            <h2 className="mt-4 text-sm font-extrabold text-ink">No relevant MITRE ATT&amp;CK context is currently available.</h2>
            <p className="mx-auto mt-1 max-w-md text-xs leading-relaxed text-ink-muted">
              ยังไม่มีข้อมูลบริบททางเทคนิค MITRE ATT&amp;CK ในขณะนี้ กรุณาส่งรายละเอียดเหตุการณ์ในหน้า Case Intake เพื่อให้ระบบทำการสืบค้นและเชื่อมโยง
            </p>
            {onOpenIntake && (
              <button type="button" onClick={onOpenIntake} className="btn-primary mt-5 inline-flex items-center gap-2 rounded-lg">
                <Icon name="intake" className="h-3.5 w-3.5" />
                Go to Case Intake · เปิดสำนวนคดี
              </button>
            )}
          </div>
        ) : (
          <section className="workspace-card px-4 sm:px-6">
            <div className="divide-y divide-line/70">
              {contextData.techniques.map((item) => (
                <TechnicalItem
                  key={item.techniqueId}
                  item={item}
                  onSelectSource={handleSelectSource}
                  activeSourceKey={activeSourceKey}
                />
              ))}
            </div>
          </section>
        )}
      </div>

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
