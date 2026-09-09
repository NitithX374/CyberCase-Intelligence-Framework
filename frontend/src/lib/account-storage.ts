export function accountStorageKey(key: string): string {
  const account = localStorage.getItem("cybercase:account");
  return `cybercase:${account ?? "signed-out"}:${key}`;
}

export function readAccountValue(key: string): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(accountStorageKey(key));
}

export function writeAccountValue(key: string, value: string): void {
  localStorage.setItem(accountStorageKey(key), value);
}
