import { Icon } from "@/components/icons";
import type { CaseLibrarySort, CaseLibraryViewMode } from "./caseDisplay";

export interface CaseLibraryToolbarProps {
  query: string;
  sort: CaseLibrarySort;
  viewMode: CaseLibraryViewMode;
  onQueryChange: (value: string) => void;
  onSortChange: (value: CaseLibrarySort) => void;
  onViewModeChange: (value: CaseLibraryViewMode) => void;
}

export function CaseLibraryToolbar({
  query,
  sort,
  viewMode,
  onQueryChange,
  onSortChange,
  onViewModeChange,
}: CaseLibraryToolbarProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3">
      <label className="relative w-full sm:w-72">
        <span className="sr-only">Search cases</span>
        <Icon
          name="search"
          className="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-ink-muted"
        />
        <input
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
          placeholder="Search cases"
          className="h-9 w-full rounded-lg border border-line-strong bg-surface pr-3 pl-9 text-sm text-ink outline-none placeholder:text-ink-muted focus:border-ink"
        />
      </label>

      <div className="flex items-center gap-2">
        <label className="relative inline-flex items-center">
          <span className="sr-only">Sort cases</span>
          <select
            value={sort}
            onChange={(event) => onSortChange(event.target.value as CaseLibrarySort)}
            aria-label="Sort cases"
            className="h-9 cursor-pointer appearance-none rounded-lg bg-transparent py-0 pr-7 pl-2.5 text-[13px] font-medium text-ink-secondary outline-none hover:bg-surface-hover hover:text-ink"
          >
            <option value="recent">Recently updated</option>
            <option value="oldest">Oldest first</option>
            <option value="title">Title</option>
          </select>
          <Icon
            name="chevron"
            className="pointer-events-none absolute right-2 h-4 w-4 text-ink-muted"
          />
        </label>
        <div
          className="flex items-center rounded-lg bg-surface-nested p-0.5"
          role="group"
          aria-label="Case layout"
        >
          <ViewButton
            label="List view"
            icon="list"
            selected={viewMode === "list"}
            onClick={() => onViewModeChange("list")}
          />
          <ViewButton
            label="Grid view"
            icon="overview"
            selected={viewMode === "grid"}
            onClick={() => onViewModeChange("grid")}
          />
        </div>
      </div>
    </div>
  );
}

function ViewButton({
  label,
  icon,
  selected,
  onClick,
}: {
  label: string;
  icon: "list" | "overview";
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      aria-pressed={selected}
      onClick={onClick}
      className={`flex h-8 w-8 items-center justify-center rounded-md transition-colors ${
        selected ? "bg-surface text-ink shadow-xs" : "text-ink-muted hover:text-ink"
      }`}
    >
      <Icon name={icon} className="h-4 w-4" />
    </button>
  );
}
