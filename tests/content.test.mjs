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

test("the generated handbook has stable, complete metadata", () => {
  const questions = handbook.sections.flatMap((section) => section.questions);
  assert.equal(handbook.sections.length, 14);
  assert.equal(questions.length, 231);
  assert.equal(new Set(questions.map((question) => question.id)).size, 231);
  assert.equal(questions.filter((question) => question.level === "S").length, 144);
  assert.equal(questions.filter((question) => question.isRealInterview).length, 49);
});

test("published questions are standalone Markdown sources", () => {
  const questionDirectory = new URL("../content/handbooks/llm-interview/questions/", import.meta.url);
  assert.equal(markdownFiles(questionDirectory).length, 231);
  assert.equal(existsSync(new URL("../content/handbooks/llm-interview-v2.json", import.meta.url)), false);
});

test("new Markdown answers support math but reject raw HTML", () => {
  const html = renderMarkdown("行内公式 $x^2$ 和 \\(y^2\\)。\n\n$$\\mathcal{L}=0$$\n\n\\[z=1\\]");
  assert.match(html, /class="katex"/);
  assert.equal((html.match(/math inline/g) ?? []).length, 2);
  assert.equal((html.match(/math display/g) ?? []).length, 2);
  assert.throws(() => renderMarkdown("<script>alert(1)</script>"), /cannot contain raw HTML/);
  assert.throws(() => renderMarkdown("$\\notARealKatexCommand{x}$"), /Undefined control sequence/);
});

test("Markdown code keeps math delimiters literal", () => {
  const html = renderMarkdown("Use `$x$` and `\\(y\\)` literally.\n\n```sh\necho '$HOME' # \\[not math\\]\n```");
  assert.doesNotMatch(html, /class="katex"/);
  assert.match(html, /<code>\$x\$<\/code>/);
  assert.match(html, /<code>\\\(y\\\)<\/code>/);
  assert.match(html, /\$HOME/);
});

test("all migrated formulas retain complete MathJax SVG wrappers", async () => {
  const questionDirectory = new URL("../content/handbooks/llm-interview/questions/", import.meta.url);
  let formulaQuestions = 0;
  for (const file of markdownFiles(questionDirectory)) {
    const source = await readFile(file, "utf8");
    if (!source.includes('class="math')) continue;
    formulaQuestions += 1;
    const mathSpans = (source.match(/<span class="math (?:display|inline)">/g) ?? []).length;
    const mathJaxContainers = (source.match(/<mjx-container/g) ?? []).length;
    assert.equal(mathSpans, mathJaxContainers, `${file.pathname} has an incomplete formula wrapper`);
    assert.equal((source.match(/<svg/g) ?? []).length >= mathJaxContainers, true, `${file.pathname} has a formula without SVG`);
  }
  assert.equal(formulaQuestions, 63);
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
