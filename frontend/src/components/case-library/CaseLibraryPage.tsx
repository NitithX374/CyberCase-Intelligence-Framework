"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Icon } from "@/components/common/icons";
import { CyberCaseLogo } from "@/components/common/CyberCaseLogo";
import { getApiErrorMessage, type CaseRead } from "@/lib/api";
import { useCaseMutations, useCases } from "@/hooks/useCaseQueries";
import { CaseLibraryCard, NewCaseCard } from "./CaseLibraryCard";
import { CaseLibraryToolbar, type CaseLibraryViewMode } from "./CaseLibraryToolbar";
import { caseDestination, caseStatusLabel, formatCaseDate, sortCases, type CaseLibrarySort } from "./caseLibraryFormatters";

export function CaseLibraryPage() {
  const router = useRouter();
  const casesQuery = useCases();
  const { createMutation } = useCaseMutations();
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<CaseLibrarySort>("recent");
  const [viewMode, setViewMode] = useState<CaseLibraryViewMode>("grid");
  const cases = casesQuery.data ?? [];
  const latestCase = sortCases(cases, "recent")[0] ?? null;
  const visibleCases = useMemo(() => {
    const allCases = casesQuery.data ?? [];
    const normalizedQuery = query.trim().toLocaleLowerCase();
    const matchingCases = normalizedQuery
      ? allCases.filter((caseRecord) => caseRecord.title.toLocaleLowerCase().includes(normalizedQuery))
      : allCases;
    return sortCases(matchingCases, sort);
  }, [casesQuery.data, query, sort]);

  const handleNewCase = async () => {
    if (createMutation.isPending) return;
    try {
      const newCase = await createMutation.mutateAsync();
      router.push(caseDestination(newCase));
    } catch {
      return;
    }
  };

  return (
    <main className="min-h-dvh bg-canvas text-ink">
      <CaseLibraryHeader />
      <div className="mx-auto w-full max-w-[1440px] px-5 py-7 sm:px-8 sm:py-9 lg:px-12 lg:py-10">
        <header className="flex flex-col gap-2 border-b border-line pb-6 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="mono-label">Case library</p>
            <h1 className="mt-2 text-2xl font-bold tracking-[-0.03em] text-ink sm:text-3xl">All cases</h1>
            <p className="mt-2 max-w-xl text-xs leading-5 text-ink-secondary sm:text-sm">Return to an investigation, review its latest state, or begin a new evidence-bound case.</p>
          </div>
          <span className="text-[11px] text-ink-muted">{cases.length} saved {cases.length === 1 ? "case" : "cases"}</span>
        </header>

        {casesQuery.isLoading ? <CaseLibraryLoadingState /> : casesQuery.error ? <CaseLibraryErrorState message={getApiErrorMessage(casesQuery.error, "Cases could not be loaded.")} onRetry={() => void casesQuery.refetch()} /> : cases.length === 0 ? <CaseLibraryEmptyState creating={createMutation.isPending} onNewCase={() => void handleNewCase()} /> : (
          <>
            {latestCase && !query.trim() && <LatestCaseSection caseRecord={latestCase} />}
            <section aria-labelledby="all-cases-heading" className="mt-10">
              <div className="flex items-baseline justify-between gap-4">
                <div>
                  <h2 id="all-cases-heading" className="text-lg font-bold tracking-[-0.02em] text-ink">Your cases</h2>
                  <p className="mt-1 text-xs text-ink-muted">Select a Case to continue its workspace.</p>
                </div>
              </div>
              <div className="mt-4">
                <CaseLibraryToolbar
                  query={query}
                  sort={sort}
                  viewMode={viewMode}
                  resultCount={visibleCases.length}
                  creating={createMutation.isPending}
                  onQueryChange={setQuery}
                  onSortChange={setSort}
                  onViewModeChange={setViewMode}
                  onNewCase={() => void handleNewCase()}
                />
              </div>
              {createMutation.error && <p role="alert" className="mt-3 text-xs text-critical">{getApiErrorMessage(createMutation.error, "A new Case could not be created.")}</p>}
              {visibleCases.length === 0 ? <NoMatchingCases query={query} onClear={() => setQuery("")} /> : <div className={viewMode === "grid" ? "mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-3" : "mt-5 grid gap-2"}>
                <NewCaseCard onClick={() => void handleNewCase()} disabled={createMutation.isPending} />
                {visibleCases.map((caseRecord) => <CaseLibraryCard key={caseRecord.id} caseRecord={caseRecord} viewMode={viewMode} />)}
              </div>}
            </section>
          </>
        )}
      </div>
    </main>
  );
}

