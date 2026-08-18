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
}

export interface HandbookSection {
  id: string;
  title: string;
  description: string;
  questions: HandbookQuestion[];
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
  stats: {
    questions: number;
    mustKnow: number;
    realInterviews: number;
    sources: number;
  };
  sections: HandbookSection[];
}
