"use client";

import { useState } from "react";
import { DisclosureToggle } from "@/components/Disclosure";
import { Icon } from "@/components/icons";
import type { LegalProvision } from "./legalReference";

const LONG_PROVISION_TEXT = 480;

export function ProvisionItem({ item, index }: { item: LegalProvision; index: number }) {
  const [isOpen, setIsOpen] = useState(false);
  const heading = item.citation || item.title || `Provision ${index + 1}`;
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
