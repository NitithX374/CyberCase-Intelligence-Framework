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
  const quoteStart = content.indexOf(exactQuote);
  if (quoteStart < 0) {
    return <>{content}</>;
  }
  const quoteEnd = quoteStart + exactQuote.length;
  return (
    <>
      {content.slice(0, quoteStart)}
      <mark className="rounded-sm bg-[#F4D58D]/75 px-0.5 text-inherit ring-1 ring-[#B98218]/20">
        {content.slice(quoteStart, quoteEnd)}
      </mark>
      {content.slice(quoteEnd)}
    </>
  );
}
