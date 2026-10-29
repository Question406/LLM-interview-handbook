import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import matter from 'gray-matter';
import { validateQuestionReferences, collectionQuestionCatalog } from '../lib/handbook-references.mjs';
import { loadCompanyRegistry, resolveQuestionCompanies } from '../lib/company-facets.mjs';
import { linkQuestionRefs } from '../scripts/build-content.mjs';

test('collection references reject paths, duplicate IDs, self-imports and unknown chapters', () => {
  const sections = new Set(['tensor']);
  const valid = { book: 'us-tech', question: 'coding-packed-lm', section: 'tensor' };
  assert.equal(validateQuestionReferences([valid], sections, 'apple-interview')[0].order, 1);
  assert.throws(() => validateQuestionReferences([{ ...valid, book: '../us-tech' }], sections, 'apple-interview'), /invalid book/);
  assert.throws(() => validateQuestionReferences([{ ...valid, book: 'apple-interview' }], sections, 'apple-interview'), /own handbook/);
  assert.throws(() => validateQuestionReferences([valid, { ...valid, book: 'another' }], sections, 'apple-interview'), /duplicate/);
  assert.throws(() => validateQuestionReferences([{ ...valid, section: 'unknown' }], sections, 'apple-interview'), /unknown/);
  assert.throws(() => validateQuestionReferences([{ ...valid, order: -1 }], sections, 'apple-interview'), /order/);
});

test('selected related questions link inside the collection, other links retain their original book', () => {
  const selected = [{ id: 'local-picked', sectionId: 'tensor', title: 'Selected question' }];
  const source = [{ id: 'local-picked', sectionId: 'coding', title: 'Selected question' },
    { id: 'source-extra', sectionId: 'systems', title: 'Unselected related question' }];
  const catalog = collectionQuestionCatalog(selected, source, 'us-tech');
  const text = linkQuestionRefs('[[local-picked]] and [[source-extra]]', catalog, 'current-card', 'apple-interview');
  assert.match(text, /book=apple-interview&section=tensor&question=local-picked/);
  assert.match(text, /book=us-tech&section=systems&question=source-extra/);
});

function markdownFiles(directory) {
  if (directory instanceof URL) directory = fileURLToPath(directory);
  return readdirSync(directory, { withFileTypes: true }).flatMap(entry => entry.isDirectory()
    ? markdownFiles(join(directory, entry.name))
    : entry.name.endsWith('.md') ? [join(directory, entry.name)] : []);
}

test('Apple collection covers every canonical Apple-tagged question and the full Data Team handbook', () => {
  const root = new URL('../content/handbooks/', import.meta.url);
  const refs = JSON.parse(readFileSync(new URL('apple-interview/question-refs.json', root), 'utf8'));
  const pairs = new Set(refs.map(ref => `${ref.book}/${ref.question}`));
  const registry = loadCompanyRegistry();
  for (const entry of readdirSync(root, { withFileTypes: true })) {
    if (!entry.isDirectory() || entry.name === 'apple-interview') continue;
    const directory = new URL(`${entry.name}/questions/`, root);
    for (const file of markdownFiles(directory)) {
      const { data } = matter(readFileSync(file, 'utf8'));
      if (data.status !== 'published') continue;
      const companies = resolveQuestionCompanies({ companies: data.companies, sectionId: data.section, tags: data.tags }, registry);
      if (entry.name === 'data-team-interview' || companies.includes('apple')) {
        assert.ok(pairs.has(`${entry.name}/${data.id}`), `missing ${entry.name}/${data.id}`);
      }
    }
  }
});

test('Apple collection is published with complete local and imported exercises', () => {
  const book = JSON.parse(readFileSync(new URL('../public/content/apple-interview/index.json', import.meta.url), 'utf8'));
  const refs = JSON.parse(readFileSync(new URL('../content/handbooks/apple-interview/question-refs.json', import.meta.url), 'utf8'));
  const questions = book.sections.flatMap(section => section.questions);
  const local = markdownFiles(new URL('../content/handbooks/apple-interview/questions/', import.meta.url));
  assert.equal(questions.length, refs.length + local.length);
  assert.equal(new Set(questions.map(question => question.id)).size, questions.length);
  for (const id of ['apple-mask-position-ids', 'apple-starts-doc-mask', 'apple-mask-pack-unpack', 'coding-packed-lm']) {
    const question = questions.find(question => question.id === id);
    assert.ok(question?.hasPractice, id);
    assert.equal(question.sectionId, 'tensor');
    assert.match(question.answerPath, /^\/content\/apple-interview\/tensor\//);
  }
  const html = JSON.parse(readFileSync(new URL('../public/content/apple-interview/tensor/coding-packed-lm.json', import.meta.url), 'utf8'));
  assert.match(html, /原始手册题目/);
  assert.match(html, /book=us-tech(?:&amp;|&)section=coding/);
});

test('Apple decoding chapter includes complete beam search, batched beam step and sampling', () => {
  const book = JSON.parse(readFileSync(new URL('../public/content/apple-interview/index.json', import.meta.url), 'utf8'));
  const section = book.sections.find(section => section.id === 'decoding');
  assert.ok(section);
  for (const id of ['coding-beam-search', 'code-beam-search', 'apple-topk-sample', 'coding-spec-accept',
    'apple-batched-token-selection', 'apple-batched-generation', 'apple-batched-beam-search']) {
    assert.ok(section.questions.find(question => question.id === id)?.hasPractice, id);
  }
  assert.ok(section.questions.find(question => question.id === 'msft-constrained-decode'));
  assert.equal(new Set(book.sections.flatMap(section => section.questions).map(question => question.id)).size, book.stats.questions);
});
