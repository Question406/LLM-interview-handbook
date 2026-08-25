---
id: data-semantic-dedup
section: data
order: 10
level: A
title: Semantic Dedup 怎么做而不过度删除？
quick: >-
  Embedding similarity 只代表语义接近，不代表训练信号重复。应先 coarse retrieve，再结合结构 / 答案 / metadata 判断「是否同一 training signal」，并对高价值多解法数据保留 diversity。
tags:
  - Data
  - Dedup
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: SemDeDup — semantic deduplication at web scale
    url: https://arxiv.org/abs/2303.09540
    type: primary
---

Embedding 高相似只说明语义接近，不说明训练信号重复。两个证明策略不同的题可能向量很近，却都该留；两个 prompt 措辞不同、解法模板完全一样，反而该并。这块容易把 cosine 阈值当唯一闸门。阈值一紧，高价值多解法被洗掉；一松，模板克隆继续占满梯度。流程必须是 **coarse retrieve → 信号判定 → 簇内挑选**，「相似就删」不够。面试里把去重率当 KPI 会系统性误杀稀有解法。

## 先召回，再判是不是同一信号

典型流水线：embedding ANN 拉高相似候选 → 规则或 cross-encoder / 小模型复核 → 聚类 → 每簇留代表。判定「同一 training signal」要看三件事是否同时接近：题意、答案/程序结构、推理模板。可把 prompt embedding、答案或 AST、reasoning signature、来源 metadata 拼成联合特征，而不是只比题面向量。

lexical / MinHash 近重（`data-minhash`）先做，语义层只处理逃过 n-gram 的改写。SFT 的 train/test 泄漏检查（`pdd-sft-template-dedup`）用同一套邻居，但决策更严：跨 split 的近邻默认可疑，簇内多解法则默认值得人工看。

## 实验：阈值要按价值校准

不要全局一个 cosine。按领域、长度、是否可验证分桶扫阈值，对照三列：去重后 token 数、分层 holdout 增益、被删样本的人工抽检（误杀率）。高价值推理/多解法簇提高保留配额；模板改写、安全套话、低信息 FAQ 收紧。代表样本选择优先：有 verifier 通过、人工金标、覆盖稀有约束的那条，而不是最长或最新的那条。

过度删除的失败模式是 holdout 变「好做」、OOD 多解法掉点。发布时报告每桶删除率与误杀抽检，而不是只报「去重了百分之多少」。语义去重是在删重复梯度，不是在把语料洗成单一风格。

簇内挑选不要默认「最长 / 最新」。更稳的键是：verifier 通过、覆盖稀有约束、来源可信、长度适中。同一数学题三种证法应能留下至少两条不同 proof signature；同一客服话术换称呼则留一条即可。阈值扫描要画「删除率 vs holdout」曲线，找拐点而不是抄 SemDeDup 论文的全局阈值。网页预训练和 SFT 指令的密度差一个数量级。面试里若对方说「cosine 大于 0.9 就删」，追问他们误杀抽检和多解法配额，没有就不算做成。

## 追问

- **相似但解法不同怎么办？** 保留 diversity：按 proof / 算法签名再切一刀，每簇可留 $k$ 条代表，而不是只留 1 条。
- **和 MinHash 谁先做？** lexical / MinHash 便宜且准，先砍克隆；语义层只处理改写。两套阈值分开校准。
- **阈值怎么定？** 分桶扫，看 holdout 增益和误杀抽检，不抄 SemDeDup 论文里的某个数当自己的门。
- **跨 split 近邻呢？** 训练侧可讨论保留；评测侧默认当泄漏，见 `data-contamination`。
