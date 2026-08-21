"use client";

import { useState } from "react";
import { Icon } from "@/components/common/icons";
import { CaseStateDeltaView } from "./case-state-delta-view";
import { CaseStateInspectorTabs } from "./case-state-inspector-tabs";
import {
  type CaseStateInspectorProps,
  type InspectorTab,
} from "./case-state-inspector-types";
import { CaseStateMitreView } from "./case-state-mitre-view";
import { CaseStateUnresolvedView } from "./case-state-unresolved-view";

export type { CaseStateInspectorProps } from "./case-state-inspector-types";
export type { CaseStateInspectorUpdate } from "./case-state-inspector-types";

export function CaseStateInspector({
  updates,
  selectedOrdinal,
  onSelectOrdinal,
  isOpen,
  onClose,
}: CaseStateInspectorProps) {
  const [activeTab, setActiveTab] = useState<InspectorTab>("delta");

  if (!isOpen) return null;

  const currentItem =
    updates.find((update) => update.ordinal === selectedOrdinal) ??
    updates[updates.length - 1] ??
    null;
  const unresolvedGaps =
    currentItem?.update.currentUnresolvedInformation ?? null;
  const mitreCandidates = currentItem?.mitreCandidates ?? null;
  const isUpdated =
    currentItem?.update.status === "updated" &&
    currentItem.update.childVersion !== null;

  return (
    <>
      <div
        role="presentation"
        className="fixed inset-0 z-30 bg-black/20 backdrop-blur-xs lg:hidden"
        onClick={onClose}
      />
      <aside
        aria-label="Case State Inspector"
        className="fixed inset-y-0 right-0 z-40 flex h-full w-full max-w-md flex-col border-l border-line bg-canvas shadow-xl transition-all lg:static lg:z-auto lg:h-full lg:w-[380px] xl:w-[420px] lg:shadow-none"
      >
        <InspectorHeader updateCount={updates.length} onClose={onClose} />
        {updates.length > 1 && (
          <InspectorHistory
            updates={updates}
            currentOrdinal={currentItem?.ordinal ?? null}
            onSelectOrdinal={onSelectOrdinal}
          />
        )}
        <CaseStateInspectorTabs
          activeTab={activeTab}
          onChange={setActiveTab}
          unresolvedCount={unresolvedGaps?.length ?? 0}
          mitreCount={mitreCandidates?.length ?? 0}
        />
        <div className="min-h-0 flex-1 overflow-y-auto p-4 sm:p-5">
          <InspectorContent
            activeTab={activeTab}
            currentItem={currentItem}
            isUpdated={isUpdated}
            unresolvedGaps={unresolvedGaps}
            mitreCandidates={mitreCandidates}
          />
        </div>
      </aside>
    </>
  );
}

function InspectorHeader({
  updateCount,
  onClose,
}: {
  updateCount: number;
  onClose: () => void;
}) {
  return (
    <div className="flex min-h-[76px] shrink-0 items-center justify-between border-b border-line bg-canvas px-4 py-3 sm:px-5 md:min-h-[72px]">
      <div className="flex min-w-0 items-center gap-2.5">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-surface-hover text-ink">
          <Icon name="details" className="h-4 w-4" />
        </div>
        <div className="min-w-0">
          <h2 className="truncate text-xs font-extrabold uppercase tracking-wider text-ink">
            Case State Inspector
          </h2>
          <p className="truncate text-[10px] text-ink-muted">
            {updateCount > 0
              ? `${updateCount} state update${updateCount > 1 ? "s" : ""}`
              : "Live delta, gaps & MITRE mapping"}
          </p>
        </div>
      </div>
      <button
        type="button"
        onClick={onClose}
        aria-label="Close Case State Inspector"
        title="Close inspector"
        className="flex h-8 w-8 shrink-0 cursor-pointer items-center justify-center rounded-lg text-ink-secondary outline-none transition-colors hover:bg-surface-hover hover:text-ink focus-visible:ring-2 focus-visible:ring-primary"
      >
        <Icon name="close" className="h-4 w-4" />
      </button>
    </div>
  );
}

function InspectorHistory({
  updates,
  currentOrdinal,
  onSelectOrdinal,
}: {
  updates: CaseStateInspectorProps["updates"];
  currentOrdinal: number | null;
  onSelectOrdinal: (ordinal: number) => void;
}) {
  return (
    <div className="flex shrink-0 items-center gap-1.5 overflow-x-auto border-b border-line bg-surface/50 px-4 py-2">
      <span className="mr-1 shrink-0 text-[10px] font-bold text-ink-muted">
        History:
      </span>
      {updates.map((item) => {
        const itemIsUpdated =
          item.update.status === "updated" &&
          item.update.childVersion !== null;
        const label = itemIsUpdated
          ? `V${item.update.parentVersion} → V${item.update.childVersion}`
          : `V${item.update.parentVersion}`;
        return (
          <button
            key={item.ordinal}
            type="button"
            onClick={() => onSelectOrdinal(item.ordinal)}
            className={`shrink-0 cursor-pointer rounded-lg px-2.5 py-1 text-[11px] font-bold transition-colors ${
              currentOrdinal === item.ordinal
                ? "bg-primary text-ivory shadow-xs"
                : "border border-line bg-surface text-ink-secondary hover:border-primary hover:text-ink"
            }`}
          >
            #{item.ordinal} {label}
          </button>
        );
      })}
    </div>
  );
}

function InspectorContent({
  activeTab,
  currentItem,
  isUpdated,
  unresolvedGaps,
  mitreCandidates,
}: {
  activeTab: InspectorTab;
  currentItem: CaseStateInspectorProps["updates"][number] | null;
  isUpdated: boolean;
  unresolvedGaps: CaseStateInspectorProps["updates"][number]["update"]["currentUnresolvedInformation"];
  mitreCandidates: CaseStateInspectorProps["updates"][number]["mitreCandidates"];
}) {
  if (!currentItem) {
    return (
      <div className="flex h-full min-h-[300px] flex-col items-center justify-center p-6 text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-surface-hover text-ink-muted">
          <Icon name="details" className="h-6 w-6" />
        </div>
        <h3 className="mt-4 text-sm font-extrabold text-ink">
          No Case State Updates Yet
        </h3>
        <p className="mt-1.5 max-w-[260px] text-xs leading-relaxed text-ink-secondary">
          When CyberCase analyzes security events and transitions the case graph,
          delta operations, gaps, and MITRE candidates will appear here.
        </p>
      </div>
    );
  }

  if (activeTab === "delta") {
    return <CaseStateDeltaView update={currentItem.update} isUpdated={isUpdated} />;
  }
  if (activeTab === "unresolved") {
    return <CaseStateUnresolvedView gaps={unresolvedGaps} />;
  }
  return <CaseStateMitreView candidates={mitreCandidates ?? null} />;
}
