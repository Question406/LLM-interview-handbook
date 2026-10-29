# Frontier Coding 扩展检索与来源记录 · 2026-10-28

本轮新增 20 张 canonical cards：Meta 8、OpenAI 6、xAI 6。同步创建 frontier-coding collection，按公司汇总原 us-tech / us-startup 可运行 cards 与本轮新增；共 117 张 coding + 1 张总览，shared 16 张只引用一次。

## 证据范围

- 一亩三分地 Maze Solver 公开页提供 debugging / keys / doors / directional tiles 题型。
- AceOffer 与 Land the Lab 是二手题型目录；付费完整题面未读取。新卡仅依据公开标题、摘要或免费题面整理，完整接口与 tests 自行编写。
- Land the Lab 若 individual URL cache miss，采用公司目录中的可见摘要作为来源；卡片引用可访问目录。
- Meta build bottlenecks individual page 可公开读取，沿用“单一 time-step target”的定义。
- OpenAI tree task route individual page 公开了 required tasks / start / end；非负 weights 为手册扩展。
- OpenAI rectangle 与 beat notation 的完整条件未公开；这两张明确为手册自定的题型扩展，realInterview=false。
- xAI JSON viewer 的 React 题型拆成 Python HTML renderer，按题型扩展处理。
- realInterview=true 的新卡有公开平台所列的 candidate-report 题型支持；接口并不视为逐字面经。其余标 false，保留平台关联与具体来源说明。
- Humans& 检索主要返回同一位候选人的 top-p 自述与镜像，没有新具体题面；未将该文章其他公司的题归入 Humans&。
- Thinking Machines Lab coding-round 讨论未披露具体 prompt；检索到的菲律宾同名企业面经与 SEO 推测题未纳入。两张既有官方机制练习继续按原类别展示。

## 检索主题

Meta AI-enabled maze / card game / word coverage / friend recommendation / string-search optimization；Meta unique prefix / plus-minus expression / build dependencies；OpenAI task-tree route / grid visit points / modular additions / file dedup / beat notation / sub-grid；xAI hierarchical limiter / cleaning Parquet documents / courier pay / JSON viewer / decimal binary palindromes / concurrent scheduler；Humans& coding / top-p；Thinking Machines Lab coding interview experiences。

具体来源与文件清单见 cards.json，各 card 也有 sources front matter 与首段来源说明。117 是练习卡数量，不作为独立面经数或题型频率。

## 验证

`python3 scripts/check-frontier-coding-expanded.py` 从 Markdown 提取每张实际展示的 implementation 与 tests，在独立 subprocess 中运行；20/20 通过。全部只用 standard library。

`node scripts/sync-frontier-coding-book.mjs` 重新扫描 canonical source books，同步 refs 并打印章节计数；不会复制题解正文。
