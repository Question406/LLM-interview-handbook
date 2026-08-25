---
id: xai-grok-pretrain
section: xai
order: 11
level: S
title: xAI：Grok 预训练公开口径能讲什么，不要编数据配比
quick: >-
  能钉死的只有 Grok-1 开源快照：314B、8 专家、每 token 2 个、约 25% 权重、JAX 加 Rust 从零训、预训练停在 2023 年
  10 月、Apache 2.0、不是对话微调。数据只写「大量文本」。Grok-3 博文给的是 Colossus 算力、RL
  推理和 Arena 分数，不是配比表。编 web/code/X 比例是减分。
tags:
  - xAI
  - Grok
  - Pretraining
  - Public Claims
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Open Release of Grok-1
    url: https://x.ai/news/grok-os
    type: primary
  - title: xai-org/grok-1
    url: https://github.com/xai-org/grok-1
    type: primary
  - title: Grok 3 Beta — The Age of Reasoning Agents
    url: https://x.ai/blog/grok-3
    type: primary
  - title: xAI Series C (6 billion USD)
    url: https://x.ai/blog/series-c
    type: primary
---

## 题怎么来的

xAI 研究 / 预训练岗会开口问 Grok 怎么训。评委要听你 **分得清公开事实和猜测**，不是要一份假的数据配比。能核对的锚点很少：2024 年 3 月开源的 Grok-1 权重和架构、Grok-3 博文里对 Colossus 和推理后训练的描述、Series C 对集群规模的公开数字。后面闭源代际没有同等数据卡。`realInterview: false`。集群故障和 ckpt 见 `xai-colossus`；MoE 结构见 `xai-grok-moe`。本题不写 Tesla 数据引擎。

## Grok-1：唯一能逐项钉死的预训练快照

开源博文和 GitHub 规格，我会当「可引用」而不是「内部 runbook」：

- **规模。** 314B 总参、Mixture of 8 Experts、每 token 用 2 个，约 25% 权重激活。
- **层与注意力。** 64 层；Q 48 头、KV 8 头（GQA）；$d=6144$；RoPE；上下文 8192。
- **词表。** SentencePiece，131072。
- **栈。** 从零训，自定义栈在 JAX 和 Rust 上。预训练阶段 **2023 年 10 月结束**。
- **不是助手。** 官方写明：这是预训练基座，没有为对话微调。把 Grok-1 的 HumanEval 口吻当成 Grok 聊天产品，是张冠李戴。

数据句官方只有一句：**trained on a large amount of text data**。面试到此停。不要补「大概 30% 代码、X 上公开帖占多少、是否走 Chinchilla 最优」。那些数字公开材料没有。评委追「那你觉得呢」，我会改口成 **一般预训练会做的事**（过滤、去重、质量分类器、合规剥离），并标明这是业界做法，不是 xAI 配方。

架构题可以讲深：为什么 8 专家 $k=2$、GQA 的 KV 头、MoE 层替换 FFN。那是开源图里有的。一滑到「 co-occurrence 统计 / 领域配比课程」，就没有出处了。

## Grok-3 博文：算力、后训练、评测，不是数据卡

Grok-3（2025 年 2 月）公开口径是另一张表，不要回填到 Grok-1 预训练：

- **算力。** 写在 Colossus 上训，号称约 10 倍于此前他们口中的 SOTA 训练计算。这是公司博文，不是你复现过的 FLOPs 账。集群就绪时间、Hopper 量级见 `xai-colossus`。不要把 10 倍换算成 token 数。
- **推理后训练。** Think 变体用大规模 RL 修思维链、回退、验算。这是 **预训练之后** 的轴。SimpleQA / AIME / GPQA 数字是博文表格，面试引用要带「官方自报、切片和提示未知」。
- **上下文。** 声称 1M window；LOFT 128k 作为长上下文 RAG 基准。实现（YaRN、分段、检索）没有公开，不要编位置编码配方。
- **Arena。** 早期版本代号 chocolate，博文写过 Chatbot Arena Elo 1402。这是在线偏好快照，不是预训练质量。怎么读 Elo 见 `xai-lmarena`，不要神化。

产品侧还提到 DeepSearch（搜网 + 代码解释器）。那是工具循环，更不是预训练配比。

错法：用 Grok-3 的 AIME 反推预训练见过竞赛题；把 X 实时搜索说成「所以预训练主要是推文」——搜索是推理期工具，官方没把训练语料拆成 X%。把 Dojo 和 Colossus 混成一个集群。

## 面试怎么讲「我不知道配比」而不显得空

我会主动给一个 **可证伪的预训练清单**，每条只写公开或标明推断：

1. 目标：下一个 token；Grok-1 是基座，助手行为是后训练的事。
2. 模型：开源图上的 MoE + GQA，闭源代际只说更大 / 更长，不编专家数。
3. 数据：未知配比。能问的工程问题是去重、泄漏、安全过滤、多语言——问他们怎么评，而不是假装你见过 mixer 配置。
4. 优化：公开没写 batch、学习率、token 预算。可以说 Adam / μP / 稳定性是通用话题，不要报假超参。
5. 验收：公开榜会脏，见 `xai-lmarena`；预训练更信持有时间切片的内部集，但那是他们的，不是你的。

这样评委听到的是诚实的边界，加上能迁移的训练判断，而不是一篇伪造的 Grok 数据论文。

## 追问

- **Grok-1 的 25% 激活是稀疏训练还是只稀疏推理？** 开源描述是每 token 2/8 专家，训练和推理都是条件计算。具体 aux loss、capacity factor 仓库示例不是高效实现，不要当成生产超参。
- **为什么开基座不开数据？** 权重证明架构可复现；数据有版权和安全约束。面试不要把「开源模型」说成「开源配方」。
- **实时 X 数据算预训练吗？** 公开产品讲的是推理时搜 X / 网页。训练是否用公开帖、如何授权，以当时隐私政策和博文为准，缺数字就说缺。
- **和 Colossus 的 10 万卡怎么接？** 那是能放下更长训、更多故障的硬件故事，见 `xai-colossus`。卡多不等于你知道数据配比。
