"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AccountGate } from "@/components/auth/AccountGate";
import { ReactNode, useState } from "react";

export default function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            refetchOnWindowFocus: false,
            staleTime: 15_000,
          },
        },
      }),
  );

  return <QueryClientProvider client={queryClient}><AccountGate>{children}</AccountGate></QueryClientProvider>;
}
