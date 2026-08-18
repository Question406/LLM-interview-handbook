import llmInterviewV2 from "./handbooks/llm-interview-v2.json";
import type { Handbook } from "./types";

function validateHandbook(candidate: Handbook): Handbook {
  const questionCount = candidate.sections.reduce((total, section) => total + section.questions.length, 0);

  if (candidate.schemaVersion !== 1 || questionCount !== candidate.stats.questions) {
    throw new Error(`Invalid handbook content: ${candidate.id}`);
  }

  return candidate;
}

export const handbooks: Handbook[] = [validateHandbook(llmInterviewV2 as Handbook)];
