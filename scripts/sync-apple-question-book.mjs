import { readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import matter from 'gray-matter';
import { loadCompanyRegistry, resolveQuestionCompanies } from '../lib/company-facets.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const books = join(root, 'content/handbooks');
const destination = join(books, 'apple-interview');
const registry = loadCompanyRegistry();
const decoding = new Set([
  'us-tech/apple-topk-sample', 'us-tech/coding-topk-nucleus',
  'us-tech/coding-beam-search', 'llm-interview/code-beam-search',
  'us-tech/coding-gumbel-max', 'us-tech/coding-spec-accept',
  'us-tech/msft-constrained-decode',
]);
const extras = new Set([
  'us-tech/coding-packed-lm', 'llm-interview/code-packed-mask',
  'us-tech/coding-attn-mask', 'llm-interview/code-linear-attn',
  'us-tech/p3a-openai-numpy-1nn-wx-b', 'us-tech/p3a-openai-autograd-hillis-steele-scan',
  'us-tech/coding-swa-mask', 'llm-interview/code-softmax-stable',
  'llm-interview/code-logprob-gather',
  'us-tech/coding-beam-search', 'llm-interview/code-beam-search',
  'us-tech/coding-gumbel-max', 'us-tech/coding-spec-accept',
  'us-tech/msft-constrained-decode',
]);

function files(directory) {
  return readdirSync(directory, { withFileTypes: true }).flatMap(entry =>
    entry.isDirectory() ? files(join(directory, entry.name))
      : entry.name.endsWith('.md') ? [join(directory, entry.name)] : []);
}
function category(book, data) {
  const id = data.id;
  if (decoding.has(`${book}/${id}`)) return 'decoding';
  if (book === 'llm-interview' || extras.has(`${book}/${id}`)) return 'tensor';
  if (book === 'data-team-interview') {
    if (data.section === 'overview') return 'guide';
    if (data.section === 'culture') return 'culture';
    if (data.section === 'hm-screen') return 'projects';
    if (data.section === 'labs' || data.section === 'cases') return 'research';
    if (data.section === 'frontier-release') return 'evaluation';
    if (data.section === 'good-data') return 'data';
    if (data.section === 'senior') {
      if (/privacy|ondevice|adapter|guided/.test(id)) return 'ondevice';
      if (/self-improve/.test(id)) return 'synthetic';
      if (/multimodal/.test(id)) return 'multimodal';
      if (/repro-lineage/.test(id)) return 'data';
      return 'projects';
    }
    if (data.section === 'posttrain-data') return /agent|tool|gui|env|swegym/.test(id) ? 'systems' : 'synthetic';
    if (data.section === 'tech-screen') {
      if (/packed|logprob|collate|token-accum|dpo-batch|rm-weighted|distill-forward|paper-gated/.test(id)) return 'tensor';
      if (/bootstrap|passk|kappa/.test(id)) return 'evaluation';
      if (/math-verifier|rejection/.test(id)) return 'synthetic';
      if (/pref-pair/.test(id)) return 'alignment';
      if (/clip|circular-padding/.test(id)) return 'multimodal';
      if (/knn|batchnorm|kfold|tabular|one-edit|decimal|ttl/.test(id)) return 'coding';
      if (/task-dag/.test(id)) return 'systems';
      return 'data';
    }
    if (/reward|pref|judge|annotator|length-hack|safety|zero-advantage/.test(id)) return 'alignment';
    if (/synth|teacher|curriculum|verifier/.test(id)) return 'synthetic';
    if (/mm-|audio|video|cvml-image/.test(id)) return 'multimodal';
    if (/tool-gap|traj-quality|flask|search-design|classifier-data|photo-ranking|video-summary/.test(id)) return 'systems';
    if (/mixture-defense/.test(id)) return 'projects';
    if (/data-mix|web-extract|longctx|replay|tokenizer|mixture-factorial/.test(id)) return 'data';
    return 'evaluation';
  }
  if (/mha-code|layernorm/.test(id)) return 'tensor';
  if (/kmeans|topk|nucleus/.test(id)) return 'coding';
  if (/foundat|afm-eval/.test(id)) return /eval/.test(id) ? 'evaluation' : 'ondevice';
  if (/mm-train|multimodal|audio-llm|vision-edge|token-prune|design-mm-assistant|design-multimodal/.test(id)) return 'multimodal';
  if (/agent|siri-grounded|design-voice|design-moderation/.test(id)) return 'systems';
  return 'ondevice';
}
const selected = [];
const foundExtras = new Set();
for (const book of readdirSync(books).filter(name => name !== 'apple-interview')) {
  const base = join(books, book, 'questions');
  let sourceFiles;
  try { sourceFiles = files(base); } catch (error) { if (error.code === 'ENOENT') continue; throw error; }
  for (const file of sourceFiles) {
    const {data} = matter(readFileSync(file, 'utf8'));
    if (data.status !== 'published') continue;
    const company = resolveQuestionCompanies({companies:data.companies, sectionId:data.section, tags:data.tags}, registry);
    const extra = extras.has(`${book}/${data.id}`);
    if (book !== 'data-team-interview' && !company.includes('apple') && !extra) continue;
    if (extra) foundExtras.add(`${book}/${data.id}`);
    selected.push({book, question:data.id, section:category(book,data), data, file,
      scope: extra ? (decoding.has(`${book}/${data.id}`) ? '跨公司/通用 decoding 迁移' : '跨公司/通用 tensor 迁移')
        : book === 'data-team-interview' ? 'AFM Data Team 备考' : 'Apple 标签题'});
  }
}
for (const expected of extras) if (!foundExtras.has(expected)) throw Error(`Missing transfer question ${expected}`);
const seen = new Set();
for(const item of selected){if(seen.has(item.question))throw Error(`Conflicting imported ID ${item.question}`);seen.add(item.question);}
const config = matter(readFileSync(join(destination,'_handbook.md'),'utf8')).data;
selected.sort((a,b)=>config.sections.findIndex(s=>s.id===a.section)-config.sections.findIndex(s=>s.id===b.section)
  || (a.data.order??9999)-(b.data.order??9999) || a.question.localeCompare(b.question));
const refs = selected.map((item,index)=>({book:item.book,question:item.question,section:item.section,order:index+20,scope:item.scope}));
writeFileSync(join(destination,'question-refs.json'),JSON.stringify(refs,null,2)+'\n');
const local = files(join(destination,'questions')).map(file=>({file,...matter(readFileSync(file,'utf8'))}));
const count = selected.length+local.length;
const escape = text=>String(text).replaceAll('|','\\|').replace(/\s+/g,' ').trim();
const rows = ['# Apple 面试 Question Book','',`本册共 **${count} 道题**：${selected.length} 道引用现有源题，${local.length} 道本册题（包含导读）。`,
'', '网页题库切换到 **Apple 面试题本**，或使用 `?book=apple-interview`。cumsum／矩阵／mask 位于第 02 章，无需再搜索日期标签。',
'', '范围：整本 Apple Foundation Models Data Team；仓库各手册所有 Apple 公司标签题；以及显式挑选的 tensor／scan／decoding 迁移练习。原帖题、二手面经、主题扩展与公开研究保留原标记，不按数量推断出题频率。',
'', '已有答案通过 question-refs.json 引用原始文件，网页可直接阅读与练习；源题更新后重新构建即可同步，原手册链接保留。掌握进度与练习草稿按手册分别保存。',
'', '## 推荐练习顺序','', '先做 3 道新题：[position IDs](questions/tensor/apple-mask-position-ids.md)、[文档起点与 mask](questions/tensor/apple-starts-doc-mask.md)、[压缩与还原](questions/tensor/apple-mask-pack-unpack.md)。再做 cu_seqlens、packed mask、ML 全流程与数据管线，最后进入合成、评测与偏好。',
'', 'Decoding 单列第 03 章：[解码练习路线](questions/decoding/apple-decoding-guide.md)。新增 [batch token selection](questions/decoding/apple-batched-token-selection.md)、[完整 batch greedy/sampling](questions/decoding/apple-batched-generation.md) 与 [完整 batched beam search](questions/decoding/apple-batched-beam-search.md)，包含独立 EOS、left padding、position IDs 与 KV cache。原单序列、单步和进阶题仍保留，支持范围见导读表格。端侧部署取舍仍见端侧章节。',
'', '新增全流程材料见第 14 章：两套 45 分钟技术模拟、两份带 CSV/JSONL 的诊断、端到端闭环、自我迭代演示、个人材料模板、五场 Panel 与 30 分钟 Director 模拟。Reward/Preference 第 08 章新增 20 道研究衍生题，其中 3 道可运行编程题。来源审计见 content/sources/apple-reward-prep-2026-10-26/README.md；题面与训练约定由本手册编写。',
'', '个人研究 Reference：[Jiabao Ji × AFM 完整参考稿](AFM-PERSONAL-REFERENCE.md)。基于公开主页、CV与论文，整理六条研究线、相关benchmark、英文表达与建议实验；网页版从第 12 章的 afm-personal-reference 进入。',
'', '三条数据 Pipeline：[Skill/Harness、Code、Multimodal Tool Use](AFM-DATA-PIPELINE-EXAMPLES.md)。第 12 章从 afm-pipeline-overview 进入；含来源、样本字段、data quality checks、SFT/偏好/RL视图和JSONL示意，均为面试设计方案。',
'', '口述参考：[26 道可直接练习的回答](AFM-ORAL-ANSWERS.md)。参考 Interview Query、IGotAnOffer、Hello Interview 和 Exponent/Aced 的公开示范重写；先读主回答，字段、公式与实验清单在每题的技术备查中展开。',
'', `全题回答逻辑：[${count} 题完整口述稿与 callout](AFM-ANSWER-GUIDES.md)。每题的情境、任务、做法/原因和结果/验证在 answer-guides 中单独维护；网页完整答案顶部显示。编程题使用输入约束、算法和正确性逻辑，个人故事不补造结果。`,
'', '网站参考题：[14 张卡的导读与来源](questions/guide/afm-web-reference-guide.md)。网页搜索「AFM 网站参考题」筛出本批；覆盖 coding、agent evaluation、data pipeline、reward/DPO、benchmark、judge bias、synthetic data、multimodal search 与项目追问。',
'', '术语约定：[English terminology](TERMINOLOGY.md)。专业名词直接使用英文，中文解释含义和选择；inference/reasoning、release gate/held-out evaluation set 按语境区分。',
'', '## 更新方法','', '`npm run apple:sync` 更新来源清单与本目录，然后 `npm run content:build`。新增 Apple 标签题自动进入下次同步；章节规则和补选迁移题在 scripts/sync-apple-question-book.mjs 中维护。',
'', '[一亩三分地原帖核对记录](../../sources/apple-forum-2026-10-26/README.md)。', ''];
for(const section of config.sections){
  const imported=selected.filter(item=>item.section===section.id);
  const own=local.filter(item=>item.data.section===section.id);
  rows.push(`## ${section.title}（${imported.length+own.length} 题）`,'',section.description,'', '| 题目 | 级别 | 依据/范围 | 复习要点 |','| --- | --- | --- | --- |');
  for(const item of own.sort((a,b)=>(a.data.order??9999)-(b.data.order??9999))){
    const link=relative(destination,item.file).replaceAll('\\','/');
    rows.push(`| [${escape(item.data.title)}](${link}) | ${item.data.level} | ${item.data.tags?.includes('AFM 网站参考题') ? '公开培训材料改编/导读' : '本册自拟/导读'} | ${escape(item.data.quick)} |`);
  }
  for(const item of imported){
    const link=relative(destination,item.file).replaceAll('\\','/');
    rows.push(`| [${escape(item.data.title)}](${link}) | ${item.data.level} | ${item.data.realInterview?'面经依据；细节见来源':'练习/研究'} · ${item.scope} | ${escape(item.data.quick)} |`);
  }
  rows.push('');
}
writeFileSync(join(destination,'README.md'),rows.join('\n')+'\n');
console.log(`Apple book: ${count} questions (${selected.length} references, ${local.length} local).`);
