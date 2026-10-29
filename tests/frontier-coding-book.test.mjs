import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import matter from 'gray-matter';
import { validateCodingStatement } from '../lib/question-statement.mjs';
import { validateQuestionReferences } from '../lib/handbook-references.mjs';
const read = path => readFileSync(new URL(`../${path}`, import.meta.url), 'utf8');
const additions = JSON.parse(read('content/sources/frontier-coding-expanded-2026-10-28/cards.json'));
const refs = JSON.parse(read('content/handbooks/frontier-coding/question-refs.json'));

test('expanded cards have standalone contracts, actual examples, runnable code and sources', () => {
  assert.equal(additions.length, 20);
  for (const entry of additions) {
    const { data, content } = matter(read(entry.file));
    assert.equal(validateCodingStatement(content), null, entry.id);
    assert.ok(data.sources?.every(source => /^https:\/\//.test(source.url)), entry.id);
    assert.equal((content.match(/^```python$/gm) || []).length, 2, entry.id);
    assert.equal((content.match(/^## 简单测试怎么写$/gm) || []).length, 1, entry.id);
    assert.match(content, /## 回答思路/);
    assert.ok(refs.some(ref => ref.question === entry.id && ref.book === entry.book), entry.id);
  }
});

test('five-company collection preserves all coding references and renders imported exercises', () => {
  const book = JSON.parse(read('public/content/frontier-coding/index.json'));
  const chapters = new Set(book.sections.map(s => s.id));
  validateQuestionReferences(refs, chapters, 'frontier-coding');
  const questions = book.sections.flatMap(s => s.questions);
  assert.equal(new Set(questions.map(q => q.id)).size, questions.length);
  assert.equal(questions.filter(q => q.hasPractice).length, refs.length);
  assert.equal(questions.length, refs.length + 1);
  for (const ref of refs) {
    const q = questions.find(q => q.id === ref.question);
    assert.ok(q?.hasPractice, ref.question);
    assert.equal(q.sectionId, ref.section);
  }
  // Keep the original batch discoverable alongside the new batch and shared exercises.
  for (const id of ['meta-conv2d-from-scratch', 'openai-indexed-sequence-checkpoints',
    'humansand-top-p-live-debug', 'tml-lora-linear-forward-gradients']) {
    assert.ok(questions.find(q => q.id === id)?.hasPractice, id);
  }
  assert.ok(book.sections.find(s => s.id === 'shared').questions.length > 0);
  const question = questions.find(q => q.id === additions[0].id);
  const html = JSON.parse(read(`public${question.answerPath}`));
  assert.match(html, /原始手册题目/);
  assert.match(html, /maze_distance/);
});
