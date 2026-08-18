import { existsSync, mkdirSync, readFileSync, readdirSync, unlinkSync, writeFileSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import matter from "gray-matter";
import katex from "katex";
import { marked } from "marked";

const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const handbooksRoot = resolve(projectRoot, "content/handbooks");
const generatedRoot = resolve(projectRoot, "content/generated/handbooks");
const generatedRegistry = resolve(projectRoot, "content/generated/registry.json");
const publicRoot = resolve(projectRoot, "public/content");
const isCheckOnly = process.argv.includes("--check");

function fail(filePath, message) {
  throw new Error(`Content validation failed in ${relative(projectRoot, filePath)}: ${message}`);
}

function readMarkdown(filePath) {
  const parsed = matter(readFileSync(filePath, "utf8"));
  return { data: parsed.data ?? {}, body: parsed.content.trim() };
}

function walkMarkdown(directory) {
  if (!existsSync(directory)) return [];
  return readdirSync(directory, { withFileTypes: true })
    .flatMap((entry) => {
      const filePath = join(directory, entry.name);
      if (entry.isDirectory()) return walkMarkdown(filePath);
      return entry.isFile() && entry.name.endsWith(".md") ? [filePath] : [];
    })
    .sort();
}

function asString(value, filePath, field) {
  if (typeof value !== "string" || !value.trim()) fail(filePath, `${field} must be a non-empty string`);
  return value.trim();
}

function asDate(value, filePath, field) {
  const date = value instanceof Date ? value.toISOString().slice(0, 10) : asString(value, filePath, field);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) fail(filePath, `${field} must use YYYY-MM-DD`);
  return date;
}

function safeUrl(value) {
  try {
    const url = new URL(value);
    return url.protocol === "https:" || url.protocol === "http:";
  } catch {
    return false;
  }
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[character]);
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function renderMath(tex, displayMode) {
  return `<span class="math${displayMode ? " display" : " inline"}">${katex.renderToString(tex.trim(), { displayMode, throwOnError: true, output: "htmlAndMathml" })}</span>`;
}

