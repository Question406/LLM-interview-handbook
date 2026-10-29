---
id: drustz-805bb8def61d10184d
section: mlsd
order: 185
level: A
title: >-
  20 · Exa 第二轮技术面：agentic search 的 retrieval / reranking / snippet / alignment ·
  4. 第二题 ⭐⭐⭐：给 agentic search 设计 reranking 这一层
quick: >-
  作者文档章节 · 20 · Exa 第二轮技术面：agentic search 的 retrieval / reranking / snippet /
  alignment · 4. 第二题 ⭐⭐⭐：给 agentic search 设计 reranking 这一层
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - ML System Design · 全流程
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/20_case_exa_agentic_search.md
    type: primary
---
## 4. 第二题 ⭐⭐⭐：给 agentic search 设计 reranking 这一层

> **题面可能长这样**："搜索返回 1000 个候选，我们要返回 top 10。设计 reranker。
> 延迟预算 100ms，QPS 500。"

### 4.1 第一句话：先问「重排是为谁排的」

**这是 agentic search 和传统搜索最大的区别，一开口就要点出来**：

| | 人用的搜索 | **agent 用的搜索** |
|---|---|---|
| 消费 top-几 | 前 3 条，position bias极强 | **全部 5–10 条一起进 context** |
| 排序重要吗 | 极重要（第 1 位 vs 第 3 位差很多） | **相对不重要，集合的覆盖度更重要** |
| 优化目标 | nDCG（位置折扣） | **答案落在集合里的概率**；应该优化 **set-level recall + 多样性**，不是 pointwise 相关性 |
| 失败代价 | 用户多点一下 | **agent 多搜一轮** → 延迟 ×N、成本 ×N（你们 RL 那篇量化过：好检索 = 少 62% search call） |
| 冗余 | 无所谓 | **有害**：5 条说同一件事 = 浪费 4 条的 context |

> 💬 **这段是本题的差异化开场**：
> "传统 reranker 优化 nDCG，因为人只看前三条。但 agent 把 5 条全读进 context——
> 位置折扣基本不适用，而**冗余是实打实的成本**。所以我会把目标从 pointwise 相关性
> 改成 **budget 约束下的 set-level 覆盖**，训练时用 listwise loss，评测时报 recall@k 和 α-nDCG（惩罚冗余），
> 而不只是 nDCG@10。"

### 4.2 级联：算力必须这样花

```text
十亿文档
   │  dense ANN（256维二值，10万簇）─┐
   │                                 ├─ RRF 融合 ─▶ ~1000 候选
   │  BM25 + WAND ───────────────────┘             （Canon：两路并行，无依赖自动并行）
   ▼
 ~1000
   │  L1：轻量重排（late interaction / 全维 embedding 重打分）
   ▼
  ~100
   │  L2：cross-encoder（真正的重排）
   ▼
   10
   │  L3（可选）：LLM listwise 重排 —— 只在 Deep / 高 effort 档开
   ▼
 返回
```



**为什么 L1 存在**：dense 那一路用的是**截断+量化**的向量（256 维二值）。
L1 可以用**全维 fp 向量**重算 top-1000 的分数 —— 这是几乎免费的精度回收。
**Matryoshka 天生就是给级联设计的**：粗筛用 256 维，精排用 4096 维，同一个模型，无需第二套索引。

> 💬 这句值得说：**"Matryoshka 在你们那里不只是省内存的技巧，它本身就是一个天然的两级级联。"**

### 4.3 算术：cross-encoder 能重排多少个

```text
N 个候选 × 512 token（query + 文档片段）
100M 参数 cross-encoder：FLOPs = 2 × 1e8 × 512N = 1.02e11 × N

预算 30ms，H100 有效 300 TFLOP/s → 9e12 FLOP
N = 9e12 / 1.02e11 ≈ 88
```

**→ 一张 H100 在 30ms 内能重排约 90 个文档（100M 参数、512 token）。**

