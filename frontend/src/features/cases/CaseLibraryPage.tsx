"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { CyberCaseLogo } from "@/components/CyberCaseLogo";
import { DeleteCaseDialog } from "@/features/cases/DeleteCaseDialog";
import { AccountMenu } from "@/features/auth/AccountMenu";
import { Icon } from "@/components/icons";
import { getApiErrorMessage, type CaseRead } from "@/lib/api";
import { useCaseMutations, useCases } from "@/features/cases/queries";
import { CaseCard } from "./CaseCard";
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
  const [viewMode, setViewMode] = useState<CaseLibraryViewMode>("list");

  const cases = useMemo(() => casesQuery.data ?? [], [casesQuery.data]);
  const visibleCases = useMemo(() => matchingCases(cases, query, sort), [cases, query, sort]);

  const newCase = async () => {
    if (createMutation.isPending) return;
    try {
      router.push(caseDestination(await createMutation.mutateAsync()));
    } catch {
      return;
    }
  };

  const confirmDelete = async () => {
    if (!deleteCandidate) return;
    try {
      await deleteMutation.mutateAsync(deleteCandidate.id);
    } finally {
      setDeleteCandidate(null);
    }
  };

  return (
    <main className="min-h-dvh bg-surface text-ink">
      <header className="border-b border-line">
        <div className="mx-auto flex h-14 w-full max-w-5xl items-center justify-between px-5 sm:px-8">
          <span className="flex items-center gap-2.5 text-[15px] font-semibold tracking-[-0.01em] text-ink">
            <CyberCaseLogo size={26} />
            CyberCase
          </span>
          <AccountMenu />
        </div>
      </header>

      <div className="mx-auto w-full max-w-5xl px-5 py-10 sm:px-8 sm:py-14">
        <div className="flex items-center justify-between gap-4">
          <h1 className="flex items-baseline gap-2.5 text-2xl font-semibold tracking-[-0.02em] text-ink">
            All cases
            {cases.length > 0 && (
              <span className="text-base font-medium text-ink-muted" aria-hidden="true">
                {cases.length}
              </span>
            )}
          </h1>
          {cases.length > 0 && (
            <button
              type="button"
              onClick={() => void newCase()}
              disabled={createMutation.isPending}
              className="btn-primary"
            >
              <Icon name={createMutation.isPending ? "spinner" : "plus"} className="h-4 w-4" />
              {createMutation.isPending ? "Creating…" : "New case"}
            </button>
          )}
        </div>

        {createMutation.error && (
          <p role="alert" className="mt-3 text-[13px] text-critical">
            {getApiErrorMessage(createMutation.error, "A new case could not be created.")}
          </p>
        )}

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
          <section aria-label="Your cases" className="mt-8">
            <CaseLibraryToolbar
              query={query}
              sort={sort}
              viewMode={viewMode}
              onQueryChange={setQuery}
              onSortChange={setSort}
              onViewModeChange={setViewMode}
            />

            {visibleCases.length === 0 ? (
              <NoMatchingCases query={query} onClear={() => setQuery("")} />
            ) : (
              <ul
                className={
                  viewMode === "grid"
                    ? "mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3"
                    : "-mx-3 mt-4 divide-y divide-line"
                }
              >
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
              </ul>
            )}
          </section>
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
