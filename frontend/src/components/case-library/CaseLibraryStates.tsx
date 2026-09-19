/** What the library shows when there are no cases to show. */

import { Icon } from "@/components/common/icons";

export function CaseLibraryLoading() {
  return (
    <div
      className="mt-8 grid gap-3 sm:grid-cols-2 xl:grid-cols-3"
      role="status"
      aria-label="Loading cases"
    >
      {[1, 2, 3].map((placeholder) => (
        <div
          key={placeholder}
          className="h-48 animate-pulse rounded-md border border-line bg-surface"
        />
      ))}
    </div>
  );
}

export function CaseLibraryError({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="mt-8 border-y border-line py-10 text-center" role="alert">
      <p className="text-sm font-semibold text-ink">Cases could not be loaded</p>
      <p className="mt-2 text-xs text-ink-secondary">{message}</p>
      <button
        type="button"
        onClick={onRetry}
        className="mt-5 rounded-md bg-primary px-4 py-2 text-xs font-bold text-ivory hover:bg-charcoal-hover focus-visible:ring-2 focus-visible:ring-primary"
      >
        Try again
      </button>
    </div>
  );
}

export function CaseLibraryEmpty({
  creating,
  onNewCase,
}: {
  creating: boolean;
  onNewCase: () => void;
}) {
  return (
    <div className="mt-8 border-y border-line py-14 text-center">
      <span className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-accent-soft text-accent">
        <Icon name="plus" className="h-5 w-5" />
      </span>
      <h2 className="mt-5 text-lg font-bold text-ink">No saved cases yet</h2>
      <p className="mx-auto mt-2 max-w-sm text-xs leading-5 text-ink-secondary">
        Create a Case to collect sources, run analysis, and keep the investigation available for
        later.
      </p>
      <button
        type="button"
        onClick={onNewCase}
        disabled={creating}
        className="mt-6 rounded-md bg-primary px-4 py-2.5 text-xs font-bold text-ivory hover:bg-charcoal-hover focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-60"
      >
        {creating ? "Creating…" : "Create your first case"}
      </button>
    </div>
  );
}

export function NoMatchingCases({ query, onClear }: { query: string; onClear: () => void }) {
  return (
    <div className="mt-8 border-y border-line py-10 text-center">
      <p className="text-sm font-semibold text-ink">No cases match “{query}”</p>
      <button
        type="button"
        onClick={onClear}
        className="mt-3 text-xs font-semibold text-accent underline underline-offset-4 hover:text-ink focus-visible:ring-2 focus-visible:ring-accent"
      >
        Clear search
      </button>
    </div>
  );
}
