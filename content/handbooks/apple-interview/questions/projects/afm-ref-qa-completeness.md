---
id: afm-ref-qa-completeness
section: projects
order: 1
level: S
title: 个人 Reference 1：DeepAmbigQA，如何把“漏答”变成 synthetic data 问题？
quick: 我会讲 DeepAmbigQA：一个答案每句话都对，也可能漏掉另一种合理解释。这个问题让我更关注答案覆盖了什么，而不只是它有没有说错。
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
  - title: DeepAmbigQA — public paper v1
    url: 'https://arxiv.org/html/2511.01323v1'
    type: primary
  - title: Jiabao Ji — public CV
    url: 'https://question406.github.io/assets/cv/cv.pdf'
    type: primary
  - title: AmbigQA — EMNLP 2020
    url: 'https://aclanthology.org/2020.emnlp-main.466/'
    type: primary
  - title: 'ASQA: Factoid Questions Meet Long-Form Answers'
    url: 'https://arxiv.org/abs/2204.06092'
    type: primary
  - title: 'MuSiQue: Multihop Questions via Single-hop Question Composition'
    url: 'https://arxiv.org/abs/2108.00573'
    type: primary
---

## 面试官可能这样问

你的研究里，有什么例子能说明你会怎么做 synthetic data 和评测？

## 可以这样回答

我会讲 DeepAmbigQA。这项工作里有一个很直观的问题：有些问题里的名字对应不止一个实体，模型可能只选了其中一个，然后给出一个完全正确、但不完整的答案。只检查它说出来的内容，很容易漏掉这种失败。

我们在这篇工作里研究了这类歧义和多跳问题。对这个岗位来说，我觉得有价值的是把“答案不够全”变成可以检查的数据问题：有哪些解释、每个解释需要找什么证据、最后应该包含哪些答案。这样比只让一个 judge 给整体印象分，更容易看清缺口。

如果继续往训练上做，我会先检查模型是没发现另一种解释，还是发现了却没找到证据。前者补消歧和分支探索的例子，后者补检索或证据整合。这个训练扩展是我的方案；论文里的 benchmark 工作，以及我本人负责的部分，需要分别讲清楚。

## 被追问时再展开

**面试官问你具体做了什么？** 回到你实际负责的数据生成、质量检查或实验模块，选一个真实决定讲清原因。公开作者名单无法替你补这一段。

## 技术备查

## 已核对的相关研究
[DeepAmbigQA](https://arxiv.org/html/2511.01323v1) 将 corpus 与知识图谱相连，构造可执行的复杂问答；公开数据为3600题。它直接支持你讨论答案完整性。你的 CV 把 Apple 实习主题写为 ambiguity-aware QA synthesis，但不能据此推断你负责了所有环节。

## 相关 benchmark 怎么区分
| 材料 | 要理解的 setting | 面试中的用途 |
| --- | --- | --- |
| [AmbigQA](https://aclanthology.org/2020.emnlp-main.466/) | 找出多种合理解释及对应答案，重写问题以消歧 | 说明歧义不是单一实体预测 |
| [ASQA](https://arxiv.org/abs/2204.06092) | 长答案应覆盖歧义问题的不同解释 | 区分文风流畅与事实覆盖 |
| [MuSiQue](https://arxiv.org/abs/2108.00573) | 组合具有依赖关系的单跳问题，减少多跳捷径 | 讨论真正用到中间证据 |

这是外部对照阅读，不表示你亲自复现过全部基准。

## 可以和面试官讨论的具体 setting（建议扩展）
构造一个许可知识库：同名的两个“Atlas”组织，每个关联不同奖项和年份。问“哪些 Atlas 相关作品在给定年限获奖？”在冻结快照内，保存解释分支、执行计划、实体 ID、全部答案和证据。例子是教学设计。

先做歧义有/无×单跳/多跳的2×2评测，再按答案集合大小 evaluation slices。报告实体级 precision/recall、集合 exact match、解释分支覆盖和证据支持；这些是建议指标，不能全部称为论文原指标。准确但漏答与胡乱多列答案要分开惩罚。

诊断依次给 oracle 解释、oracle 检索证据、oracle 中间结果，看哪个替换能恢复答案。干预分别补消歧、遗漏分支、跨证据集合操作和有依据的停止。按实体家族、模板/图结构及来源隔离开发和验收，别把题面改写当独立测试。KB 执行正确只保证快照内一致，还需抽查自然语言和外部事实。

## 英文60秒参考
> In DeepAmbigQA, we studied answer completeness in ambiguous multi-hop questions. The useful connection to data work is that a fluent answer can still omit valid interpretations. For a follow-up training setting, I would keep a structured answer set and supporting evidence, then separate ambiguity failures from retrieval and aggregation failures. I would first use oracle substitutions to identify the bottleneck, and only then generate targeted training examples. That extension is a proposal, rather than a training result I would claim from the benchmark paper.

## 高频追问与回答方向
**为什么不是把 search top-k 加大？** 更多证据不保证覆盖正确分支，也可能增加噪声；做预算受控的检索与聚合对照。
**合成答案真的全吗？** 只在定义的快照和查询域内保证，不能把知识库缺失误作现实中不存在。
**如何接 RM/bias？** 构造同样正确但覆盖不同的候选，分开标完整性、事实和冗长；一般 judge 可能奖励长而不全。独立实体集合检查不能由同一生成器自证。
**能讲 See Around Corners 吗？** 研究发现指标盲点可作线索；事前发现、推动行动与结果必须补真实时间线。

继续练 `dt-synth-reasoning`、`dt-benchmark-gap` 和 `afm-rm-length-causal-audit`。

