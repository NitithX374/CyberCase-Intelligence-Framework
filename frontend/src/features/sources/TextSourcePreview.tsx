"use client";

import { Markdown } from "@/components/Markdown";
import { Paper } from "./Paper";

export function TextSourcePreview({ question, text }: { question: string | null; text: string }) {
  return (
    <div className="h-full overflow-auto p-4 sm:p-8">
      <div className="mx-auto max-w-3xl">
        <Paper>
          {question ? (
            <dl className="space-y-6">
              <div>
                <dt className="text-xs font-medium text-ink-muted">Question</dt>
                <dd className="mt-1.5 whitespace-pre-wrap break-words text-[15px] leading-8 text-ink-secondary">
                  {question}
                </dd>
              </div>
              <div>
                <dt className="text-xs font-medium text-ink-muted">Answer</dt>
                <dd className="mt-1.5 break-words text-[15px] leading-8 text-ink">
                  <Markdown content={text} allowHtml />
                </dd>
              </div>
            </dl>
          ) : (
            <Markdown content={text} allowHtml />
          )}
        </Paper>
      </div>
    </div>
  );
}
