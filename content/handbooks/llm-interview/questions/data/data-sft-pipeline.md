---
id: data-sft-pipeline
section: data
order: 1
level: S
title: 如何从零构建高质量 SFT 数据？
quick: >-
  先定义 capability taxonomy，再做 seed task、真实 difficulty evolution、多候选生成、hard
  verifier/judge filtering、去重/污染检测、mixture 与 source-level
  ablation。数据质量最终由“带来多少增量能力”定义。
tags:
  - SFT Data
  - Synthetic Data
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>先定义 capability taxonomy，再做 seed task、真实 difficulty evolution、多候选生成、hard verifier/judge filtering、去重/污染检测、mixture 与 source-level ablation。数据质量最终由“带来多少增量能力”定义。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>一个可操作的 pipeline：</p><ol><li><b>Capability taxonomy：</b>先定义 math/code/chat/tool/agent/long-context 等能力空间，否则无法判断 coverage。</li><li><b>Seed tasks：</b>来自人工、production query、公开数据、synthetic generator。</li><li><b>Difficulty evolution：</b>增加 constraints、multi-step dependency、tool requirement、ambiguity、composition，而不是只 paraphrase。</li><li><b>K-candidate generation：</b>同一个 prompt 生成多个 candidate，为 rejection sampling / preference / verifier 留空间。</li><li><b>Hard verification first：</b>代码跑 tests、SQL execute、JSON parse、math exact/symbolic；实在无法硬验证再用 LLM judge。</li><li><b>Dedup & contamination：</b>exact、normalized、MinHash/LSH、semantic dedup，并对 eval benchmark 做 overlap 检查。</li><li><b>Mixture：</b>控制 p(domain)、p(difficulty|domain)、source temperature，不按原始 volume 无脑 concat。</li><li><b>Train & stratified eval：</b>按 skill/domain/difficulty 观察 gains 和 regression。</li><li><b>Ablation：</b>删除/加入每个 data source，测 ΔPerformance / ΔTokens，找到真正高效数据。</li></ol><p>所谓高质量至少包括 correctness、instruction following、reasoning validity、difficulty、diversity、novelty、information density、verifiability、coverage 与 deployment distribution match。</p><p>特别注意 teacher bias：strongest teacher 不一定产生最好 student data。Teacher 可能过长、风格单一、使用 student 无法复现的 implicit knowledge，或者生成 far-out-of-distribution traces；student 更需要“可学、可验证、覆盖能力边界”的数据。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>答案对但 CoT 错，能不能留？</summary><div class="follow-answer"><p>若 CoT 进入 loss，风险很大，会蒸馏 fake reasoning；可以只监督 final answer、重写 reasoning、或用 process verifier 筛掉。</p></div></details><details class="followup"><summary>数据越多为什么会掉点？</summary><div class="follow-answer"><p>低质/重复数据稀释高价值信号，domain mixture 失衡、风格/长度 bias、teacher shortcut、catastrophic interference 都可能导致负增益。</p></div></details><details class="followup"><summary>Mixing ratio 怎么选？</summary><div class="follow-answer"><p>先基于目标能力给 domain quota，再结合 per-source marginal gain、loss scaling、temperature sampling 做迭代；最终用 ablation 和 downstream metric 而不是 dataset size 决定。</p></div></details></div>
