import ruff from "@astral-sh/ruff-wasm-nodejs";
import prettier from "@prettier/sync";

export const CODE_FORMAT_OPTIONS = Object.freeze({
  printWidth: 88,
  tabWidth: 2,
});

const aliases = {
  py: "python",
  python3: "python",
  js: "javascript",
  mjs: "javascript",
  cjs: "javascript",
  ts: "typescript",
  tsx: "typescript",
  yml: "yaml",
  sh: "bash",
  shell: "bash",
  shellscript: "bash",
  zsh: "bash",
  txt: "text",
  plaintext: "text",
  md: "markdown",
};
const parsers = {
  javascript: "babel",
  jsx: "babel",
  typescript: "typescript",
  json: "json",
  jsonc: "json",
  json5: "json5",
  yaml: "yaml",
  css: "css",
  scss: "scss",
  less: "less",
  html: "html",
  graphql: "graphql",
  markdown: "markdown",
  bash: "sh",
};
const cache = new Map();
let pythonWorkspace;

/** Explicit text and unknown languages are never guessed to be executable code. */
export function codeLanguage(info = "", source = "") {
  const name = info.trim().split(/\s+/, 1)[0].toLowerCase();
  if (name) return aliases[name] ?? name;
  return /^\s*(?:from \S+ import |import |def |class |async def )/m.test(source)
    ? "python"
    : "";
}

/** Formatting only: no lint fixes, import sorting, execution, or remote services. */
export function formatCodeBlock(source, info = "") {
  const language = codeLanguage(info, source);
  if (language !== "python" && !parsers[language]) return source;
  if (!source.trim()) return source;
  const key = `${language}\0${source}`;
  if (cache.has(key)) return cache.get(key);
  let formatted;
  try {
    if (language === "python") {
      pythonWorkspace ??= new ruff.Workspace(
        {
          "line-length": CODE_FORMAT_OPTIONS.printWidth,
          "indent-width": 4,
          format: { "quote-style": "preserve", "docstring-code-format": false },
        },
        ruff.PositionEncoding.Utf16,
      );
      formatted = pythonWorkspace.format(source);
    } else {
      formatted = prettier.format(source, {
        ...CODE_FORMAT_OPTIONS,
        parser: parsers[language],
        endOfLine: "lf",
        embeddedLanguageFormatting: "off",
        ...(language === "bash" ? { plugins: ["prettier-plugin-sh"] } : {}),
      });
    }
  } catch (cause) {
    throw new Error(
      `Cannot format ${language} code block: ${String(cause.message ?? cause)}. ` +
        "Use a valid code snippet; label prose, output, pseudocode, or deliberately invalid examples as text.",
      { cause },
    );
  }
  // Match marked's fence text convention; the renderer owns the final newline.
  const result = formatted.replace(/\n$/, "");
  cache.set(key, result);
  return result;
}

/** Decode exactly once, including the numeric entities used by legacy answers. */
export function decodeCodeEntities(source) {
  const named = {
    amp: "&",
    lt: "<",
    gt: ">",
    quot: '"',
    apos: "'",
    nbsp: "\u00a0",
  };
  return source.replace(
    /&(#x[\da-f]+|#\d+|amp|lt|gt|quot|apos|nbsp);/gi,
    (match, entity) => {
      if (entity[0] !== "#") return named[entity.toLowerCase()] ?? match;
      const hex = entity[1].toLowerCase() === "x";
      const point = Number.parseInt(entity.slice(hex ? 2 : 1), hex ? 16 : 10);
      return point <= 0x10ffff && !(point >= 0xd800 && point <= 0xdfff)
        ? String.fromCodePoint(point)
        : match;
    },
  );
}

export function encodeCodeEntities(source) {
  return source
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

export function legacyCodeLanguage(attributes) {
  return (
    attributes.match(/\blanguage-([^\s"']+)/i)?.[1] ??
    attributes.match(/\bdata-lang=["']?([^\s"'>]+)/i)?.[1] ??
    ""
  );
}
