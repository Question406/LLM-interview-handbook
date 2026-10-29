---
id: drustz-6dd0baf66fac5efef2
section: mlsd
order: 192
level: A
title: >-
  20 · Exa 第二轮技术面：agentic search 的 retrieval / reranking / snippet / alignment ·
  11. 你的对位素材（这轮的个人弹药）⭐⭐
quick: >-
  作者文档章节 · 20 · Exa 第二轮技术面：agentic search 的 retrieval / reranking / snippet /
  alignment · 11. 你的对位素材（这轮的个人弹药）⭐⭐
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
## 11. 你的对位素材（这轮的个人弹药）⭐⭐

你刚做完的 [Decagon fine-tuning 项目](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/projects/decagon_finetune/README.md) 里，有三块**正好打在 Exa 的靶心上**。
面试里不要主动长篇讲，但被问到时能立刻拿出**带数字的真实实验**。

### 11.1 你实现过 Dr. GRPO —— 而他们博客里用的就是 Dr. GRPO

- 你在 L4 里手写了 GRPO，并**显式加了两个修正**：Dr. GRPO 去掉 length normalization（修长度偏置）与 std normalization（修难度偏置），以及 DAPO 的 clip-higher。
- **接话方式**："我看到你们那篇 RL 用的是 Dr. GRPO。我自己实现过它相对 vanilla GRPO 的两处修正——
  去 length norm 和去 std norm，分别对应长度偏置和难度偏置。"
- 延伸到 §5.3 那个「全组失败 → 组内优势全 0 → 白跑一组」的机制论证，这是你能超出博客的地方。
- 诚实边界：**你的 GRPO 只跑到"证明环境与梯度正确"，没跑到收敛**。这点要主动说，不要含糊。

### 11.2 你做过 hard negative 的**带对照组**ablation，并推翻了自己的结论 ⭐⭐⭐

这是你在这轮最强的一张牌，因为它同时命中 Exa 的两个痛点（hard negative、eval 可信度）。

| 配置 | 样本数 | recall@5（跨主题 5 折 CV） |
|---|---|---|
| MNRL in-batch | 306 | 0.600 ± 0.086 |
| `dup`（样本翻倍、**随机**负例）← 对照组 | 612 | 0.672 ± 0.091 |
| `hard`（同主题近邻做负例） | 612 | 0.711 ± 0.103 |

```text
in-batch 0.600 ──+0.072──▶ dup 0.672 ──+0.038──▶ hard 0.711
                 样本翻倍              难负例
                （占 65%）          （占 35%，2胜1平2负，符号检验 p=1.0）
```



**怎么讲**（60 秒版）：
> 我一开始报的是 hard negative 带来 +0.109。后来加了一个**样本数对齐的对照组**——
> 把 in-batch 的样本原样复制一份，负例仍然是随机的。结果三分之二的收益来自**样本翻倍**，
> 真正属于难负例的只有 +0.038，而且 5 折里只赢 2 折，几乎全部来自其中一折的 +0.212。
> **我把这条从收益里划掉了。**

**为什么这对 Exa 有价值**：hard negative mining 是他们必然在做的事，
而"没有 count-matched control 就把收益归给难负例"是这个领域最常见的错误。
再加一句：**同主题近邻里混着未标注的相关文档，当负例会伤召回 —— 这和你们拒绝 MS MARCO 的第一条理由是同一个问题的两面。**

### 11.3 你有一次「评测器与被评物同源」的量化翻车

- 你用 BM25 打分造 DPO 偏好对，得出"偏好方向是噪声"的结论；
- 后来发现**用来验证的独立指标本身选错了**：词汇重叠给 46.2%（≈随机），换成语义相似度是 **62.5%（p=0.014）** —— 信号一直在；
- 更深一层：真正的主因不是"打分器弱"，而是**评测器也是 BM25**，所以检索改进被系统性抹掉。

**接 §8 那条原则**。这个故事的价值在于：你不是在复述"要有好 eval"这句正确的废话，
而是**有一次自己踩进去、量出来、公开推翻自己的记录**。

### 11.4 retrieval-first 的负结果 → 正结果

- 微调生成式 query rewriter：**跨域完全失败**（模型只记住训练主题的术语）；
- 直接换检索器（BM25 → dense，零训练）：**recall@5 0.165 → 0.576**；
- 微调 bi-encoder（跨主题 5 折 CV）：**0.276±0.150 → 0.600±0.086，5/5 折全升，标准差还降了**。

**一句话结论**（这句很 Exa）：
> **当瓶颈在检索时，改检索器比微调生成器便宜一个数量级，而且泛化性完全不同。**

**还有一条方法论**：这个数据集主题间难度差 10 倍，单次 holdout 的数字纯由抽到哪几个主题决定
（同一个零训练模型，dev 上 0.576、test 上 0.012）。**所以必须跨主题 CV。**
→ 这直接呼应 Exa 拒绝 MS MARCO 的第二条理由：50 文档量级的语料预测不了十亿级表现。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/20_case_exa_agentic_search.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/20_case_exa_agentic_search.md)。作者整理资料；许可和第三方来源范围见阅读指南。
