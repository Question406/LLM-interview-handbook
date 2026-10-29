import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { validateAnswerGuide } from '../lib/answer-guides.mjs';

const valid = {id:'sample',kind:'design',situation:'反馈可能有误。',task:'找出实际缺口。',approach:'固定候选检查。',result:'独立任务确认。'};
test('answer guides require a matching ID, supported kind and all reasoning steps', () => {
  assert.equal(validateAnswerGuide(valid, '具体回答', 'sample').task, valid.task);
  assert.throws(() => validateAnswerGuide(valid, '回答', 'other'), /match/);
  assert.throws(() => validateAnswerGuide({...valid,kind:'unknown'}, '回答', 'sample'), /kind/);
  for (const key of ['situation','task','approach','result']) {
    assert.throws(() => validateAnswerGuide({...valid,[key]:' '}, '回答', 'sample'), new RegExp(key));
  }
  assert.throws(() => validateAnswerGuide(valid, '', 'sample'), /spoken/);
});

test('every Apple answer starts with a visible question-specific roadmap', () => {
  const book=JSON.parse(readFileSync(new URL('../public/content/apple-interview/index.json',import.meta.url)));
  const questions=book.sections.flatMap(s=>s.questions);
  const unique=new Set();
  for(const q of questions){
    const html=JSON.parse(readFileSync(new URL(`../public${q.answerPath}`,import.meta.url)));
    assert.match(html,/^<div class="full-answer"><aside class="answer-roadmap" aria-label="回答思路">/,q.id);
    const end=html.indexOf('</aside>');
    const callout=html.slice(0,end);
    assert.equal((callout.match(/<dt>/g)??[]).length,4,q.id);
    assert.doesNotMatch(callout,/<details/,q.id);
    unique.add(callout);
    assert.match(html.slice(end),/可以这样回答<\/h2>/,q.id);
    if(q.hasPractice) assert.match(callout,/正确性检查/,q.id);
    else assert.ok(html.indexOf('<details class="design-reference">')>end,q.id);
  }
  assert.equal(unique.size,questions.length,'roadmaps must not be one repeated template');
  assert.equal(questions.length,340);
});

test('coding guides retain the original statement, implementation and executable checks',()=>{
  const html=JSON.parse(readFileSync(new URL('../public/content/apple-interview/tensor/apple-mask-position-ids.json',import.meta.url)));
  assert.match(html,/题目描述<\/h2>/);
  assert.match(html,/position_ids_from_mask/);
  assert.match(html,/简单测试怎么写/);
  assert.match(html,/cumsum/);
  const codingStart=html.indexOf('题目描述</h2>');
  assert.ok(codingStart>html.indexOf('</aside>'));
});
