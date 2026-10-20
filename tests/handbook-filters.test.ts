import assert from "node:assert/strict";
import test from "node:test";
import { handbookHasCompanies, questionMatchesCompany } from "../lib/company-facets.mjs";
import { arrangeStudySections, isGuideQuestion } from "../lib/study-layout.ts";
import type { Handbook, HandbookQuestion } from "../content/types.ts";

const question = (companies: string[]): HandbookQuestion => ({
  id: "q",
  level: "A",
  sectionId: "posttrain",
  title: "t",
  quick: "q",
  tags: ["GRPO"],
  companies,
  isRealInterview: false,
  searchText: "t q GRPO",
  answerPath: "/x.json",
});

test("a question matches a company facet when it carries that slug", () => {
  assert.equal(questionMatchesCompany(question(["alibaba", "bytedance"]), "alibaba"), true);
  assert.equal(questionMatchesCompany(question(["alibaba"]), "openai"), false);
  assert.equal(questionMatchesCompany(question([]), "alibaba"), false);
  assert.equal(questionMatchesCompany(question(["alibaba"]), null), true);
});

test("handbooks without company-tagged questions hide the company axis", () => {
  const handbook = {
    schemaVersion: 1 as const,
    id: "leetcode-150",
    slug: "leetcode-150",
    title: "LeetCode",
    shortTitle: "150",
    edition: "1",
    audience: "",
    description: "",
    updatedAt: "2026-08-01",
    stats: { questions: 1, mustKnow: 0, realInterviews: 0, sources: 0 },
    companies: [],
    sections: [{
      id: "array-string",
      title: "Array",
      description: "",
      cardsPath: "/c.json",
      answerPath: "/a.json",
      questions: [question([])],
    }],
  } satisfies Handbook;
  assert.equal(handbookHasCompanies(handbook), false);
  handbook.companies = [{ id: "openai", title: "OpenAI", questionCount: 1 }];
  handbook.sections[0].questions[0].companies = ["openai"];
  assert.equal(handbookHasCompanies(handbook), true);
});

test("guide questions are maps, indexes, and 真题导航 cards", () => {
  assert.equal(isGuideQuestion(question([])), false);
  assert.equal(isGuideQuestion({ ...question([]), tags: ["真题导航"] }), true);
  assert.equal(isGuideQuestion({ ...question([]), tags: ["备考地图"] }), true);
  assert.equal(isGuideQuestion({ ...question([]), id: "fund-kl-posttrain-index" }), true);
  assert.equal(isGuideQuestion({ ...question([]), id: "ali-prep-map" }), true);
  assert.equal(isGuideQuestion({ ...question([]), id: "ali-algo-prep-list" }), true);
});

test("study layout pins guides above the rest, and puts S first when there is no guide", () => {
  const guide = { ...question(["alibaba"]), id: "company-alibaba", tags: ["真题导航"] };
  const s = { ...question(["alibaba"]), id: "s-q", level: "S" };
  const a = { ...question(["alibaba"]), id: "a-q", level: "A" };
  const withGuide = arrangeStudySections([{ questions: [a, guide, s] }]);
  assert.deepEqual(withGuide.pinned.map((item) => item.id), ["company-alibaba"]);
  assert.deepEqual(withGuide.sections[0].questions.map((item) => item.id), ["a-q", "s-q"]);

  const noGuide = arrangeStudySections([{ questions: [a, s] }]);
  assert.deepEqual(noGuide.pinned, []);
  assert.deepEqual(noGuide.sections[0].questions.map((item) => item.id), ["s-q", "a-q"]);
});
