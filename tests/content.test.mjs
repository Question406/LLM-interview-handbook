import assert from "node:assert/strict";
import { existsSync, readdirSync } from "node:fs";
import { readFile } from "node:fs/promises";
import test from "node:test";
import handbook from "../content/generated/handbooks/llm-interview-v2.json" with { type: "json" };
import registry from "../content/generated/registry.json" with { type: "json" };
import { highlightCodeBlocks, linkQuestionRefs, renderMarkdown, renderMathInHtml, renderMathInText } from "../scripts/build-content.mjs";

function markdownFiles(directory) {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const file = new URL(`${entry.name}${entry.isDirectory() ? "/" : ""}`, directory);
    return entry.isDirectory() ? markdownFiles(file) : (entry.name.endsWith(".md") ? [file] : []);
  });
}

test("the generated handbook has stable, complete metadata", () => {
  const questions = handbook.sections.flatMap((section) => section.questions);
  const files = markdownFiles(new URL("../content/handbooks/llm-interview/questions/", import.meta.url));
  assert.equal(handbook.sections.length, new Set(questions.map((question) => question.sectionId)).size);
  assert.equal(questions.length, files.length);
  assert.equal(new Set(questions.map((question) => question.id)).size, files.length);
  assert.equal(handbook.stats.questions, files.length);
  assert.ok(questions.every((question) => !Object.hasOwn(question, "titleHtml") && !Object.hasOwn(question, "quickHtml")));
  assert.ok(Array.isArray(handbook.companies));
  assert.ok(questions.every((question) => Array.isArray(question.companies)));
  assert.ok(questions.some((question) => question.companies.includes("alibaba")));
});

test("published questions are standalone Markdown sources", () => {
  const questionDirectory = new URL("../content/handbooks/llm-interview/questions/", import.meta.url);
  assert.equal(markdownFiles(questionDirectory).length, handbook.stats.questions);
  assert.equal(existsSync(new URL("../content/handbooks/llm-interview-v2.json", import.meta.url)), false);
});

