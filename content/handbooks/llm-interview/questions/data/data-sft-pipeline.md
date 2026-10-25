---
id: data-sft-pipeline
section: data
order: 1
level: S
title: 如何从零构建高质量 SFT 数据？
quick: "先定义要覆盖的能力类别，收集种子任务，再往里加真实约束和难度。每题生成多个候选，能硬验证的用可执行验证器，验证不了的再用 judge，然后去重、查污染，按领域、难度和来源混合。训练后逐个增减数据源，看每个源带来多少能力提升。"
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>先定义要覆盖的能力类别，收集种子任务，再往里加真实约束和难度。每题生成多个候选，能硬验证的用可执行验证器，验证不了的再用 judge，然后去重、查污染，按领域、难度和来源混合。训练后逐个增减数据源，看每个源带来多少能力提升。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>我会把它搭成一条从能力定义到 ablation 的 pipeline：先想清楚要覆盖哪些能力，再造题、加难度、多采样、硬验证、去重，最后靠分层评测和逐源 ablation 决定哪些数据留下。每一步都是为了后面能回答「这批数据到底有没有用」。</p><p>第一步是 capability taxonomy，先把 math、code、chat、tool、agent、long-context 这些能力空间定义出来，否则没法判断 coverage。种子任务可以来自人工、production query、公开数据和 synthetic generator。然后做 difficulty evolution：加 constraints、multi-step dependency、tool requirement、ambiguity、composition，只做 paraphrase 是加不出难度的。</p><p>造好题以后，同一个 prompt 生成多个 candidate，给后面的 rejection sampling、preference 和 verifier 留空间。验证优先用硬的：代码跑 tests、SQL 真正 execute、JSON 能 parse、数学做 exact 或 symbolic 比对，实在没法硬验证再用 LLM judge。接着做 dedup 和 contamination 检查，依次是 exact、normalized、MinHash/LSH、semantic dedup，并且对 eval benchmark 做 overlap 检查。</p><p>混合的时候控制 p(domain)、p(difficulty|domain) 和 source temperature，别按原始 volume 直接 concat。训练后按 skill、domain、difficulty 分层看 gains 和 regression，再对每个 data source 做删除或加入的 ablation，测 ΔPerformance / ΔTokens，看哪些 source 划算。</p><p>判断一条数据质量高不高，通常要看 correctness、instruction following、reasoning 是否成立、难度、diversity、novelty、信息密度、能不能验证、覆盖面，以及和部署分布是否匹配。</p><p>还要检查教师模型的偏差。最强的 teacher 不一定最适合给学生生成训练数据：它的回答可能过长、风格单一，依赖 student 复现不了的隐含知识，或者产生远超 student 当前能力的轨迹。student 需要的是能学会、能验证、并且覆盖能力边界的数据。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>答案对但思维链（CoT）错，能不能留？</summary><div class="follow-answer"><p>如果 CoT 参与 loss 计算，风险很大，会把假的 reasoning 蒸馏进去。可以只监督 final answer、重写 reasoning，或者用 process verifier 把它筛掉。</p></div></details><details class="followup"><summary>数据越多，为什么会掉点？</summary><div class="follow-answer"><p>因为低质或重复的数据会稀释高价值信号。domain mixture 失衡、风格或长度 bias、teacher shortcut、catastrophic interference，都可能带来负增益。</p></div></details><details class="followup"><summary>Mixing ratio 怎么选？</summary><div class="follow-answer"><p>先按目标能力给每个 domain 定 quota，再结合每个 source 的边际收益、loss scaling 和 temperature sampling 迭代调整。最后由 ablation 和下游指标说了算，dataset 有多大不是依据。</p></div></details></div>
