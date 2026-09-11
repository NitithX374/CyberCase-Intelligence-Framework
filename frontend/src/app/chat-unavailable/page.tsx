import { LegacyChatRouteStateView } from "@/features/chat/routing/LegacyChatRouteStateView";

interface PageProps {
  searchParams: Promise<{ status?: string }>;
}

export default async function ChatUnavailablePage({ searchParams }: PageProps) {
  const params = await searchParams;
  const state = params.status === "historical_unavailable"
    ? "historical_unavailable"
    : "unavailable";
  return <LegacyChatRouteStateView state={state} />;
}
