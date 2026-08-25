---
id: company-baichuan
section: companies
order: 15
level: A
title: 百川智能：大模型实习 / Agent 应重点准备什么？
quick: >-
  同一轮会从例子库、Query 改写、三路召回、RAGAS、SQL 安全、表格 Agent 增强一路问到线上评估和使用量。我准备时按「数据 →
  检索 / Agent → 安全 → 线上指标」串起来，检测率和 adoption 要能量化。
tags:
  - Baichuan
  - 真题导航
  - Agent
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 百川智能大模型实习一面 压力好大
    url: https://www.nowcoder.com/feed/main/detail/e3e6543bd5ab478292b74a48f031c530
    type: candidate-first-hand
  - title: 百川智能大模型实习一面
    url: https://www.nowcoder.com/feed/main/detail/290832d2cd3242c386e56f27f975bce3
    type: candidate-first-hand
---

百川这轮公开面经很密：几乎每个模块都要报怎么做，以及数据量、检测率、使用量。数字说不清时，我会改口讲覆盖率、learning curve 和分母怎么定义，不会去编。

## 准备主线

1. **检索与改写**：例子库怎么分层采样；Query 改写为什么常用小模型；三路召回怎么融合。
2. **微调体系**：多模型微调是为了路由、蒸馏还是领域，有效数据规模有多大。
3. **表格 / SQL Agent**：可执行增广、AST 级安全检查，检测率和误拦率一起报。
4. **评估**：RAGAS 指标和数据从哪来；上线后 task success 和使用量怎么分 cohort 解读。
5. **多 Agent**：协作协议、共享状态和失败移交。不是多个 chatbot 并行就算协作。

## 本手册真题卡

点击下面每条即可跳到对应题。

- 百川：Agent 的例子库应怎样创建
- 百川：Query 改写用了什么模型，为什么不用大模型
- 百川：为什么要多模型做微调，数据量是多少
- 百川：表格 Agent 的数据怎样增强
- 百川：SQL Agent 如何做安全检查，检测率应怎样衡量
- 百川：Agent 上线后如何评估，使用量应怎样解读
- 百川：三路召回如何做
- 百川：RAGAS 评估指标、流程和数据如何获取
- 百川：多 Agent 如何协作
- 百川：如何提取复杂表格信息
- 百川：线上评估指标的数据如何构造
- 百川：不想训全量数据、只想按权重取样，在线怎么调
- 百川：超长文本外推常见怎么做，RoPE 你怎么理解
- 百川：讲一下 GRPO，以及和 PPO、DPO 的差别
- 百川：DeepSpeed 了解吗，怎么做
- 百川：FlashAttention 是什么，能提多少性能
- 百川：预训练有哪些并行方式
- 百川：了解搜索推荐吗，和 RAG / 改写怎么接
- 百川智能：求根号下的数，二分怎么写、边界怎么收？
- 百川智能二面：手写多头注意力时和 DeepSeek 练习卡差在哪？
- 百川智能：最早机器翻译的 Attention 和 Self-Attention 的 QKV 各从哪来？
