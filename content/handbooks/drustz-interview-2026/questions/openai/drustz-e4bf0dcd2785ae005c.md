---
id: drustz-e4bf0dcd2785ae005c
section: openai
order: 133
level: A
title: >-
  Compute the Distribution of LLM Decoding Stopping Time and Build a Strategy
  Against Adversaries
quick: >-
  original-structured-preparation-guide · Compute the Distribution of LLM
  Decoding Stopping Time and Build a Strategy Against Adversaries
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/7c43fee5-fd93-40b0-b610-b533299b665f
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# LLM Decoding Stopping Time：分布估计与策略

> 只有标题可确认；“adversaries”的能力、目标函数和交互规则都没有公开。下面提供一个可讨论的数学框架，不把它包装成标准答案。

## 可以怎样建模

令随机变量 `T` 表示一次decoding产生 EOS 前的 token 数。根据历史样本 `t1...tn` 估计：

- PMF：`P(T=t)`；
- CDF：`F(t)=P(T<=t)`；
- survival：`S(t)=P(T>t)`；
- discrete hazard：`h(t)=P(T=t | T>=t)`。

经验分布可通过长度频数和 prefix sum 在线性时间建立；如果需要平滑尾部，可明确选择几何、negative-binomial 或 survival model，并用 held-out likelihood 校验，而不是默认某个分布。

## 策略框架

先问清楚 adversary 能做什么：选择 prompt、改变分布、隐藏部分观测，还是在给定总 variation / KL budget 下扰动？然后把策略写成 minimax：

```text
minimize over policy π
maximize over allowed distributions Q
expected loss L(π, T),  T ~ Q
```



策略可以包含最大 token budget、动态早停、并行多个 decode、或在低 hazard 区域重启。若没有 adversary 约束，最坏分布可以让任何有限保证失效，所以题目必须给出 distribution family 或 budget。

## 复杂度

`n` 个长度样本、最大长度 `M` 时，直方图和 CDF 为 `O(n + M)` 时间、`O(M)` 空间；若只需若干 quantile，可排序为 `O(n log n)` 或使用 streaming quantile sketch。

## 边界

右删失样本、极长尾、EOS 缺失、sampling参数改变分布、prompt 分群、训练和线上分布漂移，以及 adversary 未受约束导致问题无有限解。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/7c43fee5-fd93-40b0-b610-b533299b665f)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