由此推出的三个结论（都要说）：
1. **候选数 100 不是拍脑袋，是算力反推出来的。** 想重排 1000 个，要么模型缩到 10M，要么砍到 64 token（只用标题+首段），要么加 10 倍卡。
2. **QPS 500 意味着 500 × 30ms = 15 GPU-秒/秒 → 至少 15 张卡满打满算，实际留余量要 25–30 张。** 这是可以直接报给他的容量估算。
3. **模型不能大。** 一个 1B 的 cross-encoder 是 10×，直接出局。所以 web-scale reranker 的真实设计约束是「**在 100M 参数内把质量榨干**」，而不是「用最强的模型」。
   → 这正是**distillation**的用武之地：用大模型（甚至 LLM listwise）离线打标，蒸给 100M 的学生。

**降低单位成本的三条路**（按性价比）：

| 手段 | 收益 | 代价 |
|---|---|---|
| **Late interaction（ColBERT 式）** | 文档 token 向量**离线算好**，线上只做 query 编码 + MaxSim | 存储爆炸（每 token 一个向量）→ 必须量化，正好接他们的二值量化经验 |
| **文档侧截断** | 512 → 256 token，算力减半 | 长文档信息丢失 → 但可以先用 §3 的 highlights 挑出最相关的 256 token 再喂 reranker。**highlights 和 reranker 是互相喂的** ⭐ |
| **distillation到更小** | 100M → 30M，3× | 质量掉多少要实测；用 [06 §7.2] 的 listwise distillation（RankNet / margin-MSE） |

> ⭐ **highlights ↔ reranker 的耦合是本题最好的洞察**，而且正好横跨他自述的两个关键词：
> reranker 需要"文档里最相关的 512 token"才能判准，而这恰好就是 highlights 干的事；
> 反过来 highlights 只需要对 reranker 留下的候选跑。**两者共享 chunk embedding 缓存，可以合成一个 node。**
> Canon 里正是这个形状：rerank 拉一次结果缓存，snippet 抽取和安全过滤两个消费者并行跑在缓存上。

### 4.4 训练数据与负例（引 06，但补 agentic 特有的部分）

标准部分见 [06 §四/五/六](?book=drustz-interview-2026&section=mlsd&question=drustz-ffab78b0379e3934e2)。**agentic search 特有的三条**：

1. **没有 click。** agent 不点击。可用的隐式信号是：agent **是否基于这条结果给出了引用**、**是否在这条之后停止搜索**、**最终答案是否正确**。
   → 归因很难（5 条结果共同促成一个答案）。可用 **leave-one-out 反事实**：抽掉这条，答案还对吗？贵但干净。
2. **RL rollout 是免费的标注机。** 你们训 search agent 时会产生海量 (query, results, 最终对错) 三元组。
   这些可以反哺 reranker 的训练 —— **agent 的成功率就是 reranker 的 downstream label**。
   这是一个正反馈：好检索 → RL 更省样本 → 更多 rollout → 更好的 reranker 标签。
3. **query 分布是 agent 生成的，不是人写的。** agent 的 query 更长、更结构化、常带约束（"after 2025-08"、"official docs only"）。
   → 用人类 query 训的 reranker 在这个分布上会掉点。**必须用真实 agent query 训和评**（你们有 5000 条真实去标识 query）。

### 4.5 上线与回归

- **shadow 先跑**：新 reranker 与旧的并行，只记录不返回，比较 top-10 集合的 Jaccard 与各自的 groundedness。
- **切片必看**：query 长度、语言、domain 类别、**新鲜度**（近 7 天的页面）、**长文档**。均值达标而长文档退化是最常见的事故。
- **护栏**：p99 延迟、每查询 GPU-秒、**安全过滤后的结果数为 0 的比例**（这条最容易被忽略且最伤 agent —— 你们自己量过 SERP 有 6.74% 返回不足 5 条，方差就是这么来的）。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/20_case_exa_agentic_search.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/20_case_exa_agentic_search.md)。作者整理资料；许可和第三方来源范围见阅读指南。
