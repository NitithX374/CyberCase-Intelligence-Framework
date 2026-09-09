"use client";

import { useEffect, useState } from "react";
import { readAccountValue, writeAccountValue } from "@/lib/account-storage";

export function useAccountState<T>(key: string, initial: T) {
  const [value, setValue] = useState<T>(() => {
    const saved = readAccountValue(key);
    return saved === null ? initial : JSON.parse(saved) as T;
  });
  useEffect(() => { writeAccountValue(key, JSON.stringify(value)); }, [key, value]);
  return [value, setValue] as const;
}
