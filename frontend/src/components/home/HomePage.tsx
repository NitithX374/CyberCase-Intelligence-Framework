import {
  HomeFooter,
  HomeHero,
  HomeIntelligence,
  HomeNavigation,
  HomePlatform,
  HomeWorkflow,
} from "./HomeSections";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-line-strong text-primary">
      <div className="mx-auto overflow-hidden bg-ivory shadow-2xl">
        <HomeNavigation />
        <HomeHero />
        <HomePlatform />
        <HomeWorkflow />
        <HomeIntelligence />
        <HomeFooter />
      </div>
    </main>
  );
}
