"use client";

import { useQuery, type QueryKey } from "@tanstack/react-query";
import { useEffect, useMemo } from "react";

export function useBlobUrl(queryKey: QueryKey, fetchBlob: (signal: AbortSignal) => Promise<Blob>) {
  const query = useQuery({
    queryKey,
    queryFn: ({ signal }) => fetchBlob(signal),
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
  const url = useMemo(() => {
    if (!query.data || typeof URL.createObjectURL !== "function") return null;
    return URL.createObjectURL(query.data);
  }, [query.data]);

  useEffect(
    () => () => {
      if (url) URL.revokeObjectURL(url);
    },
    [url],
  );

  return { url, isLoading: query.isLoading, error: query.error, refetch: query.refetch };
}
