import { marked } from "marked";
import {
  formatCodeBlock,
  codeLanguage,
  decodeCodeEntities,
  encodeCodeEntities,
  legacyCodeLanguage,
} from "./code-formatting.mjs";

/** Rewrite only actual fenced code; never reflow prose, front matter, or inline code. */
export function formatQuestionSource(
  source,
  { legacyHtml = false, onBlock = () => {} } = {},
) {
  const edits = [];
  let cursor = 0;
  let block = 0;
  marked.walkTokens(marked.lexer(source), (token) => {
    if (token.type !== "code" || token.codeBlockStyle === "indented") return;
    const index = source.indexOf(token.raw, cursor);
    if (index < 0)
      throw new Error(
        "Cannot locate fenced code in its source; keep code fences outside indented lists/quotes.",
      );
    cursor = index + token.raw.length;
    const opening = /^( {0,3})(`{3,}|~{3,})([^\r\n]*)\r?\n/.exec(token.raw);
    if (!opening) return;
    const formatted = formatCodeBlock(token.text, token.lang ?? "");
    block += 1;
    onBlock({
      block,
      language: codeLanguage(token.lang ?? "", token.text),
      before: token.text,
      after: formatted,
    });
    if (formatted === token.text) return;
    const closing = new RegExp(
      `\\r?\\n {0,3}${opening[2][0]}{${opening[2].length},}[ \\t]*(?:\\r?\\n)*$`,
    ).exec(token.raw);
    if (!closing)
      throw new Error("Formatted code needs an explicit closing fence.");
    const indent = opening[1];
    const body = formatted
      .split("\n")
      .map((line) => (line ? indent + line : line))
      .join("\n");
    edits.push({
      start: index,
      end: index + token.raw.length,
      text: opening[0] + body + token.raw.slice(closing.index),
    });
  });
  let result = source;
  for (const edit of edits.reverse())
    result = result.slice(0, edit.start) + edit.text + result.slice(edit.end);
  // Only legacy-html documents contain live HTML code. Markdown can contain the
  // same tags literally inside Python strings; those must not be transformed.
  if (legacyHtml) {
    const fenceRanges = [];
    let fenceCursor = 0;
    marked.walkTokens(marked.lexer(result), (token) => {
      if (token.type !== "code" || token.codeBlockStyle === "indented") return;
      const start = result.indexOf(token.raw, fenceCursor);
      if (start >= 0) {
        fenceRanges.push([start, start + token.raw.length]);
        fenceCursor = start + token.raw.length;
      }
    });
    result = result.replace(
      /(<pre\b[^>]*>\s*<code\b([^>]*)>)([\s\S]*?)(<\/code>\s*<\/pre>)/gi,
      (match, opening, attributes, body, closing, offset) => {
        if (fenceRanges.some(([start, end]) => offset >= start && offset < end))
          return match;
        const before = decodeCodeEntities(body.replace(/\n$/, ""));
        const info = legacyCodeLanguage(attributes);
        const after = formatCodeBlock(before, info);
        block += 1;
        onBlock({ block, language: codeLanguage(info, before), before, after });
        return after === before
          ? match
          : opening + encodeCodeEntities(after) + closing;
      },
    );
  }
  return result;
}
