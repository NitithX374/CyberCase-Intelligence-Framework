import { redirect } from "next/navigation";

interface PageProps {
  params: Promise<{ threadId: string }>;
}

export default async function ThreadSpecificChatPage({ params }: PageProps) {
  const { threadId } = await params;
  redirect(`/chat/${encodeURIComponent(threadId)}/overview`);
}
