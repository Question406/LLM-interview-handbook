import type { Handbook, HandbookCatalogEntry } from "./types";

function rankHandbookId(id: string) {
  return id === "llm-interview-v2" ? 0 : 1;
}

export function validateHandbook(candidate: Handbook): Handbook {
  const questionCount = candidate.sections.reduce((total, section) => total + section.questions.length, 0);

  if (candidate.schemaVersion !== 1 || questionCount !== candidate.stats.questions) {
    throw new Error(`Invalid handbook content: ${candidate.id}`);
  }

  return {
    ...candidate,
    companies: Array.isArray(candidate.companies) ? candidate.companies : [],
    sections: candidate.sections.map((section) => ({
      ...section,
      questions: section.questions.map((question) => ({
        ...question,
        companies: Array.isArray(question.companies) ? question.companies : [],
      })),
    })),
  };
}

export function validateCatalog(candidate: HandbookCatalogEntry): HandbookCatalogEntry {
  const questionCount = candidate.sections.reduce((total, section) => total + section.questionCount, 0);
  if (candidate.schemaVersion !== 1 || questionCount !== candidate.stats.questions || !candidate.indexPath) {
    throw new Error(`Invalid handbook catalog entry: ${candidate.id}`);
  }
  return candidate;
}

export function sortHandbooks<T extends { id: string; shortTitle: string }>(handbooks: T[]): T[] {
  return [...handbooks].sort((left, right) => (
    rankHandbookId(left.id) - rankHandbookId(right.id)
    || left.shortTitle.localeCompare(right.shortTitle, "zh-Hans-CN")
  ));
}
