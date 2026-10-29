/** Render-safe import of the payload from collect-drustz-materials.py. */
import fs from "node:fs";
import path from "node:path";
import matter from "gray-matter";
import { marked } from "marked";
import katex from "katex";
import { formatCodeBlock } from "../lib/code-formatting.mjs";
import { renderMarkdown } from "./build-content.mjs";

const payload = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const book = "drustz-interview-2026";
const target = `content/handbooks/${book}`;
const sourceDir = `content/sources/${book}`;
const staticDir = `public/materials/${book}`;
const report = {
  codeAsText: [],
  mathAsText: [],
  records: payload.cards.length,
};
const byId = new Map(payload.cards.map((c) => [c.id, c]));
const firstByFile = new Map();
for (const c of payload.cards)
  for (const p of c.paths) if (!firstByFile.has(p)) firstByFile.set(p, c);
const href = (c) => `?book=${book}&section=${c.section}&question=${c.id}`;
const blob = (p) =>
  payload.source + p.split("/").map(encodeURIComponent).join("/");

const terminology = Object.entries(
  JSON.parse(fs.readFileSync("content/terminology-english.json", "utf8")),
).sort((a, b) => b[0].length - a[0].length);
function terms(text) {
  for (const [from, to] of terminology) text = text.replaceAll(from, to);
  return text.replace(/集群/g, "cluster").replace(/簇/g, "cluster");
}

function notation(text, protect) {
  const sup = Object.fromEntries(
    [..."⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ"].map((c, i) => [c, [..."0123456789+-=()ni"][i]]),
  );
  const sub = Object.fromEntries(
    [..."₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ"].map((c, i) => [
      c,
      [..."0123456789+-=()aehijklmnoprstuvx"][i],
    ]),
  );
  return text.replace(
    /[A-Za-z0-9\u0370-\u03ffΣ]+(?:(?:[_^](?:\{[^{}\n]+\}|\([^()\n]+\)|[A-Za-z0-9\u0370-\u03ff]+))|[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ])+/g,
    (original) => {
      if (
        original.includes("_") &&
        !original.includes("^") &&
        original.split("_")[0].length > 1
      )
        return original;
      let tex = original
        .replace(/\^\(([^()]+)\)/g, "^{$1}")
        .replace(
          /[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ]+/g,
          (x) => "^{" + [...x].map((c) => sup[c]).join("") + "}",
        )
        .replace(
          /[₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ]+/g,
          (x) => "_{" + [...x].map((c) => sub[c]).join("") + "}",
        )
        .replace(/_([A-Za-z0-9]{2,})/g, "_{$1}")
        .replace(/^pass\^/, "\\mathrm{pass}^");
      try {
        katex.renderToString(tex, { throwOnError: true, strict: "ignore" });
        return " " + protect("$" + tex + "$") + " ";
      } catch {
        return protect("`" + original + "`");
      }
    },
  );
}

