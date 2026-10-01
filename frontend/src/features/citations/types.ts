export interface SourceMessageRef {
  id: string;
  label: string;
  excerpt: string;
  displayContent: string;
  exactQuote: string | null;
  quoteContext: QuoteContext | null;
  filename: string | null;
  pageNumbers: number[];
  sourcePages: SourcePage[];
  question: string | null;
}

export interface QuoteContext {
  before: string;
  after: string;
  cutBefore: boolean;
  cutAfter: boolean;
}

export interface SourcePage {
  pageNumber: number;
  text: string;
}

export interface FollowupAnswer {
  qaId: string;
  question: string;
  answer: string;
}

export interface CaseSourceRef {
  id: string;
  kind: string;
  ordinal: number;
  text: string;
  pages: SourcePage[];
  filename: string | null;
  question: string | null;
}
