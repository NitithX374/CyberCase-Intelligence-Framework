import { Icon } from "@/components/common/icons";
import type { CaseLibrarySort } from "./caseLibraryFormatters";

export type CaseLibraryViewMode = "grid" | "list";

interface CaseLibraryToolbarProps {
  query: string;
  sort: CaseLibrarySort;
  viewMode: CaseLibraryViewMode;
  resultCount: number;
  creating: boolean;
  onQueryChange: (value: string) => void;
  onSortChange: (value: CaseLibrarySort) => void;
  onViewModeChange: (value: CaseLibraryViewMode) => void;
  onNewCase: () => void;
}
export function CaseLibraryToolbar({
  query,
  sort,
  viewMode,
  resultCount,
  creating,
  onQueryChange,
  onSortChange,
  onViewModeChange,
  onNewCase,
}: CaseLibraryToolbarProps) {
  return (
    <div className="flex flex-col gap-3 border-y border-line py-3 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex min-w-0 flex-1 flex-wrap items-center gap-2.5">
        <label className="relative min-w-52 flex-1 sm:max-w-xs">
          <span className="sr-only">Search cases</span>
          <Icon name="search" className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-muted" />
          <input
            value={query}
            onChange={(event) => onQueryChange(event.target.value)}
            placeholder="Search cases"
            className="h-9 w-full rounded-md border border-line bg-surface pl-9 pr-3 text-xs text-ink outline-none placeholder:text-ink-muted hover:border-line-strong focus:border-accent focus:ring-2 focus:ring-accent/20"
          />
        </label>
        <label className="flex h-9 items-center gap-2 rounded-md border border-line bg-surface px-2.5 text-xs text-ink-secondary">
          <span className="sr-only">Sort cases</span>
          <span aria-hidden="true">Sort</span>
          <select
            value={sort}
            onChange={(event) => onSortChange(event.target.value as CaseLibrarySort)}
            className="bg-transparent font-semibold text-ink outline-none"
            aria-label="Sort cases"
          >
            <option value="recent">Recently updated</option>
            <option value="oldest">Oldest first</option>
            <option value="title">Title</option>
          </select>
        </label>
        <span className="text-[11px] text-ink-muted" aria-live="polite">
          {resultCount} {resultCount === 1 ? "case" : "cases"}
        </span>
      </div>

      <div className="flex items-center justify-between gap-2 sm:justify-end">
        <div className="flex items-center rounded-md border border-line bg-surface p-0.5" role="group" aria-label="Case layout">
          <button
            type="button"
            aria-label="Grid view"
            aria-pressed={viewMode === "grid"}
            onClick={() => onViewModeChange("grid")}
            className={`flex h-8 w-8 items-center justify-center rounded outline-none focus-visible:ring-2 focus-visible:ring-accent ${viewMode === "grid" ? "bg-accent-soft text-accent" : "text-ink-muted hover:bg-surface-hover hover:text-ink"}`}
          >
            <Icon name="overview" className="h-4 w-4" />
          </button>
          <button
            type="button"
            aria-label="List view"
            aria-pressed={viewMode === "list"}
            onClick={() => onViewModeChange("list")}
            className={`flex h-8 w-8 items-center justify-center rounded outline-none focus-visible:ring-2 focus-visible:ring-accent ${viewMode === "list" ? "bg-accent-soft text-accent" : "text-ink-muted hover:bg-surface-hover hover:text-ink"}`}
          >
            <Icon name="list" className="h-4 w-4" />
          </button>
        </div>
        <button
          type="button"
          onClick={onNewCase}
          disabled={creating}
          className="inline-flex h-9 items-center gap-2 rounded-md bg-primary px-3.5 text-xs font-bold text-ivory outline-none transition-colors hover:bg-charcoal-hover focus-visible:ring-2 focus-visible:ring-primary disabled:cursor-wait disabled:opacity-60"
        >
          <Icon name="plus" className="h-3.5 w-3.5" />
          {creating ? "Creating…" : "New case"}
        </button>
      </div>
    </div>
  );
}
