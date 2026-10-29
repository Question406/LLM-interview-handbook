---
id: drustz-0364bde551eedd5fd3
section: mlsd
order: 184
level: A
title: >-
  20 · Exa 第二轮技术面：agentic search 的 retrieval / reranking / snippet / alignment ·
  3. 主推题 ⭐⭐⭐：设计 Exa Highlights（snippet generation）
quick: >-
  作者文档章节 · 20 · Exa 第二轮技术面：agentic search 的 retrieval / reranking / snippet /
  alignment · 3. 主推题 ⭐⭐⭐：设计 Exa Highlights（snippet generation）
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
## 3. 主推题 ⭐⭐⭐：设计 Exa Highlights（snippet generation）

> **题面可能长这样**："我们给 agent 返回网页内容。整页太长了，agent 的 context 烧不起。
> 设计一个系统，给定 (query, 一批网页)，返回最相关的片段。要求 p99 < 100ms。"

这是 Joshua 本人的领域，也是**外部候选人准备最少**的一块。下面是完整答案。

### 3.1 先问清楚（2 分钟，不要跳过）

| 问题 | 为什么问 | 我会假设的默认值 |
|---|---|---|
| 消费者是 **agent 还是人**？ | 决定优化目标：人要可读连贯，agent 只要「答案在里面」 | **agent**。这直接把目标改成 groundedness 而非 readability |
| 一次请求 **几个文档、多长**？ | 决定算力预算 | 10 篇 × 平均 8k token |
| 文档来自**已索引**的还是**实时抓取**的 URL？ | 决定能不能预计算 | 两者都有，混合设计 |
| 输出是**固定预算**（500 字符）还是自适应？ | 决定是不是背包问题 | 客户端给字符预算 |
| 允许**改写/生成**还是必须**原文抽取**？ | 生成有hallucination风险且慢 | **抽取式**（保证可引用、可 grounding） |

**开场就把优化目标写出来**（这一句比后面任何架构都重要）：

> 优化的不是「摘要好不好」，是 **在 B 个 token 的预算下，下游 agent 能不能答对**。
> 所以指标是 **answer-in-context recall @ budget**，即 groundedness——你们 WebCode 里正是这么做的：
> 问「这段上下文里有没有答案」而不是「生成的答案对不对」，因为后者被生成模型的能力污染了。

### 3.2 架构 v1 → v3（阶梯式，别一上来就上最复杂的）

```text
                     ┌──────────────┐
 (query, docs) ─────▶│ 1. 切块       │  语义感知切分，不是固定窗口
                     │   chunking   │  重叠 20%，保留 heading 路径
                     └──────┬───────┘
                            │ ~40 chunks/doc × 10 doc = 400 chunks
                     ┌──────▼───────┐
                     │ 2. 打分       │  ← 这一层是全部的设计空间
                     └──────┬───────┘
                            │
                     ┌──────▼───────┐
                     │ 3. 选择       │  预算约束下的子集选择（不是简单 top-k）
                     └──────┬───────┘
                            │
                     ┌──────▼───────┐
                     │ 4. 拼装       │  相邻块合并、去重、按文档内顺序、加锚点
                     └──────────────┘
```



**第 2 层的三级阶梯**（面试里把三级都说出来，并说明**什么证据会让你升级**）：

| 级别 | 做法 | 算力 | 什么时候升级 |
|---|---|---|---|
| **v1 · bi-encoder** | chunk embedding 与 query embedding 点积。**已索引文档的 chunk embedding 在索引期就算好**（query 无关），线上只做 1 次 query encode + 400 次点积 | 已索引：**~1ms**；实时抓取：见下算术 | 基线。先量它离天花板多远 |
| **v2 · 小 cross-encoder** | (query, chunk) 联合编码。捕捉 bi-encoder 抓不到的词序/否定/精确匹配 | 见下算术 | 当 v1 的 recall@budget 与 oracle（穷举最优子集）差距 >5 个点 |
| **v3 · 抽取式 span model** | 直接预测 span 边界而不是打分固定 chunk。**切块本身就是有损的** —— 答案跨块或只占块的 10% 时，chunk 级打分会把噪声一起塞进预算 | 约等于 v2 | 当误差分析显示主要损失来自**切块边界**而非排序 |
| ~~v4 · 生成式~~ | LLM 生成摘录 | **超预算，且会hallucination** | ❌ 100ms 内不可能，且破坏可引用性 |

### 3.3 算术：证明 100ms 预算能不能装下 ⭐

**这段是本题的分水岭**。绝大多数候选人会画完架构就停，你要把数算给他看。

前向 FLOPs ≈ `2 × 参数量 × token 数`。

**bi-encoder 打分（实时抓取的文档，无法预计算）**
```text
10 篇 × 8k token = 80k token
100M 参数 encoder：2 × 1e8 × 8e4 = 1.6e13 = 16 TFLOP
H100 bf16 有效算力按 300 TFLOP/s（约 30% MFU，序列短、batch 不满）
→ 16 / 300 ≈ 53ms
```

**结论：正好卡在 100ms 预算内 —— 而且这解释了他们为什么用 8×A100 服务，以及为什么"不缓存"是可行的。**
（这也和他们 2024 年那篇 chunk+embed 的架构描述对上了。）

**cross-encoder 全量重排 400 个 chunk**
```text
400 chunk × 256 token = 102k token（query 拼进去，量级不变）
100M 参数：2 × 1e8 × 1.02e5 ≈ 2.0e13 = 20 TFLOP → ~68ms
```

