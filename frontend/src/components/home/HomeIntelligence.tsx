import { homeIntelligencePillars } from "./home-content";

export function HomeIntelligence() {
  return (
    <section id="intelligence" className="grid border-t border-primary/10 md:grid-cols-2">
      <div className="bg-primary px-6 py-14 text-ivory md:px-12 md:py-20">
        <p className="text-[10px] font-bold uppercase tracking-widest text-ivory/60">
          Intelligence layer
        </p>
        <h2 className="mt-5 text-4xl font-light leading-none tracking-normal md:text-6xl">
          Grounded answers,
          <br />
          not guesses.
        </h2>
        <p className="mt-7 max-w-md text-sm leading-relaxed text-ivory/70">
          Retrieval-Augmented Generation and persisted conversation context work
          together to keep answers traceable and useful.
        </p>
      </div>

      <div className="bg-surface-hover px-6 py-14 md:px-12 md:py-20">
        <div className="space-y-6">
          {homeIntelligencePillars.map(([title, description], index) => (
            <article
              key={title}
              className="flex gap-5 border-b border-primary/15 pb-6 last:border-b-0"
            >
              <span className="text-sm font-light text-red-600">0{index + 1}</span>
              <div>
                <h3 className="text-xl font-medium tracking-tight">{title}</h3>
                <p className="mt-2 max-w-md text-sm leading-relaxed text-ink-secondary">
                  {description}
                </p>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
