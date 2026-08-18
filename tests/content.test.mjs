import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import handbook from "../content/handbooks/llm-interview-v2.json" with { type: "json" };

test("the imported handbook has stable, complete metadata", () => {
  const questions = handbook.sections.flatMap((section) => section.questions);
  assert.equal(handbook.sections.length, 10);
  assert.equal(questions.length, 191);
  assert.equal(new Set(questions.map((question) => question.id)).size, 191);
  assert.equal(questions.filter((question) => question.level === "S").length, 116);
  assert.equal(questions.filter((question) => question.isRealInterview).length, 49);
});

test("large answers are split into lazy-loaded module chunks", async () => {
  for (const section of handbook.sections) {
    const answerPath = section.questions[0].answerPath;
    assert.ok(answerPath?.startsWith("/content/llm-interview-v2/"));
    const chunkUrl = new URL(`../public${answerPath}`, import.meta.url);
    const chunk = JSON.parse(await readFile(chunkUrl, "utf8"));
    assert.deepEqual(Object.keys(chunk).sort(), section.questions.map((question) => question.id).sort());
    assert.ok(section.questions.every((question) => !Object.hasOwn(question, "answerHtml")));
  }
});
