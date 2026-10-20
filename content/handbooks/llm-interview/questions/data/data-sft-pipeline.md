---
id: data-sft-pipeline
section: data
order: 1
level: S
title: 如何从零构建高质量 SFT 数据？
quick: "先定义要覆盖的能力类别，收集种子任务，再增加真实约束和难度。每题生成多个候选，用可执行验证器或 judge 筛选，做去重和污染检查，然后按领域、难度和来源混合。训练后逐个增减数据源，检查它们是否带来能力提升。"
tags:
  - SFT Data
  - Synthetic Data
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-21'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>先定义要覆盖的能力类别，收集种子任务，再增加真实约束和难度。每题生成多个候选，用可执行验证器或 judge 筛选，做去重和污染检查，然后按领域、难度和来源混合。训练后逐个增减数据源，检查它们是否带来能力提升。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>落地时我一般按这条 pipeline：</p><ol><li><b>Capability taxonomy：</b>先定义 math/code/chat/tool/agent/long-context 等能力空间，否则无法判断 coverage。</li><li><b>Seed tasks：</b>来自人工、production query、公开数据、synthetic generator。</li><li><b>Difficulty evolution：</b>增加 constraints、multi-step dependency、tool requirement、ambiguity、composition，而不是只 paraphrase。</li><li><b>K-candidate generation：</b>同一个 prompt 生成多个 candidate，为 rejection sampling / preference / verifier 留空间。</li><li><b>Hard verification first：</b>代码跑 tests、SQL execute、JSON parse、math exact/symbolic；实在无法硬验证再用 LLM judge。</li><li><b>Dedup & contamination：</b>exact、normalized、MinHash/LSH、semantic dedup，并对 eval benchmark 做 overlap 检查。</li><li><b>Mixture：</b>控制 p(domain)、p(difficulty|domain)、source temperature，不按原始 volume 无脑 concat。</li><li><b>Train & stratified eval：</b>按 skill/domain/difficulty 观察 gains 和 regression。</li><li><b>Ablation：</b>删除/加入每个 data source，测 ΔPerformance / ΔTokens，看哪些 source 划算。</li></ol><p>高质量通常要看 correctness、instruction following、reasoning 是否成立、难度、diversity、novelty、信息密度、能不能验证、覆盖面，以及跟部署分布是否匹配。</p><p>还要检查教师模型的偏差。最强的 teacher 不一定最适合生成学生训练数据：回答可能过长、风格单一，依赖 student 无法复现的隐含知识，或产生远超 student 当前能力的轨迹。student 需要能学会、能验证，并覆盖能力边界的数据。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>答案对但思维链（CoT）错，能不能留？</summary><div class="follow-answer"><p>若 CoT 参与 loss 计算，风险很大，会把假 reasoning 蒸馏进去。可以只监督 final answer、重写 reasoning，或用 process verifier 筛掉。</p></div></details><details class="followup"><summary>数据越多为什么会掉点？</summary><div class="follow-answer"><p>低质或重复数据会稀释高价值信号。domain mixture 失衡、风格或长度 bias、teacher shortcut、catastrophic interference，都可能导致负增益。</p></div></details><details class="followup"><summary>Mixing ratio 怎么选？</summary><div class="follow-answer"><p>先按目标能力给 domain quota，再结合每个 source 的边际收益、loss scaling、temperature sampling 做迭代。最终用 ablation 和下游指标决定，不是看 dataset 有多大。</p></div></details></div>
