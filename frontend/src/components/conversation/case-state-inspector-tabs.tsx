import type { InspectorTab } from "./case-state-inspector-types";

interface CaseStateInspectorTabsProps {
  activeTab: InspectorTab;
  onChange: (tab: InspectorTab) => void;
  unresolvedCount: number;
  mitreCount: number;
}

export function CaseStateInspectorTabs({
  activeTab,
  onChange,
  unresolvedCount,
  mitreCount,
}: CaseStateInspectorTabsProps) {
  return (
    <div className="flex shrink-0 border-b border-line bg-canvas px-3 py-2 sm:px-4">
      <div className="flex w-full gap-1 rounded-xl bg-surface-hover p-1">
        <button
          type="button"
          onClick={() => onChange("delta")}
          className={`flex-1 rounded-lg py-1.5 text-center text-[11px] font-bold transition-all cursor-pointer ${
            activeTab === "delta"
              ? "bg-surface text-ink shadow-xs"
              : "text-ink-secondary hover:text-ink"
          }`}
        >
          State Delta
        </button>
        <button
          type="button"
          onClick={() => onChange("unresolved")}
          className={`flex flex-1 items-center justify-center gap-1 rounded-lg py-1.5 text-center text-[11px] font-bold transition-all cursor-pointer ${
            activeTab === "unresolved"
              ? "bg-surface text-ink shadow-xs"
              : "text-ink-secondary hover:text-ink"
          }`}
        >
          <span>Unresolved</span>
          {unresolvedCount > 0 && (
            <span className="rounded-full bg-red-100 px-1.5 py-0.2 text-[9px] font-extrabold text-red-800">
              {unresolvedCount}
            </span>
          )}
        </button>
        <button
          type="button"
          onClick={() => onChange("mitre")}
          className={`flex flex-1 items-center justify-center gap-1 rounded-lg py-1.5 text-center text-[11px] font-bold transition-all cursor-pointer ${
            activeTab === "mitre"
              ? "bg-surface text-ink shadow-xs"
              : "text-ink-secondary hover:text-ink"
          }`}
        >
          <span>MITRE</span>
          {mitreCount > 0 && (
            <span className="rounded-full bg-[#EDE9F2] px-1.5 py-0.2 text-[9px] font-extrabold text-[#51495D]">
              {mitreCount}
            </span>
          )}
        </button>
      </div>
    </div>
  );
}
