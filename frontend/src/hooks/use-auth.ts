import { useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getSession,
  devLogin,
  logout,
  getOAuthLoginUrl,
  type DevLoginPayload,
} from "@/lib/api";
import { chatQueryKeys } from "./useChatQueries";

export const authQueryKeys = {
  all: ["auth"] as const,
  session: () => [...authQueryKeys.all, "session"] as const,
};

export function useAuth() {
  const queryClient = useQueryClient();

  const sessionQuery = useQuery({
    queryKey: authQueryKeys.session(),
    queryFn: async ({ signal }) => {
      const user = await getSession(signal);
      const previous = localStorage.getItem("cybercase:account");
      if (user) {
        localStorage.setItem("cybercase:account", user.id);
        if (previous !== user.id) {
          localStorage.setItem("cybercase:session-change", String(Date.now()));
          queryClient.removeQueries({ predicate: (query) => query.queryKey[0] !== "auth" });
        }
      }
      return user;
    },
    staleTime: 0,
    refetchOnWindowFocus: true,
    refetchInterval: 60_000,
    retry: false,
  });

  useEffect(() => {
    if (sessionQuery.data) localStorage.setItem("cybercase:account", sessionQuery.data.id);
    const sync = (event: StorageEvent) => {
      if (event.key === "cybercase:session-change") window.location.reload();
    };
    window.addEventListener("storage", sync);
    return () => window.removeEventListener("storage", sync);
  }, [sessionQuery.data]);

  const devLoginMutation = useMutation({
    mutationFn: (payload: DevLoginPayload) => devLogin(payload),
    onSuccess: (data) => {
      queryClient.setQueryData(authQueryKeys.session(), data.user);
      queryClient.invalidateQueries({ queryKey: chatQueryKeys.threads() });
    },
  });

  const logoutMutation = useMutation({
    mutationFn: () => logout(),
    onSuccess: () => {
      queryClient.clear();
      localStorage.removeItem("cybercase:account");
      localStorage.setItem("cybercase:session-change", String(Date.now()));
      window.location.assign("/login");
    },
  });

  const loginWithOAuth = (provider: "google" = "google", redirect?: string) => {
    window.location.href = getOAuthLoginUrl(provider, redirect);
  };

  return {
    sessionError: sessionQuery.error,
    user: sessionQuery.data ?? null,
    isLoading: sessionQuery.isLoading,
    isAuthenticated: Boolean(sessionQuery.data),
    devLogin: devLoginMutation.mutateAsync,
    isDevLoggingIn: devLoginMutation.isPending,
    logout: logoutMutation.mutateAsync,
    isLoggingOut: logoutMutation.isPending,
    loginWithOAuth,
    refetchSession: sessionQuery.refetch,
  };
}
