const THAI_CHARACTER = /[\u0E00-\u0E7F]/;

export function hasThai(text: string): boolean {
  return THAI_CHARACTER.test(text);
}
