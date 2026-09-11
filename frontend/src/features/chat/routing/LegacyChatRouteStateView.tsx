import Link from "next/link";

type LegacyChatRouteState = "resolving" | "historical_unavailable" | "unavailable";

export function LegacyChatRouteStateView({ state }: { state: LegacyChatRouteState }) {
  if (state === "resolving") {
    return (
      <main className="flex min-h-screen items-center justify-center bg-canvas p-8 text-ink" role="status">
        <p className="font-mono text-xs font-bold uppercase tracking-widest text-ink-secondary">
          Resolving legacy Chat link…
        </p>
      </main>
    );
  }

  const historical = state === "historical_unavailable";
  return (
    <main className="flex min-h-screen items-center justify-center bg-canvas p-8 text-ink">
      <section className="w-full max-w-lg rounded-2xl border border-line bg-surface p-8 text-center shadow-sm">
        <p className="section-eyebrow">LEGACY CHAT LINK</p>
        <h1 className="mt-3 text-xl font-extrabold tracking-tight">
          {historical ? "Historical Chat is read-only" : "This Chat link is unavailable"}
        </h1>
        <p className="mt-3 text-sm leading-relaxed text-ink-secondary">
          {historical
            ? "This historical transcript has no proven Case association. It was not relinked or changed automatically."
            : "The workspace could not verify an owned Case association for this link. No Case was inferred from the Chat identifier."}
        </p>
        <Link href="/case" className="btn-primary mt-6 inline-flex rounded-lg">
          Open Case workspace
        </Link>
      </section>
    </main>
  );
}
