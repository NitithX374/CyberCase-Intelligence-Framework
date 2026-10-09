"use client";

import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import remarkGfm from "remark-gfm";

interface MarkdownProps {
  content: string;
  allowHtml?: boolean;
}

export function Markdown({ content, allowHtml = false }: MarkdownProps) {
  const rehypePlugins = allowHtml ? [rehypeRaw] : [];

  return (
    <div className="text-[15px] leading-7 text-ink">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={rehypePlugins}
        components={{
          h1: ({ children }) => (
            <h1 className="mt-5 mb-2 text-lg font-semibold tracking-tight text-ink first:mt-0">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="mt-4 mb-2 text-base font-semibold tracking-tight text-ink first:mt-0">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="mt-3.5 mb-1.5 text-[15px] font-semibold text-ink first:mt-0">
              {children}
            </h3>
          ),
          h4: ({ children }) => (
            <h4 className="mt-3 mb-1.5 text-[15px] font-semibold text-ink first:mt-0">
              {children}
            </h4>
          ),
          h5: ({ children }) => (
            <h5 className="mt-2 mb-1 text-sm font-semibold text-ink-secondary first:mt-0">
              {children}
            </h5>
          ),
          h6: ({ children }) => (
            <h6 className="mt-2 mb-1 text-xs font-semibold text-ink-secondary first:mt-0">
              {children}
            </h6>
          ),
          p: ({ children }) => (
            <p className="mb-3 text-[15px] leading-7 text-ink break-words last:mb-0">{children}</p>
          ),
          ul: ({ children }) => (
            <ul className="mb-3 space-y-1 pl-5 list-disc text-[15px] leading-7 text-ink last:mb-0 marker:text-ink-muted">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="mb-3 space-y-1 pl-5 list-decimal text-[15px] leading-7 text-ink last:mb-0 marker:text-ink-muted font-sans">
              {children}
            </ol>
          ),
          li: ({ children }) => <li className="pl-1 break-words">{children}</li>,
          strong: ({ children }) => <strong className="font-semibold text-ink">{children}</strong>,
          blockquote: ({ children }) => (
            <blockquote className="my-3 border-l-2 border-line-strong py-0.5 pl-4 text-ink-secondary">
              {children}
            </blockquote>
          ),
          pre: ({ children }) => (
            <pre className="my-3 max-w-full overflow-x-auto rounded-lg bg-primary p-4 font-mono text-[13px] leading-relaxed text-ivory">
              {children}
            </pre>
          ),
          code: ({ className, children, ...props }) => {
            const match = /language-(\w+)/.exec(className || "");
            const isCodeBlock = match || String(children).includes("\n");
            if (isCodeBlock) {
              return (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            }
            return (
              <code
                className="rounded bg-surface-hover px-1.5 py-0.5 font-mono text-[13px] text-ink break-words"
                {...props}
              >
                {children}
              </code>
            );
          },
          table: ({ children }) => (
            <div className="my-3 max-w-full overflow-x-auto rounded-lg border border-line bg-surface">
              <table className="w-full border-collapse text-left text-sm">{children}</table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="border-b border-line bg-surface-nested text-ink">{children}</thead>
          ),
          tbody: ({ children }) => <tbody className="divide-y divide-line">{children}</tbody>,
          tr: ({ children, className, ...props }: React.ComponentPropsWithoutRef<"tr">) => (
            <tr
              className={`transition-colors hover:bg-surface-hover ${className ?? ""}`.trim()}
              {...props}
            >
              {children}
            </tr>
          ),
          th: ({ children, className, ...props }: React.ComponentPropsWithoutRef<"th">) => (
            <th
              className={`px-3 py-2 text-left text-xs font-semibold text-ink-secondary ${className ?? ""}`.trim()}
              {...props}
            >
              {children}
            </th>
          ),
          td: ({ children, className, ...props }: React.ComponentPropsWithoutRef<"td">) => (
            <td
              className={`px-3 py-2 text-ink break-words ${className ?? ""}`.trim()}
              {...props}
            >
              {children}
            </td>
          ),
          script: () => null,
          iframe: () => null,
          img: ({ alt }) => (alt ? <span>{alt}</span> : null),
          a: ({ href, children }) => {
            const isSafe = href && !/^javascript:/i.test(href.trim());
            return (
              <a
                href={isSafe ? href : undefined}
                target="_blank"
                rel="noopener noreferrer"
                className="font-semibold text-ink underline decoration-line-strong underline-offset-2 transition-colors hover:text-charcoal-hover hover:decoration-primary"
              >
                {children}
              </a>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
