---
id: xai-grok-pretrain
section: xai
order: 11
level: S
title: xAI：Grok 预训练公开口径能讲什么，不要编数据配比
quick: "Grok-1 的公开权重和架构可核对：314B、8 专家每 token 用 2 个，JAX / Rust 从零训练，是未做对话微调的基座。公开数据描述只到「大量文本」；Grok-3 的算力、后训练和评测说法单独引用，不能反推出预训练配比。"
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

讲 Grok 预训练时，先用 Grok-1 开源快照说明已知架构和训练栈，再把未知数据配比与通用工程判断分开。Grok-3 的 RL、上下文和榜单属于另一组公开说法，不能回填成 Grok-1 的训练配方。

这道卡根据 2024 年 3 月开源的 Grok-1 权重与架构、Grok-3 博文对 Colossus 和推理后训练的介绍，以及 Series C 的集群数字整理，`realInterview: false`。闭源后续代际没有同等数据卡，不能补写未披露的配比。集群故障和 ckpt 见 `xai-colossus`，MoE 结构见 `xai-grok-moe`。

Grok-1 的开源博文与 GitHub 给出了这些可核对事实：

- 规模。314B 总参、Mixture of 8 Experts、每个 token 用 2 个，约 25% 权重激活。
- 层与注意力。64 层；Q 48 头、KV 8 头（GQA）；$d=6144$；RoPE；上下文 8192。
- 词表。SentencePiece，131072。
- 栈。从零训，自定义栈在 JAX 和 Rust 上。预训练阶段 2023 年 10 月结束。
- 官方写明 Grok-1 是预训练基座，没有为对话微调，因此它在 HumanEval 上的表现或输出不能直接代表 Grok 聊天产品。

官方的数据描述是 trained on a large amount of text data，没有给出代码或 X 公开帖占比，也没有给出 Chinchilla 配比结论。因此「大概 30% 代码」这样的数字不能补上。如果继续讨论如何设计，可以谈过滤、去重、质量分类器和合规剥离，但要标明这是通用预训练做法。

架构上可以继续解释 8 专家 $k=2$、GQA 的 KV 头和 MoE 替换 FFN，这些都有开源结构依据。co-occurrence 统计和领域配比课程没有对应披露，需要保留未知。

Grok-3 在 2025 年 2 月博文里的说法，应按对应版本单独读：

- 算力。写在 Colossus 上训，号称约 10 倍于此前他们口中的 SOTA 训练计算。这是公司博文，不是你复现过的 FLOPs 账。集群就绪时间、Hopper 量级见 `xai-colossus`。不要把 10 倍换算成 token 数。
- 推理后训练。Think 变体用大规模 强化学习（RL） 修思维链、回退、验算。这是预训练之后的轴。SimpleQA / AIME / GPQA 数字是博文表格，面试引用要带「官方自报、切片和提示未知」。
- 上下文。声称 1M window；LOFT 128k 作为长上下文 检索增强生成（RAG） 基准。实现（YaRN、分段、检索）没有公开，不要编位置编码配方。
- Arena。早期版本代号 chocolate，博文写过 Chatbot Arena Elo 1402。这是在线偏好快照，不是预训练质量。怎么读 Elo 见 `xai-lmarena`。

产品侧还提到 DeepSearch（搜网 + 代码解释器）。那是工具循环，更不是预训练配比。

Grok-3 的 AIME 分数不能证明预训练见过哪些竞赛题，X 实时搜索也只能说明推理期有这个工具，官方没有给训练语料里的 X% 配比。Dojo 和 Colossus 也需要分别讨论。

如果要继续展开设计，可以按目标、模型、数据、优化和验收逐项讲，并把公开事实与通用判断分开：

1. 目标：下一个 token；Grok-1 是基座，助手行为是后训练的事。
2. 模型：开源图上的 MoE + GQA，闭源代际只说更大 / 更长，不编专家数。
3. 数据：未知配比。能问的工程问题是去重、泄漏、安全过滤、多语言——问他们怎么评，别假装见过 mixer 配置。
4. 优化：公开没写 batch、学习率、token 预算。可以说 Adam / μP / 稳定性是通用话题，不要报假超参。
5. 验收：公开榜会脏，见 `xai-lmarena`；预训练更信持有时间切片的内部集，但那是他们的，不是你的。

这样可以说明哪些训练判断能够迁移，同时保留数据与超参尚未公开的边界。

## 追问

**Grok-1 的 25% 激活是稀疏训练还是只稀疏推理？**
开源描述是每 token 2/8 专家，训练和推理都是条件计算。具体 aux 损失（loss）、capacity factor 仓库示例不是高效实现，不要当成生产超参。
**为什么开基座不开数据？**
权重证明架构可复现；数据有版权和安全约束。面试不要把「开源模型」说成「开源配方」。
**实时 X 数据算预训练吗？**
公开产品讲的是推理时搜 X / 网页。训练是否用公开帖、如何授权，以当时隐私政策和博文为准，缺数字就说缺。
**和 Colossus 的 10 万卡怎么接？**
那是能放下更长训、更多故障的硬件故事，见 `xai-colossus`。卡多不等于你知道数据配比。
