import assert from 'node:assert/strict';
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { resolve } from 'node:path';
import matter from 'gray-matter';
import { splitQuestionStatement } from '../lib/question-statement.mjs';

const root = resolve(import.meta.dirname, '..');
const read = (file) => readFileSync(resolve(root, file), 'utf8');
const walk = (dir) => readdirSync(resolve(root, dir), { withFileTypes: true }).flatMap((e) => e.isDirectory() ? walk(`${dir}/${e.name}`) : e.name.endsWith('.md') ? [`${dir}/${e.name}`] : []);
const files = walk('content/handbooks/system-design/questions');
const linkedDesign = new Set();
let diagrams = 0;
for (const file of files) {
  const { data, content } = matter(read(file));
  const prompt = splitQuestionStatement(content);
  assert(prompt?.markdown.length > 180 && prompt.rest.length > 300, `${file}: standalone prompt and reference required`);
  assert.equal(data.collapseAnswer, true, file);
  assert(!data.tags.includes('完整编程练习'), file);
  for (const [, href] of content.matchAll(/\]\((\?book=[^)]+)\)/g)) {
    const p = new URLSearchParams(href.slice(1));
    const config = matter(read(`content/handbooks/${p.get('book')}/_handbook.md`)).data;
    assert(config.sections.some((s) => s.id === p.get('section')), href);
    assert(existsSync(resolve(root, `content/handbooks/${p.get('book')}/questions/${p.get('section')}/${p.get('question')}.md`)), href);
    if (p.get('question').startsWith('design-')) linkedDesign.add(p.get('question'));
  }
  for (const [, slug] of content.matchAll(/!\[[^\]]*\]\(\/system-design\/([a-z-]+\.svg)\)/g)) {
    const svg = read(`public/system-design/${slug}`);
    assert(svg.includes('<title') && svg.includes('<desc'), slug);
    assert(!/<script|onload=|<foreignObject/i.test(svg), slug);
    diagrams++;
  }
}
const evidence = JSON.parse(read('content/sources/system-design-2026-10-25/evidence.json')).entries;
for (const e of evidence) {
  const card = matter(read(`content/handbooks/system-design/questions/companies/${e.card}.md`)).data;
  assert(card.sources.some((s) => s.url === e.url), e.url);
  assert.equal(card.realInterview, e.evidence === 'existing-thread-review-record', e.card);
  assert.equal(e.reopenedThisRun, false);
}
assert.equal(new Set(evidence.map((e) => e.url)).size, evidence.length);
assert.equal(linkedDesign.size, 22);
console.log(`Checked ${files.length} standalone design cards, ${diagrams} diagrams, 22 linked design topics, ${evidence.length} evidence entries.`);
