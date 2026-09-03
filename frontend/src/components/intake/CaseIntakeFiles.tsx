import type { ReactNode } from "react";
import type { IntakeMaterial } from "@/lib/case-intake-model";

export function CaseIntakeFiles({ materials, selectedId, onSelect, children, onOpenMaterials }: {
  materials: IntakeMaterial[];
  selectedId: string | null;
  onSelect: (material: IntakeMaterial) => void;
  children: ReactNode;
  onOpenMaterials?: () => void;
}) {
  return (
    <aside aria-labelledby="intake-files-heading" className="order-first min-w-0 space-y-4 lg:sticky lg:top-5 lg:order-last">
      <h2 id="intake-files-heading" className="text-sm font-bold text-ink">Case Materials</h2>
      {children}
      {materials.length === 0 ? (
        <p className="border-t border-line pt-4 text-xs leading-relaxed text-ink-muted">No documents added. You can also begin with a written narrative.</p>
      ) : (
        <ul className="divide-y divide-line border-y border-line" aria-live="polite">
          {materials.map((item) => (
            <li key={item.id} className="py-3">
              {item.text ? (
                <button type="button" onClick={() => onSelect(item)} aria-pressed={selectedId === item.id} className="block w-full break-words text-left text-xs font-semibold leading-relaxed text-ink underline decoration-line-strong underline-offset-4 hover:decoration-ink focus-visible:outline-2">
                  {item.filename}
                </button>
              ) : <p className="break-words text-xs font-semibold leading-relaxed text-ink">{item.filename}</p>}
              <p className="mt-1 text-[11px] leading-relaxed text-ink-secondary">{item.status}</p>
              {item.pageCount !== null && <p className="mt-1 text-[11px] text-ink-muted">{item.pageCount} {item.pageCount === 1 ? "page" : "pages"}</p>}
            </li>
          ))}
        </ul>
      )}
      {onOpenMaterials && <button type="button" onClick={onOpenMaterials} className="min-h-9 text-xs text-ink-secondary underline underline-offset-4 hover:text-ink">Open case materials →</button>}
    </aside>
  );
}
