"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { CyberCaseLogo } from "@/components/common/CyberCaseLogo";
import { DeleteCaseDialog } from "@/components/common/DeleteDialog";
import { getApiErrorMessage, type CaseRead } from "@/lib/api";
import { useCaseMutations, useCases } from "@/hooks/useCaseQueries";
import { CaseCard, FeaturedCaseCard, NewCaseCard } from "./CaseCard";
import { CaseLibraryToolbar } from "./CaseLibraryToolbar";
import {
  CaseLibraryEmpty,
  CaseLibraryError,
  CaseLibraryLoading,
  NoMatchingCases,
} from "./CaseLibraryStates";
import {
  caseDestination,
  matchingCases,
  sortCases,
  type CaseLibrarySort,
  type CaseLibraryViewMode,
} from "./caseDisplay";

export function CaseLibraryPage() {
  const router = useRouter();
  const casesQuery = useCases();
  const { createMutation, deleteMutation } = useCaseMutations();

  const [deleteCandidate, setDeleteCandidate] = useState<CaseRead | null>(null);
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<CaseLibrarySort>("recent");
  const [viewMode, setViewMode] = useState<CaseLibraryViewMode>("grid");

  const cases = useMemo(() => casesQuery.data ?? [], [casesQuery.data]);
  const visibleCases = useMemo(() => matchingCases(cases, query, sort), [cases, query, sort]);
  const latestCase = sortCases(cases, "recent")[0] ?? null;

  const newCase = async () => {
    if (createMutation.isPending) return;
    try {
      router.push(caseDestination(await createMutation.mutateAsync()));
    } catch {
      return;
    }
  };

  // Deleting a case belongs where the cases are listed: the one place it is
  // not the thing you are looking at.
  const confirmDelete = async () => {
    if (!deleteCandidate) return;
    try {
      await deleteMutation.mutateAsync(deleteCandidate.id);
    } finally {
      setDeleteCandidate(null);
    }
  };

  return (
    <main className="min-h-dvh bg-canvas text-ink">
      <CaseLibraryHeader />

      <div className="mx-auto w-full max-w-[1440px] px-5 py-7 sm:px-8 sm:py-9 lg:px-12 lg:py-10">
        <header className="flex flex-col gap-2 border-b border-line pb-6 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="mono-label">Case library</p>
            <h1 className="mt-2 text-2xl font-bold tracking-[-0.03em] text-ink sm:text-3xl">
              All cases
            </h1>
            <p className="mt-2 max-w-xl text-xs leading-5 text-ink-secondary sm:text-sm">
              Return to an investigation, review its latest state, or begin a new source-bound case.
            </p>
          </div>
          <span className="text-[11px] text-ink-muted">
            {cases.length} saved {cases.length === 1 ? "case" : "cases"}
          </span>
        </header>

        {casesQuery.isLoading ? (
          <CaseLibraryLoading />
        ) : casesQuery.error ? (
          <CaseLibraryError
            message={getApiErrorMessage(casesQuery.error, "Cases could not be loaded.")}
            onRetry={() => void casesQuery.refetch()}
          />
        ) : cases.length === 0 ? (
          <CaseLibraryEmpty creating={createMutation.isPending} onNewCase={() => void newCase()} />
        ) : (
          <>
            {latestCase && !query.trim() && (
              <section aria-labelledby="latest-case-heading" className="mt-8">
                <div className="mb-3 flex items-center justify-between gap-4">
                  <h2
                    id="latest-case-heading"
                    className="text-lg font-bold tracking-[-0.02em] text-ink"
                  >
                    Continue where you left off
                  </h2>
                  <span className="text-[11px] text-ink-muted">Latest activity</span>
                </div>
                <FeaturedCaseCard caseRecord={latestCase} />
              </section>
            )}

            <section aria-labelledby="all-cases-heading" className="mt-10">
              <h2 id="all-cases-heading" className="text-lg font-bold tracking-[-0.02em] text-ink">
                Your cases
              </h2>
              <p className="mt-1 text-xs text-ink-muted">
                Select a Case to continue its workspace.
              </p>

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
                  onNewCase={() => void newCase()}
                />
              </div>

              {createMutation.error && (
                <p role="alert" className="mt-3 text-xs text-critical">
                  {getApiErrorMessage(createMutation.error, "A new Case could not be created.")}
                </p>
              )}

              {visibleCases.length === 0 ? (
                <NoMatchingCases query={query} onClear={() => setQuery("")} />
              ) : (
                <div
                  className={
                    viewMode === "grid"
                      ? "mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-3"
                      : "mt-5 grid gap-2"
                  }
                >
                  <NewCaseCard onClick={() => void newCase()} disabled={createMutation.isPending} />
                  {visibleCases.map((caseRecord) => (
                    <CaseCard
                      key={caseRecord.id}
                      caseRecord={caseRecord}
                      viewMode={viewMode}
                      isDeleting={
                        deleteMutation.isPending && deleteMutation.variables === caseRecord.id
                      }
                      onRequestDelete={setDeleteCandidate}
                    />
                  ))}
                </div>
              )}
            </section>
          </>
        )}
      </div>

      <DeleteCaseDialog
        caseRecord={deleteCandidate}
        isDeleting={deleteMutation.isPending}
        onCancel={() => setDeleteCandidate(null)}
        onConfirm={() => void confirmDelete()}
      />
    </main>
  );
}

function CaseLibraryHeader() {
  return (
    <header className="border-b border-line bg-surface">
      <div className="mx-auto flex min-h-16 w-full max-w-[1440px] items-center gap-6 px-5 sm:px-8 lg:px-12">
        <span className="flex shrink-0 items-center gap-2.5 text-sm font-bold tracking-[-0.015em] text-ink">
          <CyberCaseLogo size={28} />
          <span className="hidden sm:inline">CyberCase</span>
        </span>

        <nav
          aria-label="Case library navigation"
          className="flex h-16 items-center gap-5 text-xs font-semibold"
        >
          <span
            className="flex h-full items-center border-b-2 border-accent text-accent"
            aria-current="page"
          >
            All cases
          </span>
        </nav>
      </div>
    </header>
  );
}
