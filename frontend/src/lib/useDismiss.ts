import { useEffect, type RefObject } from "react";

/** Close a menu or popover on a click outside it, or on Escape. */
export function useDismiss(ref: RefObject<HTMLElement | null>, isOpen: boolean, close: () => void) {
  useEffect(() => {
    if (!isOpen) return;
    const dismiss = (event: MouseEvent) => {
      if (!ref.current?.contains(event.target as Node)) close();
    };
    const escape = (event: KeyboardEvent) => {
      if (event.key === "Escape") close();
    };
    document.addEventListener("mousedown", dismiss);
    document.addEventListener("keydown", escape);
    return () => {
      document.removeEventListener("mousedown", dismiss);
      document.removeEventListener("keydown", escape);
    };
  }, [close, isOpen, ref]);
}
