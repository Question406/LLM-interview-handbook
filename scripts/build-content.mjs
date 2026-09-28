import { existsSync, mkdirSync, readFileSync, readdirSync, rmSync, unlinkSync, writeFileSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import matter from "gray-matter";
import hljs from "highlight.js";
import katex from "katex";
import { marked } from "marked";

const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const handbooksRoot = resolve(projectRoot, "content/handbooks");
const generatedRoot = resolve(projectRoot, "content/generated/handbooks");
const generatedRegistry = resolve(projectRoot, "content/generated/registry.json");
const generatedCatalog = resolve(projectRoot, "content/generated/catalog.json");
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

function isInternalQuestionHref(href) {
  return /^\?(?:book=[a-z0-9-]+&)?section=[a-z0-9-]+&question=[a-z0-9-]+$/.test(href.replace(/&amp;/g, "&"));
}

function isAllowedHref(href) {
  return safeUrl(href) || isInternalQuestionHref(href);
}

function questionHref(question, book) {
  return book
    ? `?book=${book}&section=${question.sectionId}&question=${question.id}`
    : `?section=${question.sectionId}&question=${question.id}`;
}

function escapeMarkdownLinkLabel(label) {
  const math = /\$\$[\s\S]+?\$\$|\$[^$\n]+\$/g;
  let output = "";
  let cursor = 0;
  for (const match of label.matchAll(math)) {
    output += label.slice(cursor, match.index).replace(/]/g, "\\]");
    output += match[0];
    cursor = match.index + match[0].length;
  }
  return output + label.slice(cursor).replace(/]/g, "\\]");
}

function questionMarkdownLink(question, label, book) {
  return `[${escapeMarkdownLinkLabel(label)}](${questionHref(question, book)})`;
}

function catalogQuestions(catalog) {
  return Array.isArray(catalog) ? catalog : catalog.questions;
}

function uniqueTitlesByLength(questions) {
  const counts = new Map();
  for (const question of questions) counts.set(question.title, (counts.get(question.title) ?? 0) + 1);
  return questions
    .filter((question) => counts.get(question.title) === 1)
    .slice()
    .sort((left, right) => right.title.length - left.title.length || left.id.localeCompare(right.id));
}

