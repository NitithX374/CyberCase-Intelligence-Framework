export interface SourceMessageRef {
  id: string;
  label: string;
  displayContent: string;
  exactQuote: string | null;
  quoteContext: QuoteContext | null;
  filename: string | null;
  pageNumbers: number[];
  sourcePages: SourcePage[];
  question: string | null;
  quoteLabel?: string;
  toleratedNotes?: string[];
  reviewNotes?: string[];
  pointerState?: SourcePointerState;
  start?: number | null;
  end?: number | null;
  passages?: CitedSourcePassage[];
}

export type SourcePointerState = "direct" | "recovered" | "unresolved" | "legacy";

export interface CitedSourcePassage {
  quote: string;
  context: QuoteContext | null;
  pointerState: SourcePointerState;
  start: number | null;
  end: number | null;
  notes: string[];
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
