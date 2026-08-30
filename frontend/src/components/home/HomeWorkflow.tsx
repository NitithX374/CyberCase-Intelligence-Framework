import Link from "next/link";
import { homeWorkflowSteps } from "./home-content";

export function HomeWorkflow() {
  return (
    <section id="workflow" className="px-5 py-12 md:px-10 md:py-20">
      <div className="border border-primary bg-surface">
        <div className="flex items-center justify-between border-b border-primary px-5 py-4">
          <div className="flex items-center gap-3">
            <span className="text-sm font-light text-red-600">01</span>
            <span className="text-xs font-bold uppercase tracking-widest">Guided chat</span>
          </div>
          <Link
            href="/chat"
            className="border border-primary px-3 py-2 text-[10px] font-bold uppercase tracking-widest transition hover:bg-primary hover:text-ivory active:bg-charcoal-pressed"
          >
            Open chat
          </Link>
        </div>

        <div className="grid min-h-132.5 gap-10 px-6 py-16 md:grid-cols-[1.2fr_0.8fr] md:px-14">
          <div className="flex flex-col justify-center">
            <p className="text-[10px] font-bold uppercase tracking-widest text-primary/60">
              Context first
            </p>
            <h2 className="mt-5 text-5xl font-light leading-[0.95] tracking-normal md:text-7xl">
              Keep your
              <br />
              <span className="text-primary/25">context together.</span>
            </h2>
            <p className="mt-7 max-w-md text-sm leading-relaxed text-ink-secondary">
              CyberCase keeps the context in one thread, asks focused follow-up
              questions when something is missing, and lets you return to saved
              conversations.
            </p>
            <Link
              href="/chat"
              className="mt-9 inline-flex w-fit items-center gap-3 bg-primary px-5 py-3 text-[11px] font-bold uppercase tracking-widest text-ivory transition hover:bg-charcoal-hover active:bg-charcoal-pressed"
            >
              Start a conversation
              <span className="text-red-500">●</span>
            </Link>
          </div>

          <div className="flex flex-col justify-end border-l border-primary/10 pl-6 md:pl-10">
            {homeWorkflowSteps.map(([number, title, description]) => (
              <div
                key={number}
                className="border-t border-primary/15 py-5 first:border-t-0 first:pt-0"
              >
                <div className="flex gap-4">
                  <span className="text-xs font-bold text-red-600">{number}</span>
                  <div>
                    <h3 className="text-lg font-medium">{title}</h3>
                    <p className="mt-1 text-xs leading-relaxed text-ink-secondary">
                      {description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
