import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import matter from 'gray-matter';
import { loadCompanyRegistry, resolveQuestionCompanies } from '../lib/company-facets.mjs';
import { splitQuestionStatement } from '../lib/question-statement.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const companies = new Set(['meta', 'openai', 'xai', 'humansand', 'thinking-machines']);
const registry = loadCompanyRegistry();
const newCards = JSON.parse(readFileSync(join(root, 'content/sources/frontier-coding-expanded-2026-10-28/cards.json'), 'utf8'));
const priority = new Map(newCards.map((q, i) => [q.id, i]));
function files(folder) {
  return readdirSync(folder, { withFileTypes: true }).flatMap(entry => entry.isDirectory()
    ? files(join(folder, entry.name)) : entry.name.endsWith('.md') ? [join(folder, entry.name)] : []);
}
const selected = [];
for (const book of ['us-tech', 'us-startup']) {
  for (const file of files(join(root, 'content/handbooks', book, 'questions'))) {
    const { data, content } = matter(readFileSync(file, 'utf8'));
    const isPractice = data.tags?.includes('完整编程练习') || data.id?.startsWith('lc-') || /简单测试怎么写/.test(content);
    if (data.status !== 'published' || !isPractice || !splitQuestionStatement(content)) continue;
    const memberships = resolveQuestionCompanies({ companies: data.companies, sectionId: data.section, tags: data.tags }, registry);
    if (!memberships.some(company => companies.has(company))) continue;
    selected.push({ book, question: data.id, section: companies.has(data.section) ? data.section : 'shared' });
  }
}
selected.sort((a, b) => (priority.get(a.question) ?? 1000) - (priority.get(b.question) ?? 1000)
  || a.question.localeCompare(b.question));
const refs = selected.map((entry, i) => ({ ...entry, order: i + 1 }));
writeFileSync(join(root, 'content/handbooks/frontier-coding/question-refs.json'), `${JSON.stringify(refs, null, 2)}\n`);
const counts = Object.fromEntries(['meta', 'openai', 'xai', 'humansand', 'thinking-machines', 'shared']
  .map(section => [section, refs.filter(q => q.section === section).length]));
console.log(JSON.stringify({ codingCards: refs.length, newCards: newCards.length, counts }, null, 2));
