"use client";

import type { SourcesAnalysis } from "./CaseSourcesView";
import type { RailGroup } from "./railItems";
import { AnalyzeFooter } from "./AnalyzeFooter";
import { RailButton } from "./RailButton";
import { UploadingItem } from "./UploadingItem";
import { AddSourceMenu } from "./AddSourceMenu";

interface SourceRailProps {
  groups: RailGroup[];
  selectedId: string | null;
  isUploading: boolean;
  uploadingFilename?: string | null;
  onSelect: (id: string) => void;
  onOpenNarrative: () => void;
  onPickFile: () => void;
  analysis?: SourcesAnalysis;
}

export function SourceRail({
  groups,
  selectedId,
  isUploading,
  uploadingFilename,
  onSelect,
  onOpenNarrative,
  onPickFile,
  analysis,
}: SourceRailProps) {
  const total = groups.reduce((count, group) => count + group.items.length, 0);
  const shown = total + (isUploading ? 1 : 0);

  return (
    <aside className="flex max-h-72 w-full shrink-0 flex-col border-b border-line bg-sidebar md:max-h-none md:w-72 md:border-r md:border-b-0">
      <header className="flex h-12 shrink-0 items-center justify-between pr-2 pl-4">
        <h2 className="flex items-baseline gap-2 text-[13px] font-semibold text-ink">
          Sources <span className="font-medium text-ink-muted">{shown}</span>
        </h2>
        <AddSourceMenu
          isUploading={isUploading}
          isAnalysing={analysis?.isRunning ?? false}
          onOpenNarrative={onOpenNarrative}
          onPickFile={onPickFile}
        />
      </header>

      <div className="min-h-0 flex-1 space-y-5 overflow-auto px-2 pb-4">
        {isUploading && <UploadingItem filename={uploadingFilename} />}
        {groups.map((group) => (
          <section key={group.label}>
            <h3 className="px-2 pb-1 text-xs font-medium text-ink-muted">{group.label}</h3>
            <ul className="space-y-0.5">
              {group.items.map((item) => (
                <li key={item.id}>
                  <RailButton
                    item={item}
                    selected={item.id === selectedId}
                    onSelect={() => onSelect(item.id)}
                  />
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>

      {analysis && <AnalyzeFooter analysis={analysis} isUploading={isUploading} />}
    </aside>
  );
}
