import type { Handbook, HandbookQuestion } from "@/content/types";
import { qualifiedId } from "./handbook";

export type FilterId = "all" | "S" | "A" | "B" | "real" | "mastered" | "unmastered";

export type FilterOption = {
  id: FilterId;
  label: string;
  kind: "all" | "level" | "flag" | "progress";
};

export const FILTERS: FilterOption[] = [
  { id: "all", label: "全部", kind: "all" },
  { id: "S", label: "S 级", kind: "level" },
  { id: "A", label: "A 级", kind: "level" },
  { id: "B", label: "B 级", kind: "level" },
  { id: "real", label: "真实面经", kind: "flag" },
  { id: "mastered", label: "已掌握", kind: "progress" },
  { id: "unmastered", label: "未掌握", kind: "progress" },
];

export function isFilterId(value: string): value is FilterId {
  return FILTERS.some((filter) => filter.id === value);
}

export function filtersForHandbook(handbook: Handbook): FilterOption[] {
  const levels = new Set(handbook.sections.flatMap((section) => section.questions.map((question) => question.level)));
  return FILTERS.filter((filter) => filter.kind !== "level" || levels.has(filter.id));
}

export function questionMatchesFilter(
  question: HandbookQuestion,
  filter: FilterId,
  handbookId: string,
  mastered: ReadonlySet<string>,
): boolean {
  if (filter === "all") return true;
  if (filter === "S" || filter === "A" || filter === "B") return question.level === filter;
  if (filter === "real") return question.isRealInterview;
  const key = qualifiedId(handbookId, question.id);
  if (filter === "mastered") return mastered.has(key);
  if (filter === "unmastered") return !mastered.has(key);
  return true;
}

export function questionMatchesQuery(question: HandbookQuestion, normalizedQuery: string): boolean {
  if (!normalizedQuery) return true;
  return `${question.searchText} ${question.title} ${question.quick} ${question.tags.join(" ")}`
    .toLocaleLowerCase()
    .includes(normalizedQuery);
}
