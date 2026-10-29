---
id: company-baichuan
section: companies
order: 15
level: A
title: 百川智能：大模型实习 / Agent 应重点准备什么？
quick: >-
  百川一轮会从例子库、Query 改写、三路召回、RAGAS、SQL 安全、表格 Agent 增强一路问到线上评估和使用量。我按「数据 → 检索 /
  Agent → 安全 → 线上指标」串起来准备，检测率和 adoption 都要能量化。
tags:
  - Baichuan
  - 真题导航
  - Agent
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 百川智能大模型实习一面 压力好大
    url: 'https://www.nowcoder.com/feed/main/detail/e3e6543bd5ab478292b74a48f031c530'
    type: candidate-first-hand
  - title: 百川智能大模型实习一面
    url: 'https://www.nowcoder.com/feed/main/detail/290832d2cd3242c386e56f27f975bce3'
    type: candidate-first-hand
---

百川这轮公开面经问得很密，几乎每个模块都要报怎么做，以及数据量、检测率、使用量是多少。数字说不清的时候，我会改讲覆盖率、learning curve 和分母怎么定义，不去编数。

比如讲到 SQL Agent 的安全检查，面试官多半会接着问检测率多少、误拦率多少，只说一句「做了 AST 检查」是过不了的。

## 准备主线

1. 检索和改写要讲清例子库怎么 stratified sampling、Query 改写为什么常用小模型、三路召回怎么融合。
2. 微调体系要说明多模型微调是为了路由、distillation 还是领域，有效数据规模有多大。
3. 表格 / SQL Agent 讲可执行增广和 AST 级安全检查，检测率和误拦率一起报。
4. 评估要说清 RAGAS 指标和数据从哪来；上线后看 task success，使用量按用户群体分别解读。
5. 多 Agent 讲协作协议、共享状态和失败移交。几个 chatbot 并行跑，还算不上协作。

## 本手册真题卡

下面每条点进去就能跳到对应题。

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
- 百川：了解搜索推荐吗，和 检索增强生成（RAG） / 改写怎么接
- 百川智能：求根号下的数，二分怎么写、bounds 怎么收？
- 百川智能二面：手写 multi-head attention 时和 DeepSeek 练习卡差在哪？
- 百川智能：最早机器翻译的 Attention 和 Self-Attention 的 QKV 各从哪来？