export function normalizeQuestionTitle(text) {
  return text
    .replace(/（[^）]*）/g, " ")
    .replace(/\([^)]*\)/g, " ")
    .replace(/[？?！!，,、；;]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

export function compactQuestionTitle(text) {
  return normalizeQuestionTitle(text).replace(/[:：]/g, "").replace(/\s+/g, "").toLowerCase();
}

function topicKey(text) {
  const cut = text.search(/[:：]/);
  const topic = cut === -1 ? text : text.slice(cut + 1);
  return compactQuestionTitle(topic) || compactQuestionTitle(text);
}

function sharedPrefixLength(left, right) {
  const limit = Math.min(left.length, right.length);
  let index = 0;
  while (index < limit && left[index] === right[index]) index += 1;
  return index;
}

function uniqueHit(hits) {
  return hits.length === 1 ? hits[0] : null;
}

export function findQuestionForText(text, catalog, currentId) {
  const trimmed = text.replace(/^\*\*[^*]+\*\*\s*[:：]?\s*/, "").trim();
  if (!trimmed) return null;
  const others = catalogQuestions(catalog).filter((question) => question.id !== currentId);

  const exact = others.filter((question) => question.title === trimmed);
  if (exact.length === 1) return exact[0];
  if (exact.length > 1) return null;

  const key = normalizeQuestionTitle(trimmed);
  if (key.length < 8) return null;

  const exactKey = others.filter((question) => normalizeQuestionTitle(question.title) === key);
  const exactKeyHit = uniqueHit(exactKey);
  if (exactKeyHit) return exactKeyHit;
  if (exactKey.length > 1) return null;

  const itemCompact = compactQuestionTitle(trimmed);
  const itemTopic = topicKey(trimmed);

  const compactExact = others.filter((question) => compactQuestionTitle(question.title) === itemCompact);
  const compactHit = uniqueHit(compactExact);
  if (compactHit) return compactHit;

  if (itemTopic.length >= 6) {
    const topicExact = others.filter((question) => topicKey(question.title) === itemTopic);
    const topicHit = uniqueHit(topicExact);
    if (topicHit) return topicHit;
  }

  const allowFuzzy = trimmed.length <= 80;
  if (!allowFuzzy) return null;

  const prefixHits = [];
  for (const question of others) {
    const titleKey = normalizeQuestionTitle(question.title);
    const titleCompact = compactQuestionTitle(question.title);
    const titleTopic = topicKey(question.title);
    const leftoverShort = (longer, shorter) => longer.slice(shorter.length).length <= 80;
    if (titleKey.length >= 10 && key.startsWith(titleKey) && leftoverShort(key, titleKey)) prefixHits.push(question);
    else if (itemCompact.length >= 10 && titleCompact.startsWith(itemCompact)) prefixHits.push(question);
    else if (titleCompact.length >= 10 && itemCompact.startsWith(titleCompact)) prefixHits.push(question);
    else if (itemTopic.length >= 10 && titleTopic.startsWith(itemTopic)) prefixHits.push(question);
    else if (titleTopic.length >= 10 && itemTopic.startsWith(titleTopic)) prefixHits.push(question);
  }
  const uniquePrefix = [...new Set(prefixHits)];
  if (uniquePrefix.length === 1) return uniquePrefix[0];
  if (uniquePrefix.length > 1) {
    uniquePrefix.sort((left, right) => compactQuestionTitle(right.title).length - compactQuestionTitle(left.title).length);
    if (compactQuestionTitle(uniquePrefix[0].title).length > compactQuestionTitle(uniquePrefix[1].title).length) {
      return uniquePrefix[0];
    }
  }

  if (itemTopic.length >= 12) {
    const contained = others.filter((question) => topicKey(question.title).includes(itemTopic) || compactQuestionTitle(question.title).includes(itemTopic));
    const containedHit = uniqueHit(contained);
    if (containedHit) return containedHit;
  }

  if (itemTopic.length >= 12) {
    const scored = others
      .map((question) => ({ question, n: sharedPrefixLength(itemTopic, topicKey(question.title)) }))
      .filter((entry) => entry.n >= 12);
    scored.sort((left, right) => right.n - left.n);
    if (scored.length === 1) return scored[0].question;
    if (scored.length > 1 && scored[0].n >= scored[1].n + 3) return scored[0].question;
  }

  return null;
}

function shieldRegions(markdown, patterns, prefix) {
  const regions = [];
  let source = markdown;
  for (const pattern of patterns) {
    source = source.replace(pattern, (block) => {
      const token = `${prefix}${regions.length}TOKEN`;
      regions.push({ token, block });
      return token;
    });
  }
  return {
    source,
    restore(text) {
      for (let index = regions.length - 1; index >= 0; index -= 1) {
        text = text.replaceAll(regions[index].token, regions[index].block);
      }
      return text;
    },
  };
}

function alreadyLinked(text) {
  return /CONTENTQREF\d+TOKEN/.test(text) || /\]\([^)]*\)/.test(text);
}