test("new Markdown answers support math but reject raw HTML", () => {
  const html = renderMarkdown("行内公式 $x^2$ 和 \\(y^2\\)。\n\n$$\\mathcal{L}=0$$\n\n\\[z=1\\]");
  assert.match(html, /class="katex"/);
  assert.match(html, /katex-strut[^>]*style="height:/);
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

test("question linking preserves dollar replacement sequences in literal code", () => {
  const source = "Before `$T`, `$`, `$&`, and `$$`.\n\n```sh\necho '$` $& $$'\n```\n\nAfter.";
  const linked = linkQuestionRefs(source, [], "current-question");
  assert.equal(linked, source);
  const html = renderMarkdown(linked);
  assert.match(html, /<code>\$T<\/code>/);
  assert.match(html, /<code>\$<\/code>/);
  assert.equal((html.match(/Before /g) ?? []).length, 1);
  assert.equal((html.match(/After\./g) ?? []).length, 1);
});

test("coding answers keep comparisons and HTML examples literal while prose HTML stays forbidden", () => {
  const html = renderMarkdown('```python\nif 0 <= y < h and x > 0:\n    print("<button onclick=\\"run()\\" style=\\"color:red\\">x</button>")\n```');
  const visible = html.replace(/<[^>]+>/g, "");
  assert.match(visible, /&lt; h/);
  assert.match(visible, /onclick=/);
  assert.match(visible, /style=/);
  assert.equal(/<button\b/.test(html), false);
  assert.doesNotThrow(() => renderMarkdown('Use `<script>alert(1)</script>` literally.'));
  assert.throws(() => renderMarkdown('A list:\n\n- <img src=x onerror=alert(1)>'), /cannot contain raw HTML/);
});

test("fenced code is syntax-highlighted at build time", () => {
  const html = renderMarkdown("```python\ndef add(x):\n    return x + 1\n```");
  assert.match(html, /class="hljs language-python"/);
  assert.match(html, /hljs-keyword/);
  assert.match(html, />def</);
  assert.match(html, />return</);
});

test("legacy pre/code blocks keep highlighting hooks", () => {
  const html = highlightCodeBlocks('<pre><code data-lang="python">def f():\n    return 1</code></pre>');
  assert.match(html, /class="hljs language-python"/);
  assert.match(html, /hljs-keyword/);
  assert.equal(highlightCodeBlocks(html), html);
});

test("legacy answers render math without disturbing code or existing formulas", () => {
  const html = renderMathInHtml(
    '<p>ratio 是 $\\rho_t$，且 $A_t &gt; 0$。</p><pre><code>x = $raw$</code></pre>'
    + '<p><code>$literal$</code></p><span class="math display"><mjx-container>$svg$</mjx-container></span>$$\\mathcal{L}=0$$',
  );
  assert.equal((html.match(/class="math inline"/g) ?? []).length, 2);
  assert.equal((html.match(/class="math display"/g) ?? []).length, 2);
  assert.match(html, /<code>x = \$raw\$<\/code>/);
  assert.match(html, /<code>\$literal\$<\/code>/);
  assert.match(html, /<mjx-container>\$svg\$<\/mjx-container>/);
  assert.throws(() => renderMathInHtml("<p>$\\notARealCommand{x}$</p>"), /Undefined control sequence/);
});

test("card summaries render math and escape everything else", () => {
  const html = renderMathInText("摘要 $\\delta_t = r_t + \\gamma V_{t+1}$ 与 <b>字面量</b>");
  assert.equal((html.match(/class="math inline"/g) ?? []).length, 1);
  assert.match(html, /&lt;b&gt;字面量&lt;\/b&gt;/);
  assert.doesNotMatch(html, /<b>/);
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
  assert.equal(formulaQuestions, 58);
});

// Identifiers that name code, config, or protocol values rather than mathematical symbols.
// The stem must be at least two characters so single-letter math subscripts like r_t stay visible.
const codeIdentifiers = /\b(?:[a-z0-9]{2,}_[a-z0-9_]+|[A-Z0-9]{2,}_[A-Z0-9_]+)\b/g;
// Single-letter-stemmed names that coding questions quote verbatim from PyTorch code, not formulas.
const quotedCodeNames = /\b(?:d_model|d_head|x_even|x_odd)\b/g;

function stripMathSpans(html) {
  const marker = 'class="math';
  let output = "";
  let cursor = 0;
  while (cursor < html.length) {
    const markerIndex = html.indexOf(marker, cursor);
    if (markerIndex < 0) {
      output += html.slice(cursor);
      break;
    }
    const start = html.lastIndexOf("<span", markerIndex);
    if (start < cursor) {
      output += html.slice(cursor, markerIndex);
      cursor = markerIndex + marker.length;
      continue;
    }
    output += html.slice(cursor, start);
    let depth = 0;
    let index = start;
    while (index < html.length) {
      const open = html.indexOf("<span", index);
      const close = html.indexOf("</span>", index);
      if (close < 0) break;
      if (open !== -1 && open < close) {
        depth += 1;
        index = open + 5;
      } else {
        depth -= 1;
        index = close + 7;
        if (depth === 0) break;
      }
    }
    cursor = index;
  }
  return output;
}

function renderedProse(html) {
  return stripMathSpans(html)
    .replace(/<pre[\s\S]*?<\/pre>/g, " ")
    .replace(/<code[\s\S]*?<\/code>/g, " ")
    .replace(/`[^`]*`/g, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(codeIdentifiers, " ")
    .replace(quotedCodeNames, " ");
}

test("every formula reaches the page rendered, never as raw notation", async () => {
  const defects = [
    ["未消费的 TeX 定界符", /\$/],
    ["LaTeX 上下标花括号", /[_^]\{/],
    ["裸 caret 上标", /\^[A-Za-z\u0370-\u03ff(]/],
    ["未渲染的下标符号", /(?<![A-Za-z0-9_\\])[A-Za-z\u0370-\u03ff]_(?:[A-Za-z0-9]{1,5})(?![A-Za-z0-9_])/],
    ["Unicode 上下标拼凑", /[\u2080-\u209c\u2070-\u207f]/],
  ];
  const findings = [];
  const checkFragment = (label, html) => {
    const prose = renderedProse(html);
    for (const [defect, pattern] of defects) {
      const match = prose.match(pattern);
      if (match) findings.push(`${label}: ${defect} «${prose.slice(Math.max(0, match.index - 30), match.index + 30).trim()}»`);
    }
  };

  for (const handbook of registry) {
    for (const section of handbook.sections) {
      const cards = JSON.parse(await readFile(new URL(`../public${section.cardsPath}`, import.meta.url), "utf8"));
      const chunk = JSON.parse(await readFile(new URL(`../public${section.answerPath}`, import.meta.url), "utf8"));
      for (const question of section.questions) {
        checkFragment(`${handbook.id}/${question.id} [title]`, cards[question.id].titleHtml);
        checkFragment(`${handbook.id}/${question.id} [quick]`, cards[question.id].quickHtml);
        checkFragment(`${handbook.id}/${question.id} [answer]`, chunk[question.id]);
      }
    }
  }
  assert.deepEqual(findings, []);
});

test("KaTeX HTML keeps layout styles in every published fragment", async () => {
  const findings = [];
  for (const entry of registry) {
    for (const section of entry.sections) {
      const cards = JSON.parse(await readFile(new URL(`../public${section.cardsPath}`, import.meta.url), "utf8"));
      const chunk = JSON.parse(await readFile(new URL(`../public${section.answerPath}`, import.meta.url), "utf8"));
      for (const question of section.questions) {
        for (const [label, html] of [["title", cards[question.id].titleHtml], ["quick", cards[question.id].quickHtml], ["answer", chunk[question.id]]]) {
          const struts = html.match(/<span class="katex-strut"/g)?.length ?? 0;
          const styled = html.match(/<span class="katex-strut" style="/g)?.length ?? 0;
          if (struts !== styled) findings.push(`${entry.id}/${question.id} [${label}] unstyled struts ${struts - styled}/${struts}`);
        }
      }
    }
  }
  assert.deepEqual(findings, []);
});

test("large answers are split into lazy-loaded module chunks", async () => {
  for (const section of handbook.sections) {
    assert.equal(section.answerPath, `/content/llm-interview-v2/${section.id}.json`);
    assert.equal(section.cardsPath, `/content/llm-interview-v2/${section.id}.cards.json`);
    const chunkUrl = new URL(`../public${section.answerPath}`, import.meta.url);
    const chunk = JSON.parse(await readFile(chunkUrl, "utf8"));
    assert.deepEqual(Object.keys(chunk).sort(), section.questions.map((question) => question.id).sort());
    const first = section.questions[0];
    assert.equal(first.answerPath, `/content/llm-interview-v2/${section.id}/${first.id}.json`);
    const one = JSON.parse(await readFile(new URL(`../public${first.answerPath}`, import.meta.url), "utf8"));
    assert.equal(one, chunk[first.id]);
    assert.ok(section.questions.every((question) => !Object.hasOwn(question, "answerHtml")));
  }
});

test("browser catalog stays small and handbook indexes omit KaTeX HTML", async () => {
  const catalogUrl = new URL("../public/content/catalog.json", import.meta.url);
  const catalogBytes = (await readFile(catalogUrl)).byteLength;
  const catalog = JSON.parse(await readFile(catalogUrl, "utf8"));
  assert.ok(catalog.length >= 3);
  assert.ok(catalogBytes < 100_000);
  assert.doesNotMatch(JSON.stringify(catalog), /titleHtml|quickHtml/);
  const indexUrl = new URL("../public/content/llm-interview-v2/index.json", import.meta.url);
  const indexBytes = (await readFile(indexUrl)).byteLength;
  const index = JSON.parse(await readFile(indexUrl, "utf8"));
  assert.equal(index.sections[0].questions[0].titleHtml, undefined);
  assert.ok(indexBytes < 1_500_000);
});

const sampleCatalog = [
  { id: "fund-kl-directions", sectionId: "fundamentals", title: "Forward KL vs Reverse KL：Mode-Covering / Mode-Seeking 是什么意思？" },
  { id: "pt-opsd", sectionId: "posttrain", title: "OPSD 和 OPD 差在哪？同一套权重怎么当自己的老师？" },
  { id: "fund-kl-k1-k2-k3", sectionId: "fundamentals", title: "Schulman 的 $k_1/k_2/k_3$ 各估什么？数值无偏和梯度正确是一回事吗？" },
  { id: "pdd-sft-template-dedup", sectionId: "data", title: "拼多多大模型算法：SFT 数据怎样避免模板化，并做 train / test 去重？" },
  { id: "baichuan-case-library-construction", sectionId: "agent", title: "百川智能：Agent 的例子库应怎样创建？" },
  { id: "sys-verl-vs-slime", sectionId: "systems", title: "你用过 veRL 和 slime，面试官问两者差在哪、什么时候换？" },
  { id: "slime-async-train", sectionId: "systems", title: "slime 的异步训练怎么开？挪 `ray.get` 和 `train_async.py` 是一回事吗？" },
];

test("internal question links survive sanitizer; javascript hrefs do not", () => {
  const html = renderMarkdown("[下一题](?section=fundamentals&question=fund-kl-directions)");
  assert.match(html, /class="question-link"/);
  assert.match(html, /data-question-id="fund-kl-directions"/);
  const withBook = renderMarkdown("[下一题](?book=llm-interview&section=fundamentals&question=fund-kl-directions)");
  assert.match(withBook, /class="question-link"/);
  assert.match(withBook, /data-question-id="fund-kl-directions"/);
  assert.match(withBook, /book=llm-interview/);
  const blocked = renderMarkdown("[x](javascript:alert(1))");
  assert.match(blocked, /href="#"/);
  assert.doesNotMatch(blocked, /javascript:/);
});

test("related question mentions become internal links", () => {
  const html = renderMarkdown(linkQuestionRefs([
    "- Forward KL vs Reverse KL：Mode-Covering / Mode-Seeking 是什么意思？",
    "- Schulman 的 $k_1/k_2/k_3$ 各估什么？",
    "见 `pt-opsd` 与 [[fund-kl-directions|方向卡]]。",
    "主推导在「OPSD 和 OPD 差在哪？同一套权重怎么当自己的老师？」。",
  ].join("\n"), sampleCatalog, "fund-kl-posttrain-index"));

  assert.match(html, /class="question-link"/);
  assert.match(html, /data-question-id="fund-kl-directions"/);
  assert.match(html, /data-question-id="pt-opsd"/);
  assert.match(html, /data-question-id="fund-kl-k1-k2-k3"/);
  assert.match(html, /href="\?section=posttrain(?:&amp;|&)question=pt-opsd"/);
  assert.match(html, /<code>pt-opsd<\/code>/);
  assert.match(html, />方向卡</);
  assert.doesNotMatch(html, /href="#"/);
});

test("question refs skip code fences, unknown ids, and self links", () => {
  const html = renderMarkdown(linkQuestionRefs([
    "见 `batch_size` 和 `pt-opsd`。",
    "",
    "```text",
    "pt-opsd",
    "`pt-opsd`",
    "```",
    "",
    "[[pt-opsd]]",
  ].join("\n"), sampleCatalog, "pt-opsd"));

  assert.equal((html.match(/class="question-link"/g) ?? []).length, 0);
  assert.match(html, /<code>batch_size<\/code>/);
  assert.match(html, /<code>pt-opsd<\/code>/);
});

