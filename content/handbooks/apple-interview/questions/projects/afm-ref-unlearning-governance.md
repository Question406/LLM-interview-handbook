---
id: afm-ref-unlearning-governance
section: projects
order: 6
level: S
title: 个人 Reference 6：Unlearning，如何把 forget/retain 研究接到数据治理？
quick: 它让我更注意“看不到答案”和“已经删掉信息”之间的区别。数据撤回时，还要同时检查保留能力和后续是否再次混入同一来源。
companies:
  - apple
tags:
  - Apple
  - 个人研究 Reference
  - Jiabao Ji
  - AFM 2026-10-27
  - 口述版
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: Reversing the Forget-Retain Objectives — v1
    url: 'https://arxiv.org/html/2406.08607v1'
    type: primary
  - title: 'TOFU: A Task of Fictitious Unlearning for LLMs'
    url: 'https://arxiv.org/abs/2401.06121'
    type: primary
---

## 面试官可能这样问

你的 unlearning 研究和 Apple 关心的数据治理有什么联系？

## 可以这样回答

我觉得最直接的联系是，数据要撤回以后，我们怎么知道模型的行为真的改变了。在 unlearning 研究里，一个很容易产生误解的结果是：原来的问题答不出来了，但换一种问法，信息又出来了。

所以我会同时看忘记和保留两边。目标信息是否还能通过改写或间接问题取出来，其他正常能力有没有受到影响。只看原问题的准确率下降，我觉得证据还不够。

如果接到实际数据流程，我还会先检查数据来源和版本。模型这次做了 unlearning，但下一轮训练又把同一来源加回来，问题仍然存在。我的研究可以支持我讨论这些评价和权衡；它不能自动证明我处理过用户私有数据，也不能保证一种方法删除了所有可能提取的信息。

## 被追问时再展开

**那 unlearning 能替代数据许可吗？** 不能。允许不允许收集和训练，应当在前面决定。unlearning 是已经训练之后可能采用的一种补救办法，还需要验证。

## 技术备查

## 已核对的相关研究
[Reversing the Forget-Retain Objectives / ULD](https://arxiv.org/html/2406.08607v1) 是你参与的 unlearning 工作，包含 TOFU 实验。[TOFU](https://arxiv.org/abs/2401.06121) 用虚构人物资料定义 forget/retain，提供与未训练目标数据的参考行为比较。这是受控研究任务，不是实际用户隐私删除的认证。

## 可谈的治理 setting（建议扩展）
从许可合成 corpus 开始，对实体家族指定撤回集合；同时保存来源版本、训练 shard、改写派生和评测任务。比较原模型、仅 retain 重训参考及 unlearning 模型，在原问法、改写、间接线索和适当的再提取攻击上看忘记程度，并看相邻实体与通用任务效用。

先明确威胁模型：只要求不直接生成，还是限制给定攻击者的提取？输出下降可能来自拒绝行为，而非所有内部信息都消失。误删相邻事实、遗忘后再次 fine-tuning 恢复、数据后续重摄入都应作为研究问题。具体攻击和阈值依产品政策与能力选择，不声称有限测试证明信息论删除。

接到 AFM 时谈三层：摄入前的许可与用途限制；数据版本和撤回传播；已训练模型上的补救与验证。不能因为有 unlearning 方法就先收集不允许的数据，也不能把 PCC 推理保护、differential privacy 和权重遗忘说成一项机制。

## 英文60秒参考
> My unlearning research gives me a way to discuss governance through measurable forget–retain tradeoffs. I would distinguish suppressing an answer from demonstrating that information is no longer recoverable under a defined threat model. For a data pipeline, I would first preserve provenance and prevent withdrawn sources from re-entering later versions. Model-side unlearning would be one remediation option to evaluate, rather than a replacement for permission or a guarantee that every trace has been removed.

## 高频追问与回答方向
**只看 forget 准确率降到零够吗？** 不够，要测改写、提取以及 retain 效用，并与合理参考对照。
**有真实用户数据经验吗？** 按实际经历回答；这条 reference 基于受控研究，不暗示做过 Apple 用户数据处理。
**DP 能直接代替 unlearning？** 两者目标与保证不同，需分别说明邻居关系、预算和撤回威胁模型。

继续练 `dt-privacy-feedback`、`dt-repro-lineage`、`dt-legal-capability`。