export function linkQuestionRefs(markdown, catalog, currentId, book) {
  const questions = catalogQuestions(catalog);
  const byId = new Map(questions.map((question) => [question.id, question]));
  const refs = [];
  const tokenFor = (question, text) => {
    const token = `CONTENTQREF${refs.length}TOKEN`;
    refs.push({ token, question, text });
    return token;
  };

  const fenced = shieldRegions(markdown, [/(^|\n)( {0,3})(`{3,}|~{3,})[^\n]*\n[\s\S]*?\n\2\3(?=\n|$)/g], "CONTENTFENCE");
  let source = fenced.source.replace(/`([a-z0-9][a-z0-9-]*)`/g, (match, id) => {
    const question = byId.get(id);
    if (!question || question.id === currentId) return match;
    return tokenFor(question, `\`${id}\``);
  });

  const inlineCode = shieldRegions(source, [/`([^`\n]+)`/g], "CONTENTCODE");
  source = inlineCode.source.replace(/\[\[([a-z0-9]+-[a-z0-9-]*)(?:\|([^\]]+))?\]\]/g, (_match, id, label) => {
    const question = byId.get(id);
    if (!question) throw new Error(`Unknown question id in [[${id}]]`);
    if (question.id === currentId) return label ?? question.title;
    return tokenFor(question, label ?? question.title);
  });

  source = source.replace(/\[([^\]]+)\]\(question:([a-z0-9]+-[a-z0-9-]*)\)/g, (_match, label, id) => {
    const question = byId.get(id);
    if (!question) throw new Error(`Unknown question id in (question:${id})`);
    if (question.id === currentId) return label;
    return tokenFor(question, label);
  });

  const markdownLinks = shieldRegions(source, [/\[([^\]\n]+)\]\(([^)\s]+)\)/g], "CONTENTLINK");
  source = markdownLinks.source;
  for (const question of uniqueTitlesByLength(questions)) {
    if (question.id === currentId || question.title.length < 8 || !source.includes(question.title)) continue;
    source = source.split(question.title).join(tokenFor(question, question.title));
  }
  source = inlineCode.restore(markdownLinks.restore(source));

  source = source.replace(/「([^」]{8,})」/g, (match, title) => {
    if (alreadyLinked(title)) return match;
    const question = findQuestionForText(title, questions, currentId);
    if (!question) return match;
    return `「${tokenFor(question, title)}」`;
  });

  const restoreRefText = (text) => {
    let output = text;
    for (const ref of refs) output = output.replaceAll(ref.token, ref.text);
    return output;
  };

  source = source.split("\n").map((line) => {
    const match = line.match(/^(\s*(?:[-*]|\d+\.)\s+)(.+)$/);
    if (!match) return line;
    const body = match[2];
    const inLine = [...body.matchAll(/CONTENTQREF(\d+)TOKEN/g)].map((hit) => refs[Number(hit[1])]);
    const unique = [...new Map(inLine.map((ref) => [ref.question.id, ref])).values()];
    if (unique.length === 1) {
      if (body.trim() === unique[0].token) return line;
      const label = restoreRefText(body);
      if (/^\*\*/.test(body.trim()) || label.length > 180) return line;
      return `${match[1]}${tokenFor(unique[0].question, label)}`;
    }
    if (alreadyLinked(body)) return line;
    const question = findQuestionForText(body, questions, currentId);
    if (!question) return line;
    return `${match[1]}${tokenFor(question, body)}`;
  }).join("\n");

  source = fenced.restore(source);
  for (const ref of refs) source = source.replaceAll(ref.token, questionMarkdownLink(ref.question, ref.text, book));
  return source;
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

function decodeEntities(value) {
  return value.replace(/&(amp|lt|gt|quot|#39);/g, (_match, entity) => ({ amp: "&", lt: "<", gt: ">", quot: '"', "#39": "'" })[entity]);
}

const languageAliases = {
  py: "python",
  python3: "python",
  js: "javascript",
  ts: "typescript",
  "c++": "cpp",
  "c#": "csharp",
  sh: "bash",
  shell: "bash",
  zsh: "bash",
  yml: "yaml",
  text: "plaintext",
  txt: "plaintext",
};

function resolveLanguage(lang) {
  if (!lang) return "";
  const normalized = lang.trim().toLowerCase();
  const aliased = languageAliases[normalized] ?? normalized;
  return hljs.getLanguage(aliased) ? aliased : "";
}

function inferLanguage(source, lang) {
  const resolved = resolveLanguage(lang);
  if (resolved) return resolved;
  return /^\s*(?:from |import |def |class |async def )/m.test(source) ? "python" : "";
}

function highlightFence(source, lang) {
  const language = inferLanguage(source, lang);
  const highlighted = language
    ? hljs.highlight(source, { language, ignoreIllegals: true }).value
    : escapeHtml(source);
  const className = language ? `hljs language-${language}` : "hljs";
  return `<pre><code class="${className}">${highlighted}</code></pre>`;
}

export function highlightCodeBlocks(html) {
  return html.replace(/<pre\b[^>]*><code\b([^>]*)>([\s\S]*?)<\/code><\/pre>/gi, (match, attrs, body) => {
    if (/\bhljs\b/.test(attrs)) return match;
    const lang = attrs.match(/\blanguage-([^\s"']+)/i)?.[1]
      ?? attrs.match(/\bdata-lang=["']?([^\s"'>]+)/i)?.[1]
      ?? "";
    return highlightFence(decodeEntities(body.replace(/\n$/, "")), lang);
  });
}

const mathDelimiters = /\$\$([\s\S]+?)\$\$|(?<![\\$])\$([^$\n]+?)\$/g;
// Legacy answers are trusted HTML, so math must not be substituted inside code, tags, or already-rendered formulas.
const mathExemptRegions = /<pre[\s\S]*?<\/pre>|<code[\s\S]*?<\/code>|<span class="math[\s\S]*?<\/span>|<[^>]+>/g;

function renderMathDelimiters(text, { escapeProse }) {
  let output = "";
  let cursor = 0;
  for (const match of text.matchAll(mathDelimiters)) {
    const prose = text.slice(cursor, match.index);
    output += escapeProse ? escapeHtml(prose) : prose;
    const [displayTex, inlineTex] = [match[1], match[2]];
    output += renderMath(decodeEntities(displayTex ?? inlineTex), displayTex !== undefined);
    cursor = match.index + match[0].length;
  }
  const tail = text.slice(cursor);
  return output + (escapeProse ? escapeHtml(tail) : tail);
}

export function renderMathInHtml(html) {
  let output = "";
  let cursor = 0;
  for (const match of html.matchAll(mathExemptRegions)) {
    output += renderMathDelimiters(html.slice(cursor, match.index), { escapeProse: false });
    output += match[0];
    cursor = match.index + match[0].length;
  }
  return output + renderMathDelimiters(html.slice(cursor), { escapeProse: false });
}

export function renderMathInText(text) {
  return renderMathDelimiters(text, { escapeProse: true });
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
  // Sanitize Markdown HTML before substituting KaTeX. KaTeX layout depends on
  // inline height/width styles; stripping them after insertion collapses every formula.
  html = html
    .replace(/<script[\s\S]*?<\/script>/gi, "")
    .replace(/\s(?:on[a-z]+|style)=("[^"]*"|'[^']*'|[^\s>]+)/gi, "")
    .replace(/href="([^"]*)"/gi, (_match, href) => (isAllowedHref(href) ? `href="${href}"` : "href=\"#\""))
    .replace(
      /<a href="(\?(?:book=[a-z0-9-]+(?:&amp;|&))?section=[a-z0-9-]+(?:&amp;|&)question=([a-z0-9-]+))"/gi,
      '<a class="question-link" href="$1" data-question-id="$2"',
    );
  for (const replacement of replacements) {
    const token = escapeRegExp(replacement.token);
    if (replacement.block) html = html.replace(new RegExp(`<p>${token}</p>`, "g"), () => replacement.html);
    html = html.replace(new RegExp(token, "g"), () => replacement.html);
  }
  return highlightCodeBlocks(code.restore(html));
}

function sourceHtml(sources) {
  if (!sources.length) return "";
  return `<div class="sources"><div class="mini-title">延伸阅读</div>${sources.map((source) => `<a href="${escapeHtml(source.url)}" target="_blank" rel="noreferrer">${renderMathInText(source.title)}</a>`).join("")}</div>`;
}

function decorateQuestionLinks(html, catalog) {
  const byId = new Map(catalogQuestions(catalog).map((question) => [question.id, question]));
  return html.replace(
    /<a class="question-link" href="([^"]*)" data-question-id="([a-z0-9-]+)"/g,
    (match, href, id) => {
      const question = byId.get(id);
      if (!question) return match;
      return `<a class="question-link" href="${href}" data-question-id="${id}" title="${escapeHtml(question.title.replace(/\$/g, ""))}"`;
    },
  );
}

function linkQuestionIdsInHtml(html, catalog, currentId, book) {
  const byId = new Map(catalogQuestions(catalog).map((question) => [question.id, question]));
  const skip = /<pre\b[\s\S]*?<\/pre>|<a\b[\s\S]*?<\/a>/gi;
  let output = "";
  let cursor = 0;
  for (const match of html.matchAll(skip)) {
    output += linkBareQuestionCodes(html.slice(cursor, match.index), byId, currentId, book);
    output += match[0];
    cursor = match.index + match[0].length;
  }
  return output + linkBareQuestionCodes(html.slice(cursor), byId, currentId, book);
}

function linkBareQuestionCodes(html, byId, currentId, book) {
  return html.replace(/<code>([a-z0-9][a-z0-9-]*)<\/code>/g, (match, id) => {
    if (id === currentId) return match;
    const question = byId.get(id);
    if (!question) return match;
    return `<a class="question-link" href="${questionHref(question, book)}" data-question-id="${question.id}">${match}</a>`;
  });
}

function renderAnswer(question, catalog, book) {
  try {
    const answerBody = question.format === "legacy-html"
      ? decorateQuestionLinks(linkQuestionIdsInHtml(highlightCodeBlocks(renderMathInHtml(question.body)), catalog, question.id, book), catalog)
      : decorateQuestionLinks(renderMarkdown(linkQuestionRefs(question.body, catalog, question.id, book)), catalog);
    return `<div class="full-answer"><div class="mini-title">完整答案</div>${answerBody}${sourceHtml(question.sources)}</div>`;
  } catch (error) {
    error.message = `${question.id}: ${error.message}`;
    throw error;
  }
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

// A gitignored _handbook.local.md replaces _handbook.md so local-only sections never reach the repo.
function handbookFileIn(directory) {
  const local = join(directory, "_handbook.local.md");
  return existsSync(local) ? local : join(directory, "_handbook.md");
}

function findHandbookFiles() {
  if (!existsSync(handbooksRoot)) return [];
  return readdirSync(handbooksRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && existsSync(join(handbooksRoot, entry.name, "_handbook.md")))
    .map((entry) => handbookFileIn(join(handbooksRoot, entry.name)))
    .sort();
}

function writeIfChanged(filePath, content) {
  mkdirSync(dirname(filePath), { recursive: true });
  if (!existsSync(filePath) || readFileSync(filePath, "utf8") !== content) writeFileSync(filePath, content);
}

function removeStalePublicEntries(directory, expectedFiles, expectedDirs) {
  if (!existsSync(directory)) return;
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const filePath = join(directory, entry.name);
    if (entry.isDirectory()) {
      if (!expectedDirs.has(entry.name)) rmSync(filePath, { recursive: true, force: true });
      continue;
    }
    if (entry.isFile() && !expectedFiles.has(entry.name)) unlinkSync(filePath);
  }
}

function removeStaleQuestionFiles(directory, expectedIds) {
  if (!existsSync(directory)) return;
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    if (!entry.isFile() || !entry.name.endsWith(".json")) continue;
    if (!expectedIds.has(entry.name.slice(0, -5))) unlinkSync(join(directory, entry.name));
  }
}

function toCatalogEntry(handbook) {
  return {
    schemaVersion: handbook.schemaVersion,
    id: handbook.id,
    slug: handbook.slug,
    title: handbook.title,
    shortTitle: handbook.shortTitle,
    edition: handbook.edition,
    audience: handbook.audience,
    description: handbook.description,
    updatedAt: handbook.updatedAt,
    stats: handbook.stats,
    indexPath: `/content/${handbook.id}/index.json`,
    sections: handbook.sections.map((section) => ({
      id: section.id,
      title: section.title,
      description: section.description,
      questionCount: section.questions.length,
    })),
  };
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
  const cardChunks = {};
  const catalog = questions.map((question) => ({ id: question.id, sectionId: question.sectionId, title: question.title }));
  const sections = handbook.sections.map((section) => {
    const sectionQuestions = questions
      .filter((question) => question.sectionId === section.id)
      .sort((left, right) => left.order - right.order || left.title.localeCompare(right.title, "zh-Hans-CN"));
    if (!sectionQuestions.length) fail(handbook.filePath, `section ${section.id} has no published questions`);
    const answerPath = `/content/${handbook.id}/${section.id}.json`;
    const cardsPath = `/content/${handbook.id}/${section.id}.cards.json`;
    answerChunks[section.id] = Object.fromEntries(sectionQuestions.map((question) => [question.id, renderAnswer(question, catalog, handbook.slug)]));
    cardChunks[section.id] = Object.fromEntries(sectionQuestions.map((question) => [question.id, {
      titleHtml: renderMathInText(question.title),
      quickHtml: renderMathInText(question.quick),
    }]));
    return {
      ...section,
      cardsPath,
      answerPath,
      questions: sectionQuestions.map((question) => ({
        id: question.id,
        level: question.level,
        sectionId: question.sectionId,
        title: question.title,
        quick: question.quick,
        tags: question.tags,
        isRealInterview: question.isRealInterview,
        searchText: `${question.title.replace(/\$/g, "")} ${question.quick.replace(/\$/g, "")} ${question.tags.join(" ")}`.replace(/\s+/g, " ").trim(),
        answerPath: `/content/${handbook.id}/${section.id}/${question.id}.json`,
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
    mkdirSync(answerDirectory, { recursive: true });
    writeIfChanged(join(generatedRoot, `${handbook.id}.json`), `${JSON.stringify(generated)}\n`);
    writeIfChanged(join(answerDirectory, "index.json"), `${JSON.stringify(generated)}\n`);
    const expectedFiles = new Set(["index.json"]);
    const expectedDirs = new Set();
    for (const [sectionId, chunk] of Object.entries(answerChunks)) {
      expectedFiles.add(`${sectionId}.json`);
      expectedFiles.add(`${sectionId}.cards.json`);
      expectedDirs.add(sectionId);
      writeIfChanged(join(answerDirectory, `${sectionId}.json`), `${JSON.stringify(chunk)}\n`);
      writeIfChanged(join(answerDirectory, `${sectionId}.cards.json`), `${JSON.stringify(cardChunks[sectionId])}\n`);
      const questionDirectory = join(answerDirectory, sectionId);
      mkdirSync(questionDirectory, { recursive: true });
      const expectedIds = new Set();
      for (const [questionId, html] of Object.entries(chunk)) {
        expectedIds.add(questionId);
        writeIfChanged(join(questionDirectory, `${questionId}.json`), `${JSON.stringify(html)}\n`);
      }
      removeStaleQuestionFiles(questionDirectory, expectedIds);
    }
    removeStalePublicEntries(answerDirectory, expectedFiles, expectedDirs);
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
    mkdirSync(publicRoot, { recursive: true });
    removeStaleIndexes(new Set(results.map((result) => `${result.handbook.id}.json`)));
    const indexes = results.map((result) => result.handbook);
    const catalog = indexes.map(toCatalogEntry);
    writeIfChanged(generatedRegistry, `${JSON.stringify(indexes)}\n`);
    writeIfChanged(generatedCatalog, `${JSON.stringify(catalog)}\n`);
    writeIfChanged(join(publicRoot, "catalog.json"), `${JSON.stringify(catalog)}\n`);
    const staleRegistry = join(publicRoot, "registry.json");
    if (existsSync(staleRegistry)) unlinkSync(staleRegistry);
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
