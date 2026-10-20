import type { HandbookQuestion } from "@/content/types";

const GUIDE_TAGS = new Set(["备考地图", "真题导航"]);
const GUIDE_ID = /-(index|prep-map|prep-list)$/;

export function isGuideQuestion(question: HandbookQuestion): boolean {
  if (question.tags.some((tag) => GUIDE_TAGS.has(tag))) return true;
  return GUIDE_ID.test(question.id);
}

function practiceFirst(questions: HandbookQuestion[]): HandbookQuestion[] {
  return [
    ...questions.filter((question) => question.tags.includes("完整编程练习")),
    ...questions.filter((question) => !question.tags.includes("完整编程练习")),
  ];
}

export function sortSFirst(questions: HandbookQuestion[]): HandbookQuestion[] {
  const must = questions.filter((question) => question.level === "S");
  const rest = questions.filter((question) => question.level !== "S");
  return [...must, ...rest];
}

export function arrangeStudySections<T extends { questions: HandbookQuestion[] }>(sections: T[]): {
  pinned: HandbookQuestion[];
  sections: T[];
} {
  const pinned = sections.flatMap((section) => section.questions.filter(isGuideQuestion));
  const pinnedIds = new Set(pinned.map((question) => question.id));
  if (pinned.length > 0) {
    return {
      pinned,
      sections: sections
        .map((section) => ({ ...section, questions: practiceFirst(section.questions.filter((question) => !pinnedIds.has(question.id))) }))
        .filter((section) => section.questions.length > 0),
    };
  }
  return {
    pinned: [],
    sections: sections.map((section) => ({ ...section, questions: practiceFirst(sortSFirst(section.questions)) })),
  };
}
