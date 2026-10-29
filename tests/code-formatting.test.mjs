import assert from "node:assert/strict";
import test from "node:test";
import {
  codeLanguage,
  formatCodeBlock,
  decodeCodeEntities,
} from "../lib/code-formatting.mjs";
import { formatQuestionSource } from "../lib/format-question-source.mjs";
import {
  highlightCodeBlocks,
  renderMarkdown,
} from "../scripts/build-content.mjs";

test("Python formatting expands compact statements and preserves strings, comments and behavior", () => {
  const source =
    "def f(x,y):\n if x:return [x,y] # keep comment\n return '$HOME\\n'";
  const result = formatCodeBlock(source, "python");
  assert.match(
    result,
    /def f\(x, y\):\n {4}if x:\n {8}return \[x, y\] {2}# keep comment/,
  );
  assert.match(result, /return '\$HOME\\n'/);
  assert.equal(formatCodeBlock(result, "py"), result);
});

test("JS, JSON, YAML and Shell go through their formatters", () => {
  assert.equal(
    formatCodeBlock("const x={a:1,b:[2,3]}", "js"),
    "const x = { a: 1, b: [2, 3] };",
  );
  assert.equal(
    formatCodeBlock('{"a":1,"b":[2,3]}', "json"),
    '{ "a": 1, "b": [2, 3] }',
  );
  assert.equal(
    formatCodeBlock("a: [1,2]\nb: {c: 3}", "yaml"),
    "a: [1, 2]\nb: { c: 3 }",
  );
  assert.equal(
    formatCodeBlock('if true;then\necho "$HOME"\nfi', "sh"),
    'if true; then\n  echo "$HOME"\nfi',
  );
});

test("text, output, unknown languages and inline code remain literal", () => {
  const text = "def not_an_actual_program(\n  x ->   y  \n";
  for (const language of ["text", "plaintext", "txt", "mermaid"])
    assert.equal(formatCodeBlock(text, language), text);
  assert.equal(codeLanguage("", "import torch\nx=1"), "python");
  assert.equal(codeLanguage("text", "import torch"), "text");
  const source = "Before `x=1;y=2`\n\n```text\n" + text + "```\n\nAfter.";
  assert.equal(formatQuestionSource(source), source);
});

test("syntax errors are actionable and never silently become a successful format", () => {
  assert.throws(
    () => formatCodeBlock("def broken(:", "python"),
    /Cannot format python code block/,
  );
  assert.throws(
    () => formatCodeBlock('{"a":', "json"),
    /Cannot format json code block/,
  );
});

test("source migration changes fenced code only, preserves fences and is idempotent", () => {
  const source =
    '---\nid: unchanged\n---\n\nKeep  two spaces and `x=1`.\n\n~~~~python\ndef f(x,y):return x+y\n~~~~\n\n```python\nhtml="<pre><code>x=1</code></pre>"\n```\n';
  const result = formatQuestionSource(source);
  assert.ok(
    result.startsWith("---\nid: unchanged\n---\n\nKeep  two spaces and `x=1`."),
  );
  assert.match(result, /~~~~python\ndef f\(x, y\):\n {4}return x \+ y\n~~~~/);
  assert.match(result, /<pre><code>x=1<\/code><\/pre>/);
  assert.equal(formatQuestionSource(result), result);
});

test("legacy numeric entities decode once and live HTML uses the same formatter", () => {
  assert.equal(decodeCodeEntities("&#x27;a&#39; &amp;lt;"), "'a' &lt;");
  const source =
    '<pre><code data-lang="python">def f(x):return f&quot;{x[&#x27;id&#x27;]}&quot;</code></pre>';
  const result = formatQuestionSource(source, { legacyHtml: true });
  assert.match(result, /def f\(x\):\n {4}return f"\{x\['id'\]\}"/);
  assert.equal(formatQuestionSource(result, { legacyHtml: true }), result);
  const html = highlightCodeBlocks(source);
  assert.match(html, /hljs/);
  assert.equal(highlightCodeBlocks(html), html);
  assert.doesNotMatch(html, /&amp;#x27/);
});

test("legacy migration also protects HTML examples embedded in a Markdown code fence", () => {
  const source =
    "```python\nhtml='<pre><code>def f(x):return x</code></pre>'\n```\n";
  const result = formatQuestionSource(source, { legacyHtml: true });
  assert.match(result, /<pre><code>def f\(x\):return x<\/code><\/pre>/);
  assert.equal(formatQuestionSource(result, { legacyHtml: true }), result);
});

test("build rendering formats new Markdown blocks before highlighting without rewriting literal HTML", () => {
  const html = renderMarkdown("```python\ndef f(x,y):return x+y\n```");
  const visible = html.replace(/<[^>]*>/g, "");
  assert.match(visible, /def f\(x, y\):\n {4}return x \+ y/);
  const js = renderMarkdown("```javascript\nconst x={a:1}\n```");
  assert.match(js.replace(/<[^>]*>/g, ""), /const x = \{ a: 1 \};/);
});
