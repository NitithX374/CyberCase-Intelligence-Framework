import Link from "next/link";

export function HomeFooter() {
  return (
    <footer
      id="about"
      className="flex flex-col gap-5 border-t border-primary/10 px-5 py-7 text-xs text-ink-secondary md:flex-row md:items-center md:justify-between md:px-10"
    >
      <p>CyberCase Intelligence Framework</p>
      <div className="flex gap-5">
        <Link href="/chat" className="hover:text-primary">
          Workspace
        </Link>
        <a href="#platform" className="hover:text-primary">
          Platform
        </a>
      </div>
      <p>Built for evidence-led cyber conversations.</p>
    </footer>
  );
}
