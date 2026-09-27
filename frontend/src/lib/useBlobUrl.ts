"use client";

import { useQuery, type QueryKey } from "@tanstack/react-query";
import { useCallback } from "react";

export function useBlobUrl(queryKey: QueryKey, fetchBlob: (signal: AbortSignal) => Promise<Blob>) {
  const query = useQuery({
    queryKey,
    queryFn: ({ signal }) => fetchBlob(signal),
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
  const blob = query.data;
  const attach = useCallback(
    (element: HTMLAnchorElement | HTMLIFrameElement | null) => {
      if (!element || !blob || typeof URL.createObjectURL !== "function") return;
      const url = URL.createObjectURL(blob);
      if (element instanceof HTMLAnchorElement) element.href = url;
      else element.src = url;
      return () => URL.revokeObjectURL(url);
    },
    [blob],
  );

  return { blob, attach, isLoading: query.isLoading, error: query.error, refetch: query.refetch };
}
