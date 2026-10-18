"use client";

import { useState } from "react";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { Icon } from "@/components/icons";
import type { LegalReference } from "./legalReference";
import { ProvisionItem } from "./ProvisionItem";

export function LegalProvisions({
  reference,
  onDecline,
}: {
  reference: LegalReference;
  onDecline: () => void;
}) {
  const [accepted, setAccepted] = useState(false);

  return (
    <>
      <section
        id="workspace-legal-panel"
        aria-label="Legal references"
        className="flex shrink-0 flex-col bg-surface"
      >
        <div className="mx-auto w-full max-w-[52rem] px-5 pt-8 pb-16 sm:px-8 sm:pt-12">
          <header className="flex flex-wrap items-center justify-between gap-3 border-b border-line pb-3">
            <div className="flex items-baseline gap-2">
              <h2 className="text-base font-semibold text-ink">Legal references</h2>
              <span className="text-[13px] font-medium text-ink-muted">
                {reference.provisions.length}
              </span>
            </div>
            <span
              className="text-[13px] text-ink-muted"
              title={`From ${reference.provider || "an external legal service"}. It is not a case source.`}
            >
              External reference
            </span>
          </header>

          {accepted && (
            <>
              <p className="mt-4 text-[13px] leading-6 text-ink-secondary">
                {reference.disclaimer}
              </p>

              <ol className="divide-y divide-line">
                {reference.provisions.map((item, index) => (
                  <ProvisionItem key={`${index}-${item.citation}`} item={item} index={index} />
                ))}
              </ol>

              {reference.querySent && (
                <details className="group border-t border-line py-3">
                  <summary className="inline-flex h-8 cursor-pointer list-none items-center gap-1 rounded-md text-[13px] font-medium text-ink-secondary hover:text-ink">
                    What was searched
                    <Icon
                      name="chevron"
                      className="h-4 w-4 transition-transform group-open:rotate-180"
                    />
                  </summary>
                  <p className="mt-1 text-sm leading-7 whitespace-pre-line text-ink-secondary select-text">
                    {reference.querySent}
                  </p>
                  {reference.provider && (
                    <p className="mt-2 text-xs text-ink-muted">
                      Searched on <span className="font-mono">{reference.provider}</span>
                    </p>
                  )}
                </details>
              )}
            </>
          )}
        </div>
      </section>

      <ConfirmDialog
        isOpen={!accepted}
        title="โปรดอ่านก่อนดูข้อมูลกฎหมาย"
        description={reference.disclaimer}
        confirmLabel="รับทราบ"
        cancelLabel="ยกเลิก"
        onCancel={onDecline}
        onConfirm={() => setAccepted(true)}
        titleId="legal-notice-title"
        descriptionId="legal-notice-description"
      />
    </>
  );
}
