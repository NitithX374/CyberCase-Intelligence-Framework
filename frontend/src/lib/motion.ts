"use client";

import { useEffect, useLayoutEffect, useRef, type RefObject } from "react";

export const EASE_OUT = "cubic-bezier(0.16, 1, 0.3, 1)";

export function motionAllowed(): boolean {
  return (
    typeof window !== "undefined" &&
    typeof window.matchMedia === "function" &&
    window.matchMedia("(prefers-reduced-motion: no-preference)").matches
  );
}

export function useEnterOnChange(ref: RefObject<HTMLElement | null>, key: string) {
  const first = useRef(true);
  useEffect(() => {
    const element = ref.current;
    const isFirst = first.current;
    first.current = false;
    if (!element || !motionAllowed() || typeof element.animate !== "function") return;
    element.animate(
      [
        { opacity: 0, transform: isFirst ? "translateY(8px)" : "translateY(6px)" },
        { opacity: 1, transform: "none" },
      ],
      { duration: 280, easing: EASE_OUT },
    );
  }, [ref, key]);
}

export function useCountUp(ref: RefObject<HTMLElement | null>, value: number, duration = 500) {
  const shown = useRef(0);
  useLayoutEffect(() => {
    const element = ref.current;
    if (!element) return;
    const from = shown.current;
    shown.current = value;
    if (from === value || !motionAllowed()) {
      element.textContent = String(value);
      return;
    }
    const began = performance.now();
    let frame = 0;
    const tick = (now: number) => {
      const progress = Math.min(1, (now - began) / duration);
      const eased = 1 - Math.pow(1 - progress, 3);
      element.textContent = String(Math.round(from + (value - from) * eased));
      if (progress < 1) frame = requestAnimationFrame(tick);
    };
    element.textContent = String(from);
    frame = requestAnimationFrame(tick);
    return () => {
      cancelAnimationFrame(frame);
      element.textContent = String(value);
    };
  }, [ref, value, duration]);
}