function clean(body, card) {
  const protectedParts = [];
  const protect = (text) => {
    const token = `DRUSTZIMPORTPROTECTED${protectedParts.length}END`;
    protectedParts.push(text);
    return token;
  };
  // Normalize list / quote indentation around fenced blocks before locating
  // marked tokens. This leaves their code text intact and makes source formatting repeatable.
  body = body.replace(
    /(^|\n)([ \t>]+)(`{3,}|~{3,})([^\n]*)\n([\s\S]*?)\n\2\3[ \t]*(?=\n|$)/g,
    (_whole, leading, prefix, delimiter, language, code) =>
      leading +
      "\n" +
      delimiter +
      language +
      "\n" +
      code
        .split("\n")
        .map((line) =>
          line.startsWith(prefix) ? line.slice(prefix.length) : line,
        )
        .join("\n") +
      "\n" +
      delimiter +
      "\n",
  );
  // marked also sees indented and unclosed code blocks that a fence regex misses.
  const codeTokens = [];
  marked.walkTokens(marked.lexer(body), (token) => {
    if (token.type === "code") codeTokens.push(token);
  });
  for (const token of codeTokens.sort((a, b) => b.raw.length - a.raw.length)) {
    let language = (token.lang || "text").split(/\s/)[0];
    let code = token.text;
    try {
      code = formatCodeBlock(code, language);
    } catch {
      report.codeAsText.push({ question: card.id, language });
      language = "text";
    }
    const delimiter = "`".repeat(
      Math.max(3, ...[...code.matchAll(/`+/g)].map((m) => m[0].length + 1)),
    );
    body = body.replace(
      token.raw,
      protect(`${delimiter}${language}\n${code}\n${delimiter}`) + "\n\n",
    );
  }
  body = body.replace(/(`+)([^`\n]*?)\1/g, (match) => protect(match));
  body = terms(body);
  // Adapt local links to the pinned source, resolving inside this book when a
  // single full-document card is available. Anchors continue to the source.
  body = body.replace(
    /(!?)\[([^\]\n]*)\]\(([^\s)]+)(?:\s+"[^"]*")?\)/g,
    (all, image, label, dest) => {
      if (/^(https?:|mailto:|\?book=|\/materials\/)/.test(dest))
        return image ? `[${label || "图片"}](${dest})` : all;
      const [rel, anchor] = dest.split("#");
      const original =
        card.paths.find((p) => p.endsWith(".md")) ||
        card.paths[0] ||
        "README.md";
      let resolved = path.posix.normalize(
        path.posix.join(
          path.posix.dirname(original),
          rel || path.posix.basename(original),
        ),
      );
      if (resolved.startsWith("../")) resolved = rel.replace(/^(\.\.\/)+/, "");
      const mapped = firstByFile.get(resolved);
      const link =
        mapped && !anchor && !image
          ? href(mapped)
          : blob(resolved) + (anchor ? "#" + anchor : "");
      return `[${label || "图片"}](${link})`;
    },
  );
  body = body
    .replace(/<summary>([\s\S]*?)<\/summary>/gi, "\n\n**$1**\n\n")
    .replace(/<\/?details\b[^>]*>/gi, "\n\n")
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<a\s+(?:id|name)=[^>]*>\s*<\/a>/gi, "");
  // Raw HTML is forbidden in authored Markdown; retain visible labels and
  // escape tag-like syntax such as <tool_call> outside code rather than drop it.
  body = body
    .replace(/<!--[\s\S]*?-->/g, "")
    .replace(/<\/?[A-Za-z][^>\n]*>/g, (t) =>
      t.replaceAll("<", "&lt;").replaceAll(">", "&gt;"),
    );
  body = body
    .replace(/简单测试怎么写/g, "测试示例")
    .replace(/，不是会员页面的逐字答案。/g, "。")
    .replace(/，不代表 Apple 原题。/g, "。");
  body = body.replace(/https?:\/\/[^\s<>)]+/g, (text, offset, source) =>
    source[offset - 1] === "(" ? protect(text) : protect(`[来源链接](${text})`),
  );
  body = body.replace(/questions\/\{id\}_\{slug\}\//g, (text) =>
    protect("`" + text + "`"),
  );
  body = body.replace(
    /^\$[ \t]*\n([\s\S]+?)\n\$[ \t]*$/gm,
    (_all, tex) => "$$\n" + tex + "\n$$",
  );
  body = body.replace(/([（(])\$(?=\s+(?:和|and))/g, "$1&#36;");
  // Unsupported LaTeX is retained verbatim as code; valid formulas remain math.
  body = body.replace(
    /\$\$([\s\S]+?)\$\$|\\\[([\s\S]+?)\\\]|\$([^$\n]+?)\$|\\\(([^\n]+?)\\\)/g,
    (whole, a, b, c, d) => {
      if (
        c &&
        /^[\d/]/.test(c) &&
        /[\u4e00-\u9fff]/.test(c) &&
        !/\\(?:text|mathrm)/.test(c)
      )
        return whole.replaceAll("$", "&#36;");
      try {
        katex.renderToString(a ?? b ?? c ?? d, {
          throwOnError: true,
          displayMode: a !== undefined || b !== undefined,
        });
        return protect(whole);
      } catch {
        report.mathAsText.push({ question: card.id, formula: whole });
        return protect(
          "`" + whole.replaceAll("`", "′").replaceAll("\n", " ") + "`",
        );
      }
    },
  );
  body = body
    .split(/(\]\([^\n)]*\))/g)
    .map((part, index) => (index % 2 ? part : notation(part, protect)))
    .join("");
  // Any remaining dollar is literal currency or shell notation, not paired math.
  body = body.replaceAll("$", "&#36;");
  body = body.replace(
    /DRUSTZIMPORTPROTECTED(\d+)END/g,
    (_t, i) => protectedParts[Number(i)],
  );
  return body.trim();
}

