---
id: xiaohongshu-posttrain-gain
section: data
order: 181
level: A
title: 小红书 Hi lab：如何评估训练后的收益？搜索 top-k 该固定还是由模型选？
quick: >-
  收益要对照冻结的 checkpoint，在同一检索版本、同一 prompt、同一 decoding 下比，按能力桶报胜率、confidence
  interval 和回归，再看线上护栏，「平均分涨了」不算数。top-k 默认固定、按 query 类型分档，用 Recall@k
  对延迟的曲线选拐点；让模型动态选 k 要设硬上限和延迟预算，否则它会学会一直多要上下文。
tags:
  - Xiaohongshu
  - Evaluation
  - Retrieval
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 小红书Hi lab 日常实习 一面
    url: 'https://www.nowcoder.com/feed/main/detail/8f02e3837274408d9c94c312e8ee578d'
    type: candidate-first-hand
---

## 真题记录

- 公司：小红书
- 团队 / 岗位：Hi lab；日常实习
- 届别 / 流程：一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“是否有评估训练后的收益”**；**“搜索引擎召回的 top-k 值是固定还是模型选择”**

这两问我分开答。训练收益要做成对照实验：新旧 checkpoint 在同一 prompt、同一检索版本、同一 decoding 下比，按能力桶报胜率、confidence interval 和回归，再看线上护栏。top-k 默认固定、按 query 类型分档；让模型动态选 $k$ 也可以，但要有上限和延迟预算。没有冻结对照集的「感觉更好」不算收益，让 Agent 自己无限加大 $k$ 也不行。

先说收益。离线冻结一个 golden，分事实、多轮、安全几个能力桶看胜率，不用一个总分，再补上通用指令、安全的回归集。比如平均分涨了 $1$ 个点，但安全桶掉了，或者只在标注员常用的句式上涨，都算失败；小 golden 上的 $1$ 个点也可能只是噪声，所以要给 confidence interval，它当不了发版理由。多轮任务成功不能拿单轮 cross entropy loss（CE）代替（`xiaohongshu-multiturn-split`）。覆盖不足时，桶外的用户会受伤（`pdd-offline-eval-coverage`）。

对照一定要锁检索索引的版本。不锁的话，「涨分」可能来自新笔记入库，和训练没关系；检索改了、却把提升算到 SFT 头上，是很常见的错。所以收益报告里检索版本、prompt 版本、decoding 参数要并列写出来。线上用影子流量或小流量看采纳和投诉，护栏指标包括投诉、人工打回、延迟，别把评测集当调参集。overfitting 的信号是 dev 升、线上投诉也升，或者换一批同分布的新 query 就骤降。离线和线上的缺口见 `data-offline-online-metric-gap`，生成评测怎么操作见 `xiaohongshu-gen-eval`。原帖也强调落地比背 DAPO 公式重要，从 SFT 换 DAPO / GRPO 之前，先保证这把尺子稳，算法对比见 `xiaohongshu-dapo-vs-grpo`。

再说 top-k。它是上下文预算，和模型个性没关系。起步固定 $k$，或者按 query 类型分档：事实短答用小 $k$，调研类用大 $k$，ID / 精确字段类用小 $k$ 甚至 BM25 直达。默认值用 Recall@$k$ 对延迟画曲线，选拐点，Recall 的定义要先对齐（`byte-recall-at-5`）。按 query 分类器分档时，分类错了宁可偏小 $k$ 再澄清，别默认拉满。

动态 $k$ 合法的触发条件是「当前证据不足以支撑断言，而且延迟预算还没用完」，并且要有硬上限。不计成本的话，Agent 会学会刷上下文：多要文档总能让「看起来有证据」的 judge 分变高，可延迟变差、噪声进入生成，hallucination 也不一定降。所以实现上要把 $k$ 写进轨迹，才能把「多召回」和「真的会答」拆开分析。真要上线，还要报扩召回的触发率、平均 $k$、延迟 P95 和任务成功率的联合曲线；触发很多、成功率不升，就是在刷上下文。

原帖把收益评估和 top-k 放在一起问，考的就是这一点：后训练的增益不能和检索改动混在一本账里，检索超参也不能交给政策无限加上下文。

## 追问

**收益的最小报告长什么样？**
相对冻结 checkpoint 的分组胜率，加回归、延迟和安全护栏。没有对照集的主观感受不算。

**动态 $k$ 什么时候值得做？**
漏召能测出来、扩 $k$ 有明确增益、延迟预算也允许的时候。否则固定分档更稳。

**这题和 DAPO / GRPO 那题怎么接？**
先能测准收益，再谈算法。测不准的时候换目标函数没有意义。

**平均分涨了、投诉也涨了，怎么办？**
先看安全和长尾桶，再查是不是 overfitting 了 golden，别继续加训。

**$k$ 和切窗谁先锁？**
两个都放进同一张配置单（`xiaohongshu-multiturn-split`），一起做训推差分。
