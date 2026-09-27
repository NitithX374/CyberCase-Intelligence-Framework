import { http } from "@/lib/api/http";
import type { PasswordLoginRequest, RegisterRequest, UserRead } from "@/lib/api/types";

export async function login(request: PasswordLoginRequest): Promise<UserRead> {
  return (await http.post<UserRead>("/auth/login", request)).data;
}

export async function register(request: RegisterRequest): Promise<UserRead> {
  return (await http.post<UserRead>("/auth/register", request)).data;
}

export async function getSession(signal?: AbortSignal): Promise<UserRead | null> {
  return (await http.get<UserRead | null>("/auth/session", { signal })).data;
}

export async function logout(): Promise<void> {
  await http.post("/auth/logout", {});
}
