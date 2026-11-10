import type { ReactNode } from "react";
import { CyberCaseLogo } from "./CyberCaseLogo";

export function AppSkeleton({
  title,
  detail,
  children,
}: {
  title: string;
  detail?: string;
  children?: ReactNode;
}) {
  return (
    <div className="flex h-dvh overflow-hidden bg-ground text-ink">
      <aside
        aria-hidden="true"
        className="hidden w-[17.5rem] shrink-0 flex-col gap-3 bg-espresso px-4 py-6 lg:flex"
      >
        <span className="flex items-center gap-3 px-3 text-xl font-bold text-white">
          <span className="flex h-10 w-10 items-center justify-center rounded-[10px] bg-surface">
            <CyberCaseLogo size={28} />
          </span>
          CyberCase
        </span>
        <span className="mx-3 mt-1 mb-3 h-px bg-espresso-line" />
        {[70, 55, 62, 48, 58].map((width, index) => (
          <span
            key={index}
            className="mx-3.5 h-4 rounded bg-espresso-raised"
            style={{ width: `${width}%` }}
          />
        ))}
      </aside>
      <main className="flex min-w-0 flex-1 flex-col gap-5 px-3 pt-5 sm:px-6 lg:px-8">
        <div
          aria-hidden="true"
          className="flex min-h-12 shrink-0 items-center gap-3 border-b border-line-strong pb-4"
        >
          <span className="shimmer h-4 w-56 rounded" />
          <span className="ml-auto h-10 w-10 rounded-full bg-surface-hover" />
        </div>
        <section
          role="status"
          aria-live="polite"
          className="relative shrink-0 overflow-hidden rounded-xl bg-primary px-5 py-6 text-white sm:px-8 sm:py-7"
        >
          <div className="relative flex items-start gap-4">
            <span className="mt-1 flex h-5 w-5 shrink-0 items-center justify-center">
              <span className="h-5 w-5 animate-spin rounded-full border-2 border-white/35 border-t-white motion-reduce:animate-none" />
            </span>
            <div className="min-w-0">
              <p className="text-2xl font-bold tracking-[-0.01em]">{title}</p>
              {detail && <p className="mt-2 max-w-2xl text-sm text-white">{detail}</p>}
              {children}
            </div>
          </div>
        </section>
        <div aria-hidden="true" className="grid shrink-0 grid-cols-2 gap-5 xl:grid-cols-4">
          {[0, 1, 2, 3].map((index) => (
            <div key={index} className="sheet space-y-2.5 px-5 py-4">
              <span className="shimmer block h-7 w-12 rounded" />
              <span className="shimmer block h-3.5 w-24 rounded" />
            </div>
          ))}
        </div>
        <div aria-hidden="true" className="sheet space-y-4 px-6 py-6">
          <span className="shimmer block h-5 w-40 rounded" />
          {[92, 84, 88, 70].map((width, index) => (
            <span
              key={index}
              className="shimmer block h-4 rounded"
              style={{ width: `${width}%` }}
            />
          ))}
        </div>
      </main>
    </div>
  );
}