function shieldCodeDelimiters(markdown) {
  const delimiters = [];
  const shield = (code) => code.replace(/[\\$]/g, (character) => {
    const token = `CONTENT_CODE_DELIMITER_${delimiters.length}_TOKEN`;
    delimiters.push({ token, character });
    return token;
  });
  const fenced = markdown.replace(/(^|\n)( {0,3})(`{3,}|~{3,})[^\n]*\n[\s\S]*?\n\2\3(?=\n|$)/g, shield);
  const source = fenced.replace(/(`+)([^`\n]*?)\1/g, shield);
  return {
    source,
    restore(html) {
      for (const { token, character } of delimiters) html = html.replaceAll(token, character);
      return html;
    },
  };
}

export function renderMarkdown(markdown) {
  if (/<\/?[a-z][^>]*>/i.test(markdown)) {
    throw new Error("Markdown questions cannot contain raw HTML. Use normal Markdown or a legacy-html migration file.");
  }

  const replacements = [];
  const code = shieldCodeDelimiters(markdown);
  let source = code.source.replace(/\$\$([\s\S]+?)\$\$|\\\[([\s\S]+?)\\\]/g, (_match, dollarTex, bracketTex) => {
    const token = `CONTENT_MATH_BLOCK_${replacements.length}_TOKEN`;
    replacements.push({ token, html: renderMath(dollarTex ?? bracketTex, true), block: true });
    return `\n\n${token}\n\n`;
  });
  source = source.replace(/(^|[^\\$])\$([^$\n]+?)\$|\\\((.+?)\\\)/g, (_match, prefix = "", dollarTex, parenTex) => {
    const token = `CONTENT_MATH_INLINE_${replacements.length}_TOKEN`;
    replacements.push({ token, html: renderMath(dollarTex ?? parenTex, false), block: false });
    return `${prefix}${token}`;
  });

  let html = marked.parse(source, { gfm: true, breaks: false });
  for (const replacement of replacements) {
    const token = escapeRegExp(replacement.token);
    if (replacement.block) html = html.replace(new RegExp(`<p>${token}</p>`, "g"), replacement.html);
    html = html.replace(new RegExp(token, "g"), replacement.html);
  }

  return code.restore(html
    .replace(/<script[\s\S]*?<\/script>/gi, "")
    .replace(/\s(?:on[a-z]+|style)=("[^"]*"|'[^']*'|[^\s>]+)/gi, "")
    .replace(/href="([^"]*)"/gi, (_match, href) => (safeUrl(href) ? `href="${href}"` : 'href="#"')));
}

function sourceHtml(sources) {
  if (!sources.length) return "";
  return `<div class="sources"><div class="mini-title">延伸阅读</div>${sources.map((source) => `<a href="${escapeHtml(source.url)}" target="_blank" rel="noreferrer">${escapeHtml(source.title)}</a>`).join("")}</div>`;
}

function renderAnswer(question) {
  if (question.format === "legacy-html") return question.body;
  const answerBody = renderMarkdown(question.body);
  return `<div class="full-answer"><div class="mini-title">完整答案</div>${answerBody}${sourceHtml(question.sources)}</div>`;
}

function textOnly(value) {
  return value
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, " ")
    .trim();
}

function parseQuestion(filePath, sectionIds) {
  const { data, body } = readMarkdown(filePath);
  const id = asString(data.id, filePath, "id");
  if (!/^[a-z0-9][a-z0-9-]*$/.test(id)) fail(filePath, "id must use lowercase letters, numbers, and hyphens");
  const sectionId = asString(data.section, filePath, "section");
  if (!sectionIds.has(sectionId)) fail(filePath, `section ${sectionId} is not declared in _handbook.md`);
  const level = asString(data.level, filePath, "level");
  const title = asString(data.title, filePath, "title");
  const quick = asString(data.quick, filePath, "quick");
  if (!Array.isArray(data.tags) || !data.tags.length || data.tags.some((tag) => typeof tag !== "string" || !tag.trim())) {
    fail(filePath, "tags must be a non-empty list of strings");
  }
  if (typeof data.realInterview !== "boolean") fail(filePath, "realInterview must be true or false");
  if (data.status !== "published" && data.status !== "draft" && data.status !== "review") fail(filePath, "status must be draft, review, or published");
  if (data.format !== "markdown" && data.format !== "legacy-html") fail(filePath, "format must be markdown or legacy-html");
  if (data.format === "legacy-html" && data.provenance !== "legacy-handbook-v2") {
    fail(filePath, "legacy-html is reserved for migrated legacy content");
  }
  if (!body) fail(filePath, "answer body is empty");

  const sources = Array.isArray(data.sources) ? data.sources.map((source, index) => {
    if (!source || typeof source !== "object") fail(filePath, `sources[${index}] must be an object`);
    const titleValue = asString(source.title, filePath, `sources[${index}].title`);
    const url = asString(source.url, filePath, `sources[${index}].url`);
    if (!safeUrl(url)) fail(filePath, `sources[${index}].url must be an http(s) URL`);
    return { title: titleValue, url, type: typeof source.type === "string" ? source.type : "reference" };
  }) : [];
  if (data.format === "markdown" && !sources.length) fail(filePath, "new Markdown questions need at least one source");

  return {
    filePath,
    id,
    sectionId,
    level,
    title,
    quick,
    tags: data.tags.map((tag) => tag.trim()),
    isRealInterview: data.realInterview,
    status: data.status,
    format: data.format,
    order: Number.isInteger(data.order) && data.order >= 0 ? data.order : 9999,
    updatedAt: asDate(data.updatedAt, filePath, "updatedAt"),
    sources,
    body,
  };
}

function loadHandbook(handbookFile) {
  if (!existsSync(handbookFile)) throw new Error(`Missing handbook configuration: ${relative(projectRoot, handbookFile)}`);
  const { data } = readMarkdown(handbookFile);
  if (data.schemaVersion !== 1) fail(handbookFile, "schemaVersion must be 1");
  for (const field of ["id", "slug", "title", "shortTitle", "edition", "audience", "description"]) asString(data[field], handbookFile, field);
  if (!Array.isArray(data.sections) || !data.sections.length) fail(handbookFile, "sections must be a non-empty list");
  const sectionIds = new Set();
  const sections = data.sections.map((section, index) => {
    if (!section || typeof section !== "object") fail(handbookFile, `sections[${index}] must be an object`);
    const id = asString(section.id, handbookFile, `sections[${index}].id`);
    if (sectionIds.has(id)) fail(handbookFile, `duplicate section id ${id}`);
    sectionIds.add(id);
    return {
      id,
      title: asString(section.title, handbookFile, `sections[${index}].title`),
      description: asString(section.description, handbookFile, `sections[${index}].description`),
    };
  });
  return { ...data, sections, sectionIds, root: dirname(handbookFile), filePath: handbookFile };
}

function findHandbookFiles() {
  if (!existsSync(handbooksRoot)) return [];
  return readdirSync(handbooksRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && existsSync(join(handbooksRoot, entry.name, "_handbook.md")))
    .map((entry) => join(handbooksRoot, entry.name, "_handbook.md"))
    .sort();
}

function writeIfChanged(filePath, content) {
  mkdirSync(dirname(filePath), { recursive: true });
  if (!existsSync(filePath) || readFileSync(filePath, "utf8") !== content) writeFileSync(filePath, content);
}

function removeStaleChunks(directory, expected) {
  if (!existsSync(directory)) return;
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    if (entry.isFile() && entry.name.endsWith(".json") && !expected.has(entry.name)) unlinkSync(join(directory, entry.name));
  }
}

function buildHandbook(handbookFile, { write = true } = {}) {
  const handbook = loadHandbook(handbookFile);
  const sectionIds = handbook.sectionIds;
  const files = walkMarkdown(join(handbook.root, "questions"));
  if (!files.length) throw new Error("No published question files found");
  const questions = files.map((filePath) => parseQuestion(filePath, sectionIds));
  const ids = new Set();
  for (const question of questions) {
    if (question.status !== "published") fail(question.filePath, "questions/ may only contain published questions; keep drafts under drafts/");
    if (ids.has(question.id)) fail(question.filePath, `duplicate question id ${question.id}`);
    ids.add(question.id);
  }

  const answerDirectory = join(publicRoot, handbook.id);
  const answerChunks = {};
  const sections = handbook.sections.map((section) => {
    const sectionQuestions = questions
      .filter((question) => question.sectionId === section.id)
      .sort((left, right) => left.order - right.order || left.title.localeCompare(right.title, "zh-Hans-CN"));
    if (!sectionQuestions.length) fail(handbook.filePath, `section ${section.id} has no published questions`);
    const answerPath = `/content/${handbook.id}/${section.id}.json`;
    answerChunks[section.id] = Object.fromEntries(sectionQuestions.map((question) => [question.id, renderAnswer(question)]));
    return {
      ...section,
      questions: sectionQuestions.map((question) => ({
        id: question.id,
        level: question.level,
        sectionId: question.sectionId,
        title: question.title,
        quick: question.quick,
        tags: question.tags,
        isRealInterview: question.isRealInterview,
        searchText: `${question.title} ${question.quick} ${question.tags.join(" ")} ${textOnly(answerChunks[section.id][question.id])}`.replace(/\s+/g, " ").trim(),
        answerPath,
      })),
    };
  });

  const allQuestions = sections.flatMap((section) => section.questions);
  const sourceUrls = new Set(questions.flatMap((question) => question.sources.map((source) => source.url)));
  const generated = {
    schemaVersion: handbook.schemaVersion,
    id: handbook.id,
    slug: handbook.slug,
    title: handbook.title,
    shortTitle: handbook.shortTitle,
    edition: handbook.edition,
    audience: handbook.audience,
    description: handbook.description,
    updatedAt: questions.map((question) => question.updatedAt).sort().at(-1),
    stats: {
      questions: allQuestions.length,
      mustKnow: allQuestions.filter((question) => question.level === "S").length,
      realInterviews: allQuestions.filter((question) => question.isRealInterview).length,
      sources: sourceUrls.size,
    },
    sections,
  };

  if (write) {
    writeIfChanged(join(generatedRoot, `${handbook.id}.json`), `${JSON.stringify(generated)}\n`);
    const expected = new Set();
    for (const [sectionId, chunk] of Object.entries(answerChunks)) {
      const filename = `${sectionId}.json`;
      expected.add(filename);
      writeIfChanged(join(answerDirectory, filename), `${JSON.stringify(chunk)}\n`);
    }
    removeStaleChunks(answerDirectory, expected);
  }

  return { handbook: generated, questionFiles: files, questions };
}

function removeStaleIndexes(expected) {
  if (!existsSync(generatedRoot)) return;
  for (const entry of readdirSync(generatedRoot, { withFileTypes: true })) {
    if (entry.isFile() && entry.name.endsWith(".json") && !expected.has(entry.name)) unlinkSync(join(generatedRoot, entry.name));
  }
}

export function buildContent({ write = true } = {}) {
  const handbookFiles = findHandbookFiles();
  if (!handbookFiles.length) throw new Error("No handbook directories found under content/handbooks");
  const results = handbookFiles.map((filePath) => buildHandbook(filePath, { write }));
  const ids = new Set();
  for (const result of results) {
    if (ids.has(result.handbook.id)) throw new Error(`Duplicate handbook id: ${result.handbook.id}`);
    ids.add(result.handbook.id);
  }
  if (write) {
    removeStaleIndexes(new Set(results.map((result) => `${result.handbook.id}.json`)));
    writeIfChanged(generatedRegistry, `${JSON.stringify(results.map((result) => result.handbook))}\n`);
  }
  return {
    handbooks: results.map((result) => result.handbook),
    questionFiles: results.flatMap((result) => result.questionFiles),
    questions: results.flatMap((result) => result.questions),
  };
}

if (process.argv[1] && resolve(fileURLToPath(import.meta.url)) === resolve(process.argv[1])) {
  const result = buildContent({ write: !isCheckOnly });
  console.log(`${isCheckOnly ? "Validated" : "Built"} ${result.questions.length} questions across ${result.handbooks.length} handbook(s).`);
}
