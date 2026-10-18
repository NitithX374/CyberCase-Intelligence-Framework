"use client";

import type { CaseAnalysisResultRead, CaseSourceRead } from "@/lib/api/types";
import { Icon } from "@/components/icons";
import { SourceDrawer } from "@/features/citations/SourceDrawer";
import { useSourceDrawer } from "@/features/citations/useSourceDrawer";
import type { SourceMessageRef } from "@/features/citations/types";
import { buildTechnicalContext, technicalContextMessage } from "./technicalContext";
import { TechnicalItem } from "./TechnicalItem";
import { RetrievedOnlyItem } from "./RetrievedOnlyItem";

interface TechnicalContextViewProps {
  analysisResult: CaseAnalysisResultRead;
  sources: CaseSourceRead[] | null;
}

export function TechnicalContextView({ analysisResult, sources }: TechnicalContextViewProps) {
  const contextData = buildTechnicalContext(analysisResult, sources);
  const drawer = useSourceDrawer();
  const handleSelectSource = (
    sourceRef: SourceMessageRef,
    anchorElement: HTMLElement,
    key: string,
  ) => drawer.toggle({ sourceRef, anchorElement, key });

  const message = technicalContextMessage(contextData);
  const retrievedOnly = contextData.retrievedOnlyTechniques;
  const count = contextData.techniques.length || retrievedOnly.length;

  return (
    <section
      id="workspace-technical-context-panel"
      aria-label="Technical Context"
      className="flex shrink-0 flex-col bg-surface"
    >
      <div className="mx-auto w-full max-w-[52rem] px-5 pt-16 sm:px-8">
        <header className="flex flex-wrap items-center justify-between gap-3 border-b border-line pb-3">
          <div className="flex items-baseline gap-2">
            <h2 className="text-base font-semibold text-ink">MITRE ATT&amp;CK</h2>
            {count > 0 && <span className="text-[13px] font-medium text-ink-muted">{count}</span>}
          </div>
          <a
            href="https://attack.mitre.org/"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-[13px] text-ink-muted transition-colors hover:text-ink hover:underline"
            title="Open MITRE ATT&CK website"
          >
            <span>External reference</span>
            <Icon name="external" className="h-3 w-3" />
          </a>
        </header>

        {!contextData.hasContext ? (
          <p className="py-5 text-sm text-ink-muted" role="status">
            {message}
          </p>
        ) : (
          <>
            {message && (
              <p className="pt-5 text-sm text-ink-muted" role="status">
                {message}
                {contextData.failureCode && (
                  <span className="ml-2 font-mono text-xs text-critical">
                    {contextData.failureCode}
                  </span>
                )}
              </p>
            )}

            {contextData.techniques.length > 0 && (
              <div className="divide-y divide-line">
                {contextData.techniques.map((item) => (
                  <TechnicalItem
                    key={item.associationId}
                    item={item}
                    onSelectSource={handleSelectSource}
                    activeSourceKey={drawer.openKey}
                  />
                ))}
              </div>
            )}

            {retrievedOnly.length > 0 &&
              (contextData.techniques.length > 0 ? (
                <details className="group border-t border-line py-3">
                  <summary className="inline-flex h-8 cursor-pointer list-none items-center gap-1 rounded-md text-[13px] font-medium text-ink-secondary hover:text-ink">
                    Also retrieved, not linked to the case
                    <span className="text-ink-muted">{retrievedOnly.length}</span>
                    <Icon
                      name="chevron"
                      className="h-4 w-4 transition-transform group-open:rotate-180"
                    />
                  </summary>
                  <ul className="divide-y divide-line">
                    {retrievedOnly.map((item) => (
                      <RetrievedOnlyItem key={item.techniqueId} item={item} />
                    ))}
                  </ul>
                </details>
              ) : (
                <ul className="mt-2 divide-y divide-line">
                  {retrievedOnly.map((item) => (
                    <RetrievedOnlyItem key={item.techniqueId} item={item} />
                  ))}
                </ul>
              ))}

            {contextData.techniques.some((item) => item.retrievalScore !== null) && (
              <p className="border-t border-line pt-3 text-xs text-ink-muted">
                Scores show retrieval similarity, not whether a mapping is right.
              </p>
            )}
          </>
        )}
      </div>

      {drawer.open && (
        <SourceDrawer
          sourceRef={drawer.open.sourceRef}
          anchorElement={drawer.open.anchorElement}
          onClose={drawer.close}
        />
      )}
    </section>
  );
}
