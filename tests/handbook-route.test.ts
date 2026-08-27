import assert from "node:assert/strict";
import test from "node:test";
import { parseHandbookSearch, resolveCatalogEntry, serializeHandbookSearch } from "../lib/handbook-route.ts";
import type { HandbookCatalogEntry } from "../content/types.ts";

const catalog: HandbookCatalogEntry[] = [
  {
    schemaVersion: 1 as const,
    id: "llm-interview-v2",
    slug: "llm-interview",
    title: "LLM",
    shortTitle: "LLM",
    edition: "V2",
    audience: "",
    description: "",
    updatedAt: "2026-08-01",
    stats: { questions: 1, mustKnow: 1, realInterviews: 0, sources: 1 },
    indexPath: "/content/llm-interview-v2/index.json",
    sections: [{ id: "posttrain", title: "Post-Training", description: "", questionCount: 1 }],
  },
  {
    schemaVersion: 1 as const,
    id: "leetcode-150",
    slug: "leetcode-150",
    title: "LeetCode",
    shortTitle: "150",
    edition: "1",
    audience: "",
    description: "",
    updatedAt: "2026-08-01",
    stats: { questions: 1, mustKnow: 1, realInterviews: 0, sources: 1 },
    indexPath: "/content/leetcode-150/index.json",
    sections: [{ id: "array-string", title: "Array", description: "", questionCount: 1 }],
  },
];

test("handbook search round-trips book, section, and question", () => {
  const parsed = parseHandbookSearch("?book=leetcode-150&section=array-string&question=lc-1");
  assert.deepEqual(parsed, {
    book: "leetcode-150",
    section: "array-string",
    question: "lc-1",
    view: null,
  });
  assert.equal(
    serializeHandbookSearch(parsed, catalog),
    "?book=leetcode-150&section=array-string&question=lc-1",
  );
});

test("handbook search resolves both id and slug, and fills book when omitted", () => {
  assert.equal(resolveCatalogEntry(catalog, "llm-interview")?.id, "llm-interview-v2");
  assert.equal(resolveCatalogEntry(catalog, "llm-interview-v2")?.slug, "llm-interview");
  assert.equal(
    serializeHandbookSearch({ book: null, section: "posttrain", question: null, view: null }, catalog),
    "?book=llm-interview&section=posttrain",
  );
  assert.equal(
    serializeHandbookSearch({ book: null, section: null, question: null, view: "guide" }, catalog),
    "?book=llm-interview&view=guide",
  );
});
