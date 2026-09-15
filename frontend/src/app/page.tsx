"use client";

import {
  HomeFooter,
  HomeHero,
  HomeIntelligence,
  HomeNavigation,
  HomePlatform,
  HomeWorkflow,
} from "@/components/home/HomeSections";

export default function Home() {
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
