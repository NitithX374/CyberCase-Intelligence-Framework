import type { PersistedChatMessage } from "@/lib/api";
import { ExtractedTextPreview } from "./ExtractedTextPreview";

export function ExistingCaseRecord({ message, text, filename }: {
  message?: PersistedChatMessage;
  text?: string;
  filename?: string;
}) {
  return (
    <section className="workspace-card min-w-0 space-y-4 p-5 sm:p-6">
      <div>
        <h2 className="text-base font-bold text-ink">Case information</h2>
        <p className="mt-1 break-words text-xs text-ink-secondary">{filename ?? "Submitted case narrative"}</p>
        {message && <p className="mt-1 text-[11px] text-ink-muted">Submitted {new Date(message.created_at).toLocaleString("en-GB")}</p>}
      </div>
      <ExtractedTextPreview key={filename ?? message?.id} text={text ?? message?.content ?? ""} label="Case narrative" />
    </section>
  );
}
