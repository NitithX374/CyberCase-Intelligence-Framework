"use client";

export function LegalSkeleton() {
  return (
    <div
      role="status"
      aria-label="Loading legal references"
      className="mx-auto w-full max-w-[52rem] space-y-6 px-5 pt-8 sm:px-8 sm:pt-12"
    >
      <div className="h-4 w-40 animate-pulse rounded bg-surface-nested" />
      <div className="h-16 w-full animate-pulse rounded bg-surface-nested" />
      <div className="h-16 w-full animate-pulse rounded bg-surface-nested" />
    </div>
  );
}
