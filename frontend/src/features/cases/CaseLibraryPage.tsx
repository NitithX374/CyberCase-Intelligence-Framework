"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { CyberCaseLogo } from "@/components/CyberCaseLogo";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { AccountMenu } from "@/features/auth/AccountMenu";
import { useAuth } from "@/features/auth/useAuth";
import Link from "next/link";
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

type CaseStatusFilter = "all" | CaseRead["analysis_freshness"];

const STATUS_CARDS: Array<{
  status: CaseStatusFilter;
  label: string;
}> = [
  { status: "all", label: "all cases" },
  { status: "current", label: "analyzed" },
  { status: "stale", label: "out of date" },
  { status: "missing", label: "not analyzed" },
];

export function CaseLibraryPage() {
  const router = useRouter();
  const casesQuery = useCases();
  const { createMutation, deleteMutation } = useCaseMutations();

  const [deleteCandidate, setDeleteCandidate] = useState<CaseRead | null>(null);
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<CaseLibrarySort>("recent");
  const [viewMode, setViewMode] = useState<CaseLibraryViewMode>("list");

  const cases = useMemo(() => casesQuery.data ?? [], [casesQuery.data]);
  const [status, setStatus] = useState<CaseStatusFilter>("all");
  const { user } = useAuth();
  const visibleCases = useMemo(
    () =>
      matchingCases(cases, query, sort).filter(
        (caseRecord) => status === "all" || caseRecord.analysis_freshness === status,
      ),
    [cases, query, sort, status],
  );
  const counts = {
    all: cases.length,
    current: cases.filter((caseRecord) => caseRecord.analysis_freshness === "current").length,
    stale: cases.filter((caseRecord) => caseRecord.analysis_freshness === "stale").length,
    missing: cases.filter((caseRecord) => caseRecord.analysis_freshness === "missing").length,
  };
  const recent = matchingCases(cases, "", "recent").slice(0, 5);
  const firstName = user?.name?.trim().split(/\s+/)[0];
  const outstanding = [
    counts.stale > 0 &&
      `${counts.stale} ${counts.stale === 1 ? "case is" : "cases are"} out of date`,
    counts.missing > 0 &&
      `${counts.missing} ${counts.missing === 1 ? "case has" : "cases have"} not been analyzed`,
  ].filter(Boolean);

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
        <span aria-hidden="true" className="mx-3 -mt-2 mb-4 h-px bg-primary" />
        <span
          aria-current="page"
          className="flex min-h-11 items-center gap-3.5 rounded-lg bg-primary px-3.5 text-sm font-semibold"
        >
          <Icon name="folder" className="text-[22px]" />
          All cases
          {cases.length > 0 && (
            <span className="ml-auto inline-flex h-6 min-w-6 items-center justify-center rounded-md bg-white/20 px-1.5 text-xs">
              {cases.length}
            </span>
          )}
        </span>
        {recent.length > 0 && (
          <nav aria-label="Recent cases" className="flex flex-col gap-1">
            <p className="px-3.5 pt-5 pb-2 text-xs font-semibold tracking-[0.1em] text-espresso-muted uppercase">
              Recent
            </p>
            {recent.map((caseRecord) => (
              <Link
                key={caseRecord.id}
                href={caseDestination(caseRecord)}
                className="group flex min-h-11 items-center gap-3.5 rounded-lg px-3.5 text-sm text-white/85 transition-colors hover:bg-espresso-raised hover:text-white focus-visible:outline-white"
              >
                <Icon
                  name="case"
                  className="shrink-0 text-[22px] transition-transform duration-200 group-hover:translate-x-0.5"
                />
                <span className="truncate" title={caseRecord.title}>
                  {caseRecord.title}
                </span>
              </Link>
            ))}
          </nav>
        )}
      </aside>
      <main className="rise-in min-w-0 flex-1 px-3 pt-4 pb-12 sm:px-6 lg:px-8 lg:pt-5">
        <header className="flex min-h-12 items-center gap-3 border-b border-line-strong pb-4">
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

        {cases.length > 0 && (
          <>
            <div className="ruled rise-in relative mt-5 overflow-hidden rounded-xl bg-primary px-5 py-6 text-white sm:px-8 sm:py-7">
              <div className="relative flex flex-wrap items-center gap-5">
                <div className="min-w-0 flex-1">
                  <p className="text-2xl font-bold tracking-[-0.01em] sm:text-3xl">
                    {firstName ? `Welcome back, ${firstName}` : "Welcome back"}
                  </p>
                  <p className="mt-2 text-sm text-white">
                    {outstanding.length === 0
                      ? "Every case has an up-to-date analysis."
                      : `${outstanding.join(" and ")}.`}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => void newCase()}
                  disabled={createMutation.isPending}
                  className="btn-on-band"
                >
                  <Icon name={createMutation.isPending ? "spinner" : "plus"} className="text-lg" />
                  {createMutation.isPending ? "Creating…" : "New case"}
                </button>
              </div>
            </div>

            <div
              role="group"
              aria-label="Show cases"
              className="mt-5 grid grid-cols-2 gap-5 xl:grid-cols-4"
            >
              {STATUS_CARDS.map((card, index) => (
                <button
                  key={card.status}
                  type="button"
                  aria-pressed={status === card.status}
                  onClick={() => setStatus(card.status)}
                  style={{ ["--i" as string]: index + 1, ["--step" as string]: "60ms" }}
                  className={`sheet stagger lift px-5 py-4 text-left active:scale-[0.99] ${
                    status === card.status ? "ring-2 ring-primary" : ""
                  }`}
                >
                  <span>
                    <span className="block text-2xl leading-tight font-bold text-ink">
                      {counts[card.status]}
                    </span>
                    <span className="block text-sm text-ink-muted">{card.label}</span>
                  </span>
                </button>
              ))}
            </div>
          </>
        )}

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
                <NoMatchingCases
                  query={query}
                  onClear={() => {
                    setQuery("");
                    setStatus("all");
                  }}
                />
              ) : (
                <>
                  {viewMode === "list" && (
                    <div
                      aria-hidden="true"
                      className="-mx-5 mt-4 flex gap-4 border-t border-line bg-surface-nested px-5 py-2.5 text-xs font-semibold tracking-[0.08em] text-ink-muted uppercase sm:-mx-6 sm:px-6"
                    >
                      <span className="flex-1">Case</span>
                      <span>Status</span>
                      <span className="hidden w-32 text-right sm:block">Updated</span>
                      <span className="w-10" />
                    </div>
                  )}
                  <ul
                    key={`${status}:${sort}:${viewMode}`}
                    className={
                      viewMode === "grid"
                        ? "mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3"
                        : "-mx-5 divide-y divide-line border-t border-line sm:-mx-6"
                    }
                  >
                    {visibleCases.map((caseRecord, index) => (
                      <CaseCard
                        key={caseRecord.id}
                        index={index}
                        caseRecord={caseRecord}
                        viewMode={viewMode}
                        isDeleting={
                          deleteMutation.isPending && deleteMutation.variables === caseRecord.id
                        }
                        onRequestDelete={setDeleteCandidate}
                      />
                    ))}
                  </ul>
                </>
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
