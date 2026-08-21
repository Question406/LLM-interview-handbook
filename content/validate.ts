import type { Handbook } from "./types";

export function validateHandbook(candidate: Handbook): Handbook {
  const questionCount = candidate.sections.reduce((total, section) => total + section.questions.length, 0);

  if (candidate.schemaVersion !== 1 || questionCount !== candidate.stats.questions) {
    throw new Error(`Invalid handbook content: ${candidate.id}`);
  }

  return candidate;
}

export function sortHandbooks(handbooks: Handbook[]): Handbook[] {
  return [...handbooks].sort((left, right) => {
    const rank = (id: string) => (id === "llm-interview-v2" ? 0 : 1);
    return rank(left.id) - rank(right.id) || left.shortTitle.localeCompare(right.shortTitle, "zh-Hans-CN");
  });
}