fs.mkdirSync(target, { recursive: true });
fs.rmSync(`${target}/questions`, { recursive: true, force: true });
fs.mkdirSync(sourceDir, { recursive: true });
const counters = {};
for (const card of payload.cards) {
  const previousCodeFallbacks = report.codeAsText.length;
  let body = clean(card.body, card);
  if (report.codeAsText.length > previousCodeFallbacks)
    body +=
      "\n\n代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。\n";
  if (card.key === "guide")
    body += `\n\n## 本地下载\n\n- [Code、Tests 与 Data ZIP](/materials/${book}/code-and-tests.zip)\n- [完整文件覆盖清单](/materials/${book}/source-manifest.json)\n- [MIT license](/materials/${book}/mit-license.txt)\n- [Deep-ML license](/materials/${book}/deepml-license.txt)\n`;
  const related = (card.extra.related || [])
    .map((id) => byId.get(payload.recordMap[id]))
    .filter(Boolean);
  if (related.length)
    body +=
      "\n\n## 对应题库卡片\n\n" +
      related
        .map((c) => `- [${c.title.replaceAll("]", "\\]")}](${href(c)})`)
        .join("\n");
  body += `\n\n---\n\n来源：[DrustZ / Mingrui Zhang · ${card.paths[0] || "原仓库"}](${blob(card.paths[0] || "README.md")})。${card.section === "deepml" ? "Deep-ML：Educational Use Only License。" : "作者整理资料；许可和第三方来源范围见阅读指南。"}\n`;
  try {
    renderMarkdown(body);
  } catch (e) {
    throw new Error(`${card.id} (${card.title}): ${e.message}`, { cause: e });
  }
  const order = (counters[card.section] = (counters[card.section] || 0) + 1);
  const data = {
    id: card.id,
    section: card.section,
    order,
    level: "A",
    title: notation(terms(card.title), (x) => x),
    quick: `${card.kind} · ${notation(terms(card.title), (x) => x)}`,
    companies: ["openai", "anthropic"].includes(card.extra.company)
      ? [card.extra.company]
      : [],
    tags: ["DrustZ", card.kind, payload.sections[card.section]],
    realInterview: false,
    status: "published",
    format: "markdown",
    updatedAt: "2026-10-28",
    sources: [
      {
        title: "DrustZ / Mingrui Zhang · pinned source",
        url: blob(card.paths[0] || "README.md"),
        type: "primary",
      },
    ],
  };
  if (card.extra.sourceUrl?.startsWith("http"))
    data.sources.push({
      title: "作者记录的原始来源",
      url: card.extra.sourceUrl,
      type: "secondary",
    });
  const dest = `${target}/questions/${card.section}/${card.id}.md`;
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.writeFileSync(dest, matter.stringify(body, data));
}
const guide = payload.cards.find((c) => c.key === "guide");
const metadata = {
  schemaVersion: 1,
  id: book,
  slug: book,
  title: "DrustZ · AI Interview Prep 2026",
  shortTitle: "DrustZ Interview Book",
  audience:
    "Research Engineer、MLE、Agent / ML System Design · DrustZ 资料整合",
  edition: "V1",
  updatedAt: "2026-10-28",
  description: `${payload.cards.length} 张资料卡，覆盖 OpenAI / Anthropic、ML Coding、Agent、ML System Design、Robotics 与 Labs；保留作者全文、代码、tests 与来源。阅读入口：${guide.title}。`,
  sections: Object.entries(payload.sections)
    .filter(([id]) => counters[id])
    .map(([id, title], i) => ({
      id,
      title: `${String(i + 1).padStart(2, "0")} · ${title}`,
      description: `DrustZ · ${title}`,
    })),
};
fs.writeFileSync(`${target}/_handbook.md`, matter.stringify("", metadata));
fs.writeFileSync(
  `${sourceDir}/manifest.json`,
  JSON.stringify(
    {
      ...payload,
      cards: payload.cards.map((c) => {
        const metadata = { ...c };
        delete metadata.body;
        return metadata;
      }),
    },
    null,
    2,
  ) + "\n",
);
fs.writeFileSync(
  `${staticDir}/source-manifest.json`,
  JSON.stringify({ commit: payload.commit, files: payload.manifest }, null, 2) +
    "\n",
);
fs.writeFileSync(
  `${sourceDir}/normalization-report.json`,
  JSON.stringify(report, null, 2) + "\n",
);
console.log(
  JSON.stringify({
    cards: payload.cards.length,
    sections: counters,
    codeAsText: report.codeAsText.length,
    mathAsText: report.mathAsText.length,
    guide: href(guide),
  }),
);
