import { HomeMiniVisual } from "./HomeMiniVisual";
import { homePillars } from "./home-content";

export function HomePlatform() {
  return (
    <section id="platform" className="bg-primary px-5 py-10 text-ivory md:px-10 md:py-16">
      <div className="flex flex-col gap-6 border-b border-ivory/10 pb-8 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-widest text-ivory/60">
            CyberCase platform
          </p>
          <h2 className="mt-4 max-w-2xl text-4xl font-light leading-none tracking-normal md:text-6xl">
            From an open question
            <br />
            to a clear next step.
          </h2>
        </div>
        <p className="max-w-xs text-sm leading-relaxed text-ivory/70">
          A persistent workflow for asking, clarifying, and returning to every
          saved conversation.
        </p>
      </div>

      <div className="mt-8 grid gap-4 md:grid-cols-3">
        {homePillars.map((pillar) => (
          <article
            key={pillar.number}
            className="group min-h-90 border border-ivory/15 bg-charcoal-pressed p-5 transition hover:-translate-y-1 hover:border-ivory/50"
          >
            <div className="flex items-center justify-between">
              <span className="text-sm font-light text-ivory/70">{pillar.number}</span>
              <span className="text-[10px] font-bold uppercase tracking-widest text-ivory/60">
                {pillar.label}
              </span>
            </div>
            <HomeMiniVisual type={pillar.type} />
            <div className="mt-10">
              <h3 className="text-3xl font-light tracking-normal">{pillar.title}</h3>
              <p className="mt-4 max-w-xs text-sm leading-relaxed text-ivory/70">
                {pillar.description}
              </p>
            </div>
            <div className="mt-8 flex items-center justify-between border-t border-ivory/10 pt-4 text-[10px] font-bold uppercase tracking-widest text-ivory/65">
              <span>Explore module</span>
              <span className="text-red-500">↗</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