test("nested python lists like [[1]] stay literal", () => {
  const html = renderMarkdown(linkQuestionRefs("- $n=k=1$：`[[1]]`。\n\n```python\nassert permute([1]) == [[1]]\n```", sampleCatalog, "pt-opsd"));
  assert.doesNotMatch(html, /class="question-link"/);
  assert.match(html, /\[\[1\]\]/);
});

test("unknown wiki question ids fail the build", () => {
  assert.throws(() => linkQuestionRefs("见 [[not-a-real-question]]。", sampleCatalog, "pt-opsd"), /Unknown question id/);
});

test("a list item with one question id becomes a full-line link", () => {
  const linked = linkQuestionRefs("- 为什么 rollout 要重算：`pt-opsd`。不要只背公式。", sampleCatalog, "fund-kl-posttrain-index");
  assert.match(linked, /^- \[为什么 rollout 要重算：`pt-opsd`。不要只背公式。\]\(\?section=posttrain&question=pt-opsd\)$/m);
  const html = renderMarkdown(linked);
  assert.equal((html.match(/class="question-link"/g) ?? []).length, 1);
  assert.match(html, /data-question-id="pt-opsd"/);
});

test("full-line links keep math subscripts like nums[i]", () => {
  const html = renderMarkdown(linkQuestionRefs("- 下标 $nums[i]$ 仍指向 `pt-opsd`。", sampleCatalog, "fund-kl-posttrain-index"));
  assert.match(html, /data-question-id="pt-opsd"/);
  assert.match(html, /class="katex"/);
});