**结论：v2 全量跑不进预算**（还要留出网络、切块、拼装的时间）。
→ **必须做级联**：bi-encoder 筛 400 → 40，cross-encoder 只跑 40 个。
```text
40 chunk × 256 token = 10k token → 2 TFLOP → ~7ms  ✅
```



**完整 p50 预算表**（我会在白板上写这张）：

| 阶段 | 预算 | 备注 |
|---|---|---|
| 切块（CPU） | 8ms | 这就是他们 Python→Rust 那篇解决的东西；GIL 卡住 IPC，rayon 后throughput 4× |
| query encode | 3ms | 一次，可与 chunk 前处理并行 |
| bi-encoder 打分 | 53ms | 实时抓取路径；已索引路径 **~1ms**（embedding 预计算） |
| cross-encoder 精排 top-40 | 7ms | |
| 预算内选择 + 拼装 | 2ms | |
| 序列化 / 网络 | 10ms | |
| **合计 p50** | **~83ms** | 留 17ms 给 p99 尾巴 —— 不够，见下 |

**p99 怎么办**（主动说，别等他问）：
- p99 的杀手不是均值，是**长文档**。一篇 200k token 的 API 参考页就能把预算打爆。
- 对策：① 按 token 数**分级路由**，超长文档先用廉价信号（heading 匹配、BM25）粗筛掉 90% 的块，再进 encoder；
  ② **超时降级**：cross-encoder 阶段带 deadline，超了就用 bi-encoder 的序 —— 这正是 Canon 的 pull-based + 级联取消能干净表达的东西；
  ③ 把「返回稍差的 highlight」和「返回整页」都当作合法降级，**但要打点区分**，否则 SLO 达标但质量在偷偷退化。

### 3.4 训练数据从哪来（他一定会追这个）

抽取式 snippet 没有天然标签。四类来源，按成本排序：

| 来源 | 怎么造 | 坑 |
|---|---|---|
| **弱监督 · 答案定位** | 有 (query, 答案) 的数据集（SimpleQA / NQ / 你们的 317 组 WebCode QA），在页面里定位答案字符串所在的 span → 正例 | 答案可能以不同措辞出现；**只做精确匹配会漏掉大半**，要用语义匹配兜底 |
| **distillation · 强模型打标** | 用大模型对 (query, chunk) 打 0–1 相关分，蒸给小模型 | 教师有position bias（偏爱开头的块）；要**打乱块顺序**取平均 |
| **下游反事实** | 把 chunk 塞给下游 agent，看**答对率**。这是最贴目标的信号 | 贵；而且被 agent 能力污染 —— 所以你们改用 discriminative（有没有答案）而不是 generative（答得对不对） |
| **锚文本 / 引用** | 别的页面引用这一页时用的那句话，天然是"这一页里最值得引的一段" | 分布偏向热门页 |

**我会主推第 1 + 第 3 的组合**：
用答案定位造大批弱标签训 bi-encoder，用下游反事实造少量高质量标签**只用来评测和calibration**，不用来训（量太小、方差太大）。

**负例是关键**（接 [06 §六](?book=drustz-interview-2026&section=mlsd&question=drustz-ffab78b0379e3934e2)）：
- **同文档内的其他 chunk 是最好的 hard negative** —— 主题相同、只差相关性，正好逼模型学 query-specific 而非 topic-level 相关。
- ⚠️ **陷阱**：同一页里常有多个块都含答案。把它们全当负例会直接教坏模型。
  这和 Exa 拒绝 MS MARCO 的第一条理由（稀疏标注造成**假负例**）是同一个问题。
  解法：多正例 / soft label，或者只把「与正例语义相似度低于阈值」的块当负例。
- 我**实际测过这个的对照实验**，见 §11.2 —— 这是我在这题上最强的个人素材。

### 3.5 Eval：三层，且第一层最容易做错

| 层 | 指标 | 怎么算 |
|---|---|---|
| **① 内在** | **answer-in-context recall @ budget** | 固定 500 / 1k / 4k 字符预算，答案（语义匹配）是否落在返回的片段里。**画成 recall-vs-budget 曲线，不要只报一个点** —— 你们那两个数字（500 字符 ≈ 8000 字符、4k > 32k）本质就是这条曲线上的两点 |
| ② 对照 | 与 **oracle 子集**的差距 | 穷举/贪心选出预算内最优子集作为上界。**报「离上界还差多少」比报绝对值有信息量得多** |
| ③ 下游 | agent 端到端答对率、总 token、search call 次数 | 这是钱；但方差大，需要足够样本量 |

**baseline 阶梯**（必须报，否则数字没有意义）：
`整页前 N 字符` → `随机 N 字符` → `BM25 选块` → `零训练 bi-encoder 选块` → 你的模型。
你们博客里那个 **60% vs 6%** 大概率就是「模型 vs 整页前 N 字符」，这个 baseline 在长文档上极弱，
所以**我会同时报 BM25 baseline**，那才是诚实的对照。

> 💬 **可以直接说的一句**：
> "我注意到你们 highlights 那篇报的是 vs 全文截断。我会额外加一条 BM25 选块的 baseline ——
> 在长 API 文档上截断这个 baseline 弱得不正常，报它会高估收益。"
> （这展示你会读别人的数字，而不是复述。风险可控：这是方法论建议，不是指责。）

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/20_case_exa_agentic_search.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/20_case_exa_agentic_search.md)。作者整理资料；许可和第三方来源范围见阅读指南。
