import { EmptyState } from "@/components/EmptyState";

export function CaseLibraryLoading() {
  return (
    <div className="mt-4 space-y-1" role="status" aria-label="Loading cases">
      {[1, 2, 3].map((placeholder) => (
        <div key={placeholder} className="flex items-center gap-4 px-3 py-4">
          <div className="flex-1 space-y-2">
            <div className="h-4 w-2/5 animate-pulse rounded bg-surface-nested" />
            <div className="h-3 w-24 animate-pulse rounded bg-surface-nested" />
          </div>
          <div className="h-3 w-20 animate-pulse rounded bg-surface-nested" />
        </div>
      ))}
    </div>
  );
}

export function CaseLibraryError({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="mt-10 flex flex-col items-center text-center" role="alert">
      <p className="text-base font-semibold text-ink">Cases could not be loaded</p>
      <p className="mt-1 text-sm text-ink-muted">{message}</p>
      <button type="button" onClick={onRetry} className="btn-secondary mt-5">
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
    <EmptyState
      title="No saved cases yet"
      description="A case holds its sources, analysis and report."
      className="mt-16"
    >
      <button type="button" onClick={onNewCase} disabled={creating} className="btn-primary mt-6">
        {creating ? "Creating…" : "Create your first case"}
      </button>
    </EmptyState>
  );
}

export function NoMatchingCases({ query, onClear }: { query: string; onClear: () => void }) {
  return (
    <div className="mt-10 flex flex-col items-center text-center">
      <p className="text-sm text-ink-muted">No cases match “{query}”</p>
      <button type="button" onClick={onClear} className="btn-ghost mt-2">
        Clear search
      </button>
    </div>
  );
}