test("follow-up bullets keep inline id links instead of wrapping the whole FAQ", () => {
  const linked = linkQuestionRefs("- **最少跳跃次数？** 覆盖范围只能回答「能不能」。独立卡见 `pt-opsd`。", sampleCatalog, "fund-kl-k1-k2-k3");
  assert.match(linked, /\[`pt-opsd`\]\(\?section=posttrain&question=pt-opsd\)/);
  assert.doesNotMatch(linked, /^- \[\*\*最少跳跃次数/m);
});

test("a list item with two question ids keeps separate links", () => {
  const linked = linkQuestionRefs("- 见 `pt-opsd` 与 `fund-kl-directions`。", sampleCatalog, "company-pdd");
  assert.match(linked, /\[`pt-opsd`\]\(\?section=posttrain&question=pt-opsd\)/);
  assert.match(linked, /\[`fund-kl-directions`\]\(\?section=fundamentals&question=fund-kl-directions\)/);
  assert.doesNotMatch(linked, /^- \[见 /m);
});

test("nav cards link truncated titles and company-prefix variants", () => {
  const html = renderMarkdown(linkQuestionRefs([
    "- 拼多多：SFT 数据怎样避免模板化，并做 train / test 去重",
    "- 百川：Agent 的例子库应怎样创建",
    "- 你用过 veRL 和 slime，两者差在哪、什么时候换？",
    "- slime 的异步训练怎么开？",
    "- **后训练策略**：RLVR 的 verifier 与 fresh rollout；混合加训和 continue SFT 的适用条件。",
  ].join("\n"), sampleCatalog, "company-pdd"));
  assert.match(html, /data-question-id="pdd-sft-template-dedup"/);
  assert.match(html, /data-question-id="baichuan-case-library-construction"/);
  assert.match(html, /data-question-id="sys-verl-vs-slime"/);
  assert.match(html, /data-question-id="slime-async-train"/);
  assert.equal((html.match(/class="question-link"/g) ?? []).length, 4);
});

test("KL post-training index links its related cards", async () => {
  const chunk = JSON.parse(await readFile(new URL("../public/content/llm-interview-v2/fundamentals.json", import.meta.url), "utf8"));
  const html = chunk["fund-kl-posttrain-index"];
  assert.match(html, /data-question-id="fund-kl-directions"/);
  assert.match(html, /data-question-id="pdd-forward-reverse-kl"/);
  assert.match(html, /data-question-id="pt-sft-fwd-kl-vs-rlhf-rev-kl"/);
  assert.match(html, /data-question-id="pt-opsd"/);
  assert.ok((html.match(/class="question-link"/g) ?? []).length >= 20);
});

test("other nav cards also link out to related questions", async () => {
  const fundamentals = JSON.parse(await readFile(new URL("../public/content/llm-interview-v2/fundamentals.json", import.meta.url), "utf8"));
  const companies = JSON.parse(await readFile(new URL("../public/content/llm-interview-v2/companies.json", import.meta.url), "utf8"));
  const systems = JSON.parse(await readFile(new URL("../public/content/llm-interview-v2/systems.json", import.meta.url), "utf8"));
  const cases = [
    ["fund-pg-ppo-grpo-index", fundamentals, 10],
    ["company-pdd", companies, 20],
    ["company-bytedance", companies, 15],
    ["company-ant", companies, 15],
    ["sys-rl-intro-index", systems, 15],
    ["sys-llm-rl-framework-index", systems, 10],
  ];
  for (const [id, chunk, minLinks] of cases) {
    const html = chunk[id];
    assert.ok(html, `missing generated answer for ${id}`);
    const links = html.match(/class="question-link"/g) ?? [];
    assert.ok(links.length >= minLinks, `${id} expected >= ${minLinks} links, got ${links.length}`);
  }
});
