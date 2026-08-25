export type QuestionLevel = "S" | "A" | "B" | string;

export interface HandbookQuestion {
  id: string;
  level: QuestionLevel;
  sectionId: string;
  title: string;
  quick: string;
  tags: string[];
  isRealInterview: boolean;
  searchText: string;
  answerPath: string;
  titleHtml?: string;
  quickHtml?: string;
}

export interface HandbookSectionSummary {
  id: string;
  title: string;
  description: string;
  questionCount: number;
}

export interface HandbookSection {
  id: string;
  title: string;
  description: string;
  cardsPath: string;
  answerPath: string;
  questions: HandbookQuestion[];
}

export interface HandbookStats {
  questions: number;
  mustKnow: number;
  realInterviews: number;
  sources: number;
}

export interface HandbookCatalogEntry {
  schemaVersion: 1;
  id: string;
  slug: string;
  title: string;
  shortTitle: string;
  edition: string;
  audience: string;
  description: string;
  updatedAt: string;
  stats: HandbookStats;
  indexPath: string;
  sections: HandbookSectionSummary[];
}

export interface Handbook {
  schemaVersion: 1;
  id: string;
  slug: string;
  title: string;
  shortTitle: string;
  edition: string;
  audience: string;
  description: string;
  updatedAt: string;
  stats: HandbookStats;
  sections: HandbookSection[];
}

export interface QuestionCardHtml {
  titleHtml: string;
  quickHtml: string;
}
