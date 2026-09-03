import { Fragment } from "react";

interface HighlightedEvidenceTextProps {
  content: string;
  exactQuote: string | null;
}

export function HighlightedEvidenceText({
  content,
  exactQuote,
}: HighlightedEvidenceTextProps) {
  if (!exactQuote) {
    return <>{content}</>;
  }
  const segments = content.split(exactQuote);
  if (segments.length === 1) {
    return <>{content}</>;
  }
  return (
    <>
      {segments.map((segment, index) => (
        <Fragment key={index}>
          {segment}
          {index < segments.length - 1 && (
            <mark className="rounded-sm bg-[#F4D58D]/75 px-0.5 text-inherit ring-1 ring-[#B98218]/20">
              {exactQuote}
            </mark>
          )}
        </Fragment>
      ))}
    </>
  );
}
