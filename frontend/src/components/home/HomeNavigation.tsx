import Link from "next/link";

export function HomeNavigation() {
  return (
    <header className="flex items-center justify-between border-b border-primary/10 px-5 py-4 md:px-8">
      <Link href="/" className="flex items-center gap-2 font-semibold tracking-tight">
        <span className="grid h-6 w-6 place-items-center bg-primary text-xs font-black text-ivory">
          C
        </span>
        <span>CyberCase Framework</span>
      </Link>

      <nav className="hidden items-center gap-7 text-[11px] font-bold uppercase tracking-widest text-primary/60 md:flex">
        <a href="#platform" className="transition hover:text-primary">
          Platform
        </a>
        <a href="#workflow" className="transition hover:text-primary">
          Workflow
        </a>
        <a href="#intelligence" className="transition hover:text-primary">
          Intelligence
        </a>
        <a href="#about" className="transition hover:text-primary">
          About
        </a>
      </nav>

      <div className="flex items-center gap-3">
        <Link
          href="/chat"
          className="hidden text-[11px] font-bold uppercase tracking-wider text-primary/60 hover:text-primary sm:block"
        >
          Open chat
        </Link>
        <Link
          href="/chat"
          className="flex items-center gap-3 bg-primary px-4 py-2 text-[10px] font-bold uppercase tracking-widest text-ivory transition hover:bg-charcoal-hover active:bg-charcoal-pressed"
        >
          Start case
          <span className="h-1.5 w-1.5 rounded-full bg-red-500" />
        </Link>
      </div>
    </header>
  );
}