function CaseLibraryHeader() {
  return (
    <header className="border-b border-line bg-surface">
      <div className="mx-auto flex min-h-16 w-full max-w-[1440px] items-center gap-6 px-5 sm:px-8 lg:px-12">
        <Link href="/" className="flex shrink-0 items-center gap-2.5 text-sm font-bold tracking-[-0.015em] text-ink focus-visible:ring-2 focus-visible:ring-accent">
          <CyberCaseLogo size={28} />
          <span className="hidden sm:inline">CyberCase</span>
        </Link>
        <nav aria-label="Case library navigation" className="flex h-16 items-center gap-5 text-xs font-semibold">
          <span className="flex h-full items-center border-b-2 border-accent text-accent" aria-current="page">All cases</span>
          <Link href="/" className="text-ink-muted transition-colors hover:text-ink">About CyberCase</Link>
        </nav>
      </div>
    </header>
  );
}

function LatestCaseSection({ caseRecord }: { caseRecord: CaseRead }) {
  return (
    <section aria-labelledby="latest-case-heading" className="mt-8">
      <div className="mb-3 flex items-center justify-between gap-4">
        <h2 id="latest-case-heading" className="text-lg font-bold tracking-[-0.02em] text-ink">Continue where you left off</h2>
        <span className="text-[11px] text-ink-muted">Latest activity</span>
      </div>
      <Link href={caseDestination(caseRecord)} className="group block rounded-md border border-line bg-surface p-4 outline-none transition-colors hover:border-line-strong hover:bg-surface-hover focus-visible:ring-2 focus-visible:ring-accent sm:p-5">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[10px] font-semibold text-ink-muted">
              <span className="inline-flex items-center gap-2"><span className="h-1.5 w-1.5 rounded-full bg-accent" aria-hidden="true" />{caseStatusLabel(caseRecord)}</span>
              <span>Updated {formatCaseDate(caseRecord.updated_at)}</span>
            </div>
            <h3 className="mt-2 truncate text-xl font-semibold tracking-[-0.025em] text-ink sm:text-2xl" title={caseRecord.title}>{caseRecord.title}</h3>
            <p className="mt-2 text-xs text-ink-muted">Evidence revision {caseRecord.evidence_revision}</p>
          </div>
          <span className="inline-flex shrink-0 items-center gap-2 text-xs font-bold text-accent transition-transform group-hover:translate-x-0.5">Open case <Icon name="external" className="h-3.5 w-3.5" /></span>
        </div>
      </Link>
    </section>
  );
}

function CaseLibraryLoadingState() {
  return <div className="mt-8 grid gap-3 sm:grid-cols-2 xl:grid-cols-3" role="status" aria-label="Loading cases">{[1, 2, 3].map((item) => <div key={item} className="h-48 animate-pulse rounded-md border border-line bg-surface" />)}</div>;
}

function CaseLibraryErrorState({ message, onRetry }: { message: string; onRetry: () => void }) {
  return <div className="mt-8 border-y border-line py-10 text-center" role="alert"><p className="text-sm font-semibold text-ink">Cases could not be loaded</p><p className="mt-2 text-xs text-ink-secondary">{message}</p><button type="button" onClick={onRetry} className="mt-5 rounded-md bg-primary px-4 py-2 text-xs font-bold text-ivory hover:bg-charcoal-hover focus-visible:ring-2 focus-visible:ring-primary">Try again</button></div>;
}

function CaseLibraryEmptyState({ creating, onNewCase }: { creating: boolean; onNewCase: () => void }) {
  return <div className="mt-8 border-y border-line py-14 text-center"><span className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-accent-soft text-accent"><Icon name="plus" className="h-5 w-5" /></span><h2 className="mt-5 text-lg font-bold text-ink">No saved cases yet</h2><p className="mx-auto mt-2 max-w-sm text-xs leading-5 text-ink-secondary">Create a Case to collect evidence, run analysis, and keep the investigation available for later.</p><button type="button" onClick={onNewCase} disabled={creating} className="mt-6 rounded-md bg-primary px-4 py-2.5 text-xs font-bold text-ivory hover:bg-charcoal-hover focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-60">{creating ? "Creating…" : "Create your first case"}</button></div>;
}

function NoMatchingCases({ query, onClear }: { query: string; onClear: () => void }) {
  return <div className="mt-8 border-y border-line py-10 text-center"><p className="text-sm font-semibold text-ink">No cases match “{query}”</p><button type="button" onClick={onClear} className="mt-3 text-xs font-semibold text-accent underline underline-offset-4 hover:text-ink focus-visible:ring-2 focus-visible:ring-accent">Clear search</button></div>;
}
