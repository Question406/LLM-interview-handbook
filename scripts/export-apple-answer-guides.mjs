import {readFileSync,writeFileSync} from 'node:fs';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import matter from 'gray-matter';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const base=join(root,'content/handbooks/apple-interview');
const book=JSON.parse(readFileSync(join(root,'public/content/apple-interview/index.json'),'utf8'));
const lines=['# Apple 面试：完整回答与思路','',`本稿包含当前题本全部 ${book.stats.questions} 题。每题先列背景、任务、做法与原因、结果或验证，再给口述回答。编程题原始实现、测试及全部来源仍在网页题本的原题内容中。`,'','设计方案没有实际结果时写验证条件；个人项目仍须填真实职责和指标。'];
for(const section of book.sections){
  lines.push('',`## ${section.title}`,'');
  for(const question of section.questions){
    const {data,content}=matter(readFileSync(join(base,'answer-guides',`${question.id}.md`),'utf8'));
    lines.push(`### ${question.title}`,'',`> **回答思路**  `,`> **背景：** ${data.situation}  `,`> **任务：** ${data.task}  `,`> **做法与原因：** ${data.approach}  `,`> **结果／验证：** ${data.result}`,'',content.replace(/^## /gm,'#### ').trim(),'',`[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=${section.id}&question=${question.id})`,'');
  }
}
writeFileSync(join(base,'AFM-ANSWER-GUIDES.md'),lines.join('\n')+'\n');
console.log(`Exported ${book.stats.questions} answer guides.`);
