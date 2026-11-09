"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { CyberCaseLogo } from "@/components/CyberCaseLogo";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { AccountMenu } from "@/features/auth/AccountMenu";
import { Icon } from "@/components/icons";
import type { CaseRead } from "@/lib/api/types";
import { detailMessage } from "@/lib/userFacingError";
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
    } catch {
      return;
    } finally {
      setDeleteCandidate(null);
    }
  };

  return (
    <div className="flex min-h-dvh bg-ground text-ink">
      <aside className="hidden w-[17.5rem] shrink-0 flex-col gap-1 bg-espresso px-4 py-6 text-white lg:flex">
        <span className="mb-5 flex items-center gap-3 px-3 text-xl font-bold tracking-[-0.01em]">
          <span className="flex h-10 w-10 items-center justify-center rounded-[10px] bg-surface">
            <CyberCaseLogo size={28} />
          </span>
          CyberCase
        </span>
        <span
          aria-current="page"
          className="flex min-h-11 items-center gap-3.5 rounded-lg bg-primary px-3.5 text-sm font-semibold shadow-[0_0_12px_1px_rgba(156,79,51,0.45)]"
        >
          <Icon name="folder" className="text-[22px]" />
          All cases
          {cases.length > 0 && (
            <span className="ml-auto inline-flex h-6 min-w-6 items-center justify-center rounded-full bg-white/20 px-1.5 text-xs">
              {cases.length}
            </span>
          )}
        </span>
      </aside>
      <main className="min-w-0 flex-1 px-3 pt-4 pb-12 sm:px-6 lg:px-8 lg:pt-5">
        <header className="sheet flex min-h-16 items-center gap-3 px-5">
          <span className="flex items-center gap-2.5 text-base font-semibold text-ink lg:hidden">
            <CyberCaseLogo size={26} />
            CyberCase
          </span>
          <span className="hidden flex-1 text-sm text-ink-muted lg:block">
            Your cases, newest first. Open one to read its findings.
          </span>
          <span className="flex-1 lg:hidden" />
          <AccountMenu />
        </header>

        <div className="sheet mt-5 w-full px-5 py-6 sm:px-6">
          <div className="flex items-center justify-between gap-4">
            <h1 className="flex items-center gap-2.5 text-2xl font-bold tracking-[-0.01em] text-ink">
              All cases
              {cases.length > 0 && (
                <span className="count-pill" aria-hidden="true">
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
            <p role="alert" className="mt-3 text-sm text-critical">
              {detailMessage(createMutation.error, "A new case could not be created.")}
            </p>
          )}
          {deleteMutation.error && (
            <p role="alert" className="mt-3 text-sm text-critical">
              {detailMessage(deleteMutation.error, "The case could not be deleted.")}
            </p>
          )}

          {casesQuery.isLoading ? (
            <CaseLibraryLoading />
          ) : casesQuery.error ? (
            <CaseLibraryError
              message={detailMessage(casesQuery.error, "Cases could not be loaded.")}
              onRetry={() => void casesQuery.refetch()}
            />
          ) : cases.length === 0 ? (
            <CaseLibraryEmpty
              creating={createMutation.isPending}
              onNewCase={() => void newCase()}
            />
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
                      : "-mx-5 mt-4 divide-y divide-line border-t border-line sm:-mx-6"
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

        <ConfirmDialog
          isOpen={Boolean(deleteCandidate)}
          title="Delete this case?"
          description={`“${deleteCandidate?.title ?? "This case"}” and its sources, chat and reports will be permanently deleted.`}
          confirmLabel="Delete case"
          confirmLoadingLabel="Deleting…"
          isProcessing={deleteMutation.isPending}
          tone="danger"
          onCancel={() => setDeleteCandidate(null)}
          onConfirm={() => void confirmDelete()}
          titleId="delete-case-title"
          descriptionId="delete-case-description"
        />
      </main>
    </div>
  );
}
