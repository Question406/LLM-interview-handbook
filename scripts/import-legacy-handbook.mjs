import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";

const inputPath = process.argv[2];
const outputPath = process.argv[3] ?? "content/handbooks/llm-interview-v2.json";
const handbookId = "llm-interview-v2";

if (!inputPath) {
  console.error("Usage: node scripts/import-legacy-handbook.mjs <source.html> [output.json]");
  process.exit(1);
}

const html = readFileSync(resolve(inputPath), "utf8");
const allSections = html.match(/<div id="allSections">([\s\S]*?)<div id="empty"/i)?.[1];

if (!allSections) {
  throw new Error("Could not find #allSections in the legacy handbook.");
}

const decode = (value = "") => value
  .replaceAll("&amp;", "&")
  .replaceAll("&lt;", "<")
  .replaceAll("&gt;", ">")
  .replaceAll("&quot;", '"')
  .replaceAll("&#39;", "'")
  .replaceAll("&nbsp;", " ");

const textOnly = (value = "") => decode(value.replace(/<[^>]+>/g, " "))
  .replace(/\s+/g, " ")
  .trim();

const sectionMatches = [...allSections.matchAll(/<section class="section" id="([^"]+)"[^>]*>/g)];
const sections = sectionMatches.map((match, sectionIndex) => {
  const start = match.index;
  const end = sectionMatches[sectionIndex + 1]?.index ?? allSections.length;
  const block = allSections.slice(start, end);
  const header = block.match(/<div class="section-head">[\s\S]*?<h2>([\s\S]*?)<\/h2><p>([\s\S]*?)<\/p>/i);
  const questions = [];
  const articlePattern = /<article class="q-card" id="([^"]+)" data-level="([^"]+)" data-section="([^"]+)" data-search="([^"]*)">([\s\S]*?)<\/article>/gi;

  for (const article of block.matchAll(articlePattern)) {
    const [, id, level, sectionId, searchText, body] = article;
    const badges = body.match(/<div class="q-badges">([\s\S]*?)<\/div>/i)?.[1] ?? "";
    const tags = [...badges.matchAll(/<span class="tag">([\s\S]*?)<\/span>/gi)].map((tag) => textOnly(tag[1]));
    const title = textOnly(body.match(/<summary><h3>([\s\S]*?)<\/h3>/i)?.[1]);
    const quick = textOnly(body.match(/<div class="quick">[\s\S]*?<p>([\s\S]*?)<\/p><\/div>/i)?.[1]);
    const answerHtml = body.match(/<div class="answer-wrap">([\s\S]*)<\/div>\s*<\/details>\s*$/i)?.[1]?.trim();

    if (!title || !answerHtml) {
      throw new Error(`Could not parse question ${id}`);
    }

    questions.push({
      id,
      level,
      sectionId,
      title,
      quick,
      tags,
      isRealInterview: /class="badge true"/i.test(badges),
      searchText: textOnly(searchText),
      answerHtml,
    });
  }

  if (!header || questions.length === 0) {
    throw new Error(`Could not parse section ${match[1]}`);
  }

  return {
    id: match[1],
    title: textOnly(header[1]),
    description: textOnly(header[2]),
    questions,
  };
});

const allQuestions = sections.flatMap((section) => section.questions);
const uniqueSources = new Set(
  allQuestions.flatMap((question) => [...question.answerHtml.matchAll(/href="([^"]+)"/gi)].map((source) => decode(source[1]))),
);

for (const section of sections) {
  const chunkPath = resolve(`public/content/${handbookId}/${section.id}.json`);
  mkdirSync(dirname(chunkPath), { recursive: true });
  writeFileSync(chunkPath, `${JSON.stringify(Object.fromEntries(section.questions.map((question) => [question.id, question.answerHtml])))}\n`);
}

const contentSections = sections.map((section) => ({
  ...section,
  questions: section.questions.map(({ answerHtml: _answerHtml, ...question }) => ({
    ...question,
    answerPath: `/content/${handbookId}/${section.id}.json`,
  })),
}));

const handbook = {
  schemaVersion: 1,
  id: handbookId,
  slug: "llm-interview",
  title: "LLM / Post-Training / Agent",
  shortTitle: "LLM 面试手册",
  edition: "V2",
  audience: "中国大陆头部科技公司 · 2027 校招",
  description: "重点覆盖 Post-Training 算法与数据、Reasoning RL、Agent / Skill / Harness、Agent RL，同时系统补齐架构、系统、数学、RAG 与手撕代码。",
  updatedAt: "2026-08-17",
  stats: {
    questions: allQuestions.length,
    mustKnow: allQuestions.filter((question) => question.level === "S").length,
    realInterviews: allQuestions.filter((question) => question.isRealInterview).length,
    sources: uniqueSources.size,
  },
  sections: contentSections,
};

mkdirSync(dirname(resolve(outputPath)), { recursive: true });
writeFileSync(resolve(outputPath), `${JSON.stringify(handbook)}\n`);
console.log(`Imported ${allQuestions.length} questions across ${sections.length} sections into ${outputPath}`);
