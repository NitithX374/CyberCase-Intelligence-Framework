import { HomeFooter } from "./HomeFooter";
import { HomeHero } from "./HomeHero";
import { HomeIntelligence } from "./HomeIntelligence";
import { HomeNavigation } from "./HomeNavigation";
import { HomePlatform } from "./HomePlatform";
import { HomeWorkflow } from "./HomeWorkflow";

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
