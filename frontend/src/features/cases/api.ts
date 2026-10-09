import { caseUrl, http } from "@/lib/api/http";
import type { CaseRead } from "@/lib/api/types";

export async function listCases(signal?: AbortSignal): Promise<CaseRead[]> {
  return (await http.get<CaseRead[]>("/cases", { signal })).data;
}

export async function createCase(): Promise<CaseRead> {
  return (await http.post<CaseRead>("/cases", { title: "New case" })).data;
}

export async function getCase(caseId: string, signal?: AbortSignal): Promise<CaseRead> {
  return (await http.get<CaseRead>(caseUrl(caseId), { signal })).data;
}

export async function updateCase(caseId: string, title: string): Promise<CaseRead> {
  return (await http.patch<CaseRead>(caseUrl(caseId), { title })).data;
}

export async function deleteCase(caseId: string): Promise<void> {
  await http.delete(caseUrl(caseId));
}
