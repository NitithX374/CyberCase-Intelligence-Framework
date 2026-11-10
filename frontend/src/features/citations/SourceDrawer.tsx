"use client";

import { useEffect, useRef, useState, type PointerEvent } from "react";
import * as Dialog from "@radix-ui/react-dialog";
import type { SourceMessageRef } from "./types";
import { SourceText } from "./SourceText";
import { Icon } from "@/components/icons";

export function SourceDrawer({
  sourceRef,
  anchorElement,
  citationRole,
  onClose,
}: {
  sourceRef: SourceMessageRef;
  anchorElement: HTMLElement;
  citationRole?: "supporting" | "conflicting";
  onClose: () => void;
}) {
  const windowRef = useRef<HTMLDivElement>(null);
  const anchorRef = useRef(anchorElement);
  const dragRef = useRef<{
    x: number;
    y: number;
    offset: { x: number; y: number };
    box: DOMRect;
  } | null>(null);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const sourceTitle = sourceRef.filename ?? sourceRef.label;

  useEffect(() => {
    anchorRef.current = anchorElement;
  }, [anchorElement]);

  const close = () => {
    if (anchorRef.current.isConnected) anchorRef.current.focus();
    onClose();
  };

  const startDrag = (event: PointerEvent<HTMLElement>) => {
    if (event.button !== 0 || (event.target as HTMLElement).closest("button")) return;
    const box = windowRef.current?.getBoundingClientRect();
    if (!box) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    dragRef.current = { x: event.clientX, y: event.clientY, offset, box };
  };

  const drag = (event: PointerEvent<HTMLElement>) => {
    const start = dragRef.current;
    if (!start) return;
    const dx = clamp(
      event.clientX - start.x,
      8 - start.box.left,
      window.innerWidth - 8 - start.box.right,
    );
    const dy = clamp(
      event.clientY - start.y,
      8 - start.box.top,
      window.innerHeight - 8 - start.box.bottom,
    );
    setOffset({ x: start.offset.x + dx, y: start.offset.y + dy });
  };

  return (
    <Dialog.Root open modal={false} onOpenChange={(open) => !open && close()}>
      <Dialog.Portal>
        <Dialog.Content
          ref={windowRef}
          aria-describedby={undefined}
          onInteractOutside={(event) => event.preventDefault()}
          onCloseAutoFocus={(event) => event.preventDefault()}
          style={{ transform: `translate(${offset.x}px, ${offset.y}px)` }}
          className="pop-in fixed inset-x-2 bottom-2 z-40 flex h-[min(70dvh,640px)] flex-col overflow-hidden rounded-xl border border-line-strong bg-surface text-ink shadow-[0_12px_40px_rgba(24,24,28,0.18)] outline-none [--origin:bottom_right] sm:inset-x-auto sm:right-5 sm:bottom-5 sm:w-[440px]"
        >
          <header
            onPointerDown={startDrag}
            onPointerMove={drag}
            onPointerUp={() => (dragRef.current = null)}
            onPointerCancel={() => (dragRef.current = null)}
            className="flex shrink-0 cursor-grab touch-none items-start justify-between gap-4 border-b border-line px-5 pt-4 pb-3 select-none active:cursor-grabbing"
          >
            <div className="min-w-0 space-y-0.5">
              {citationRole === "conflicting" && (
                <p className="text-xs font-medium text-critical">Conflicting source</p>
              )}
              <Dialog.Title className="text-base font-semibold leading-6 [overflow-wrap:anywhere]">
                <span className="sr-only">Source: </span>
                {sourceTitle}
              </Dialog.Title>
              {sourceRef.label !== sourceTitle && (
                <p className="text-sm text-ink-muted">{sourceRef.label}</p>
              )}
            </div>
            <Dialog.Close aria-label="Close source" className="icon-btn -mr-2">
              <Icon name="close" className="h-5 w-5" />
            </Dialog.Close>
          </header>
          <div
            className="min-h-0 flex-1 overflow-y-auto px-5 py-4"
            tabIndex={0}
            aria-label="Source text"
          >
            <SourceText sourceRef={sourceRef} />
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), Math.max(min, max));
}
