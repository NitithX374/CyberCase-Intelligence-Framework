import Link from "next/link";

export function HomeHero() {
  const buildingHeights = [
    "h-[32%]",
    "h-[48%]",
    "h-[68%]",
    "h-[94%]",
    "h-[74%]",
    "h-[90%]",
    "h-[46%]",
  ];

  return (
    <section className="relative min-h-180 overflow-hidden px-5 pb-10 pt-20 md:min-h-205 md:px-10 md:pt-28">
      <div className="pointer-events-none absolute inset-x-0 bottom-0 flex h-[58%] items-end justify-center gap-0 opacity-80">
        {buildingHeights.map((height) => (
          <div key={height} className={`${height} w-[14%] border border-primary/10`} />
        ))}
      </div>

      <div className="relative z-10 mx-auto max-w-4xl text-center">
        <p className="text-[10px] font-bold uppercase tracking-widest text-primary/60">
          Cyber Threat Intelligence Framework
        </p>
        <h1 className="mt-7 text-5xl font-light leading-[0.94] tracking-normal sm:text-6xl md:text-8xl">
          Make every investigation
          <br />
          <span className="font-normal">clearer, faster,</span>
          <br />
          and defensible.
        </h1>
        <p className="mx-auto mt-8 max-w-xl text-sm leading-relaxed text-ink-secondary md:text-base">
          CyberCase turns fragmented incident details into a persistent
          conversation where you can ask questions, add evidence, and keep the
          reasoning in one place.
        </p>
        <div className="mt-9 flex flex-wrap justify-center gap-3">
          <Link
            href="/chat"
            className="bg-primary px-5 py-3 text-[11px] font-bold uppercase tracking-widest text-ivory transition hover:bg-charcoal-hover active:bg-charcoal-pressed"
          >
            Start a chat
          </Link>
          <a
            href="#platform"
            className="border border-primary px-5 py-3 text-[11px] font-bold uppercase tracking-widest transition hover:bg-primary hover:text-ivory active:bg-charcoal-pressed"
          >
            Explore platform
          </a>
        </div>
      </div>

      <div className="absolute bottom-7 left-5 z-10 max-w-52.5 md:bottom-10 md:left-10">
        <p className="text-[10px] font-bold uppercase tracking-widest text-primary/60">
          Evidence-led conversation
        </p>
        <p className="mt-2 text-xs leading-relaxed text-ink-secondary">
          Keep each conversation grounded in retrieved context and
          analyst-confirmed details.
        </p>
      </div>
      <div className="absolute bottom-7 right-5 z-10 text-right md:bottom-10 md:right-10">
        <p className="text-[10px] font-bold uppercase tracking-widest text-primary/60">
          Built for analysts
        </p>
        <p className="mt-2 text-xs text-ink-secondary">
          Persistent chat · Guided follow-up · Saved threads
        </p>
      </div>
    </section>
  );
}
