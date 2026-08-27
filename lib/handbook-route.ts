import type { HandbookCatalogEntry } from "@/content/types";

export type HandbookSearch = {
  book: string | null;
  section: string | null;
  question: string | null;
  view: "guide" | null;
};

export const EMPTY_SEARCH: HandbookSearch = {
  book: null,
  section: null,
  question: null,
  view: null,
};

export function parseHandbookSearch(search: string): HandbookSearch {
  const params = new URLSearchParams(search.startsWith("?") ? search.slice(1) : search);
  const view = params.get("view");
  return {
    book: emptyToNull(params.get("book")),
    section: emptyToNull(params.get("section")),
    question: emptyToNull(params.get("question")),
    view: view === "guide" ? "guide" : null,
  };
}

export function serializeHandbookSearch(route: HandbookSearch, catalog: HandbookCatalogEntry[]): string {
  const params = new URLSearchParams();
  const entry = resolveCatalogEntry(catalog, route.book) ?? catalog[0];
  if (entry) params.set("book", entry.slug);
  if (route.view === "guide") params.set("view", "guide");
  if (route.section) params.set("section", route.section);
  if (route.question) params.set("question", route.question);
  const text = params.toString();
  return text ? `?${text}` : "";
}

export function resolveCatalogEntry(
  catalog: HandbookCatalogEntry[],
  book: string | null | undefined,
): HandbookCatalogEntry | undefined {
  if (!book) return undefined;
  return catalog.find((entry) => entry.id === book || entry.slug === book);
}

function emptyToNull(value: string | null): string | null {
  return value && value.trim() ? value.trim() : null;
}
