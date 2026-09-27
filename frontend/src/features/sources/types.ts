export interface SourceMessageRef {
  id: string;
  label: string;
  excerpt: string;
  displayContent: string;
  exactQuote: string | null;
  filename: string | null;
  pageNumbers: number[];
  sourcePages: SourcePage[];
  question: string | null;
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
