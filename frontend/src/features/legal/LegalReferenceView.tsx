"use client";

import { useState } from "react";
import type { CaseAnalysisResultRead } from "@/lib/api";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { DisclosureToggle } from "@/components/Disclosure";
import { EmptyState } from "@/components/EmptyState";
import { Icon, type IconName } from "@/components/icons";
import {
  legalLookupSkipped,
  readLegalReference,
  type LegalProvision,
  type LegalReference,
} from "./legalReference";

interface LegalReferenceViewProps {
  analysisResult: CaseAnalysisResultRead | null;
  isLoading?: boolean;
  isError?: boolean;
  /** Where the reader goes when they turn the notice down. */
  onDecline: () => void;
}

/** Past this many characters a provision's text is clamped behind "Full text". */
const LONG_PROVISION_TEXT = 480;

/**
 * Thai provisions the RAG service matched to the case.
 *
 * They are references, not advice, so every visit to the page opens with the
 * provider's notice, and no provision is shown until the reader accepts it.
 */
export function LegalReferenceView({
  analysisResult,
  isLoading = false,
  isError = false,
  onDecline,
}: LegalReferenceViewProps) {
  if (isLoading) return <LegalSkeleton />;
  if (isError) {
    return (
      <LegalState
        icon="error"
        title="Analysis unavailable"
        description="The analysis could not be loaded."
      />
    );
  }
  if (!analysisResult) {
    return (
      <LegalState
        title="Not analyzed yet"
        description="Legal references are looked up when the case is analyzed."
      />
    );
  }

  const reference = readLegalReference(analysisResult);
  if (!reference) {
    return (
      <LegalState
        title="No legal references"
        description={
          legalLookupSkipped(analysisResult)
            ? "The legal lookup runs with the ATT&CK retrieval, and this case was judged not to need it."
            : "This analysis made no legal lookup."
        }
      />
    );
  }
  if (!reference.provisions.length) {
    return (
      <LegalState
        title="No provisions found"
        description={reference.degraded || "The legal service matched no provisions to this case."}
      />
    );
  }
  return <LegalProvisions reference={reference} onDecline={onDecline} />;
}

function LegalProvisions({
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
              className="tag bg-surface-nested text-ink-secondary"
              title={`From ${reference.provider || "an external legal service"}. It is not a case source.`}
            >
              External reference
            </span>
          </header>

          {accepted && (
            <>
              <p className="mt-4 flex gap-2.5 rounded-lg bg-unresolved/[0.08] px-3.5 py-2.5 text-[13px] leading-6 text-ink">
                <Icon name="alert" className="mt-1 h-4 w-4 shrink-0 text-unresolved" />
                <span>{reference.disclaimer}</span>
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

function ProvisionItem({ item, index }: { item: LegalProvision; index: number }) {
  const [isOpen, setIsOpen] = useState(false);
  const heading = item.citation || item.title || `Provision ${index + 1}`;
  // The citation usually already names the act, so the title would repeat it.
  const showTitle = Boolean(item.title) && !heading.includes(item.title);
  const isLong = item.text.length > LONG_PROVISION_TEXT;
  const textId = `legal-provision-${index}-text`;

  return (
    <li className="py-5">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <h3 className="text-[15px] leading-7 font-semibold text-ink">{heading}</h3>
          {showTitle && <p className="text-[13px] text-ink-muted">{item.title}</p>}
        </div>
        {item.url && (
          <a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            aria-label={`Open ${heading} at the source`}
            title="Open at the source"
            className="icon-btn"
          >
            <Icon name="external" className="h-4 w-4" />
          </a>
        )}
      </div>
      {item.text && (
        <>
          <p
            id={textId}
            className={`mt-1.5 text-sm leading-7 whitespace-pre-line text-ink-secondary select-text ${
              isLong && !isOpen ? "line-clamp-4" : ""
            }`}
          >
            {item.text}
          </p>
          {isLong && (
            <DisclosureToggle
              label="Full text"
              isOpen={isOpen}
              onToggle={() => setIsOpen((open) => !open)}
              controls={textId}
              className="-ml-1.5 mt-1"
            />
          )}
        </>
      )}
    </li>
  );
}

function LegalState({
  icon = "legal",
  title,
  description,
}: {
  icon?: IconName;
  title: string;
  description: string;
}) {
  return (
    <section
      id="workspace-legal-panel"
      aria-label="Legal references"
      className="flex shrink-0 flex-col bg-surface"
    >
      <EmptyState
        icon={icon}
        title={title}
        description={description}
        className="mx-auto min-h-[420px] w-full max-w-[52rem] justify-center px-5 py-16 sm:px-8"
      />
    </section>
  );
}

function LegalSkeleton() {
  return (
    <div
      role="status"
      aria-label="Loading legal references"
      className="mx-auto w-full max-w-[52rem] space-y-6 px-5 pt-8 sm:px-8 sm:pt-12"
    >
      <div className="h-4 w-40 animate-pulse rounded bg-surface-nested" />
      <div className="h-16 w-full animate-pulse rounded bg-surface-nested" />
      <div className="h-16 w-full animate-pulse rounded bg-surface-nested" />
    </div>
  );
}
