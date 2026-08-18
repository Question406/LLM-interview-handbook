import assert from "node:assert/strict";
import { existsSync, readdirSync } from "node:fs";
import { readFile } from "node:fs/promises";
import test from "node:test";
import handbook from "../content/generated/handbooks/llm-interview-v2.json" with { type: "json" };
import { renderMarkdown } from "../scripts/build-content.mjs";

function markdownFiles(directory) {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const file = new URL(`${entry.name}${entry.isDirectory() ? "/" : ""}`, directory);
    return entry.isDirectory() ? markdownFiles(file) : (entry.name.endsWith(".md") ? [file] : []);
  });
}

test("the imported handbook has stable, complete metadata", () => {
  const questions = handbook.sections.flatMap((section) => section.questions);
  assert.equal(handbook.sections.length, 10);
  assert.equal(questions.length, 191);
  assert.equal(new Set(questions.map((question) => question.id)).size, 191);
  assert.equal(questions.filter((question) => question.level === "S").length, 116);
  assert.equal(questions.filter((question) => question.isRealInterview).length, 49);
});

test("published questions are standalone Markdown sources", () => {
  const questionDirectory = new URL("../content/handbooks/llm-interview/questions/", import.meta.url);
  assert.equal(markdownFiles(questionDirectory).length, 191);
  assert.equal(existsSync(new URL("../content/handbooks/llm-interview-v2.json", import.meta.url)), false);
});

test("new Markdown answers support math but reject raw HTML", () => {
  const html = renderMarkdown("行内公式 $x^2$。\n\n$$\\mathcal{L}=0$$");
  assert.match(html, /class="katex"/);
  assert.match(html, /math display/);
  assert.throws(() => renderMarkdown("<script>alert(1)</script>"), /cannot contain raw HTML/);
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
