---
id: dt-good-data-def
section: good-data
order: 2
level: S
title: 什么叫好数据？别用「高质量」三个字糊过去
quick: "好数据要针对明确的训练阶段和目标任务：加入后，固定评测中的目标能力改善，其他重要能力没有退步，而且来源、过滤器、教师版本和评测重叠情况都能追溯。分类器分高、像教科书或 token 多，都不能单独证明它好。"
companies:
  - apple
tags:
  - Apple
  - Data Quality
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: DataComp-LM
    url: https://arxiv.org/abs/2406.11794
    type: primary
  - title: A Survey on Data Selection for Language Models
    url: https://arxiv.org/abs/2402.16827
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

判断数据是否好，先回答三个问题：用在哪个训练阶段，要改善哪类任务，以及结果能否追溯到具体版本。只说「高质量」，面试官仍不知道你如何选择和验证。

同一篇文档，对预训练网页数据和工具监督微调（SFT）的作用可能完全不同，甚至一个有益、一个有害。Albalak 等的数据选择综述用效用函数描述这种依赖关系。分类器分数高、写得像教科书或 token 多，都只是信号，不能直接当成定义。

## 怎么把定义落到实验

先确定训练阶段。预训练网页、数学 continued PT、工具 SFT 轨迹，以及基于人类反馈的强化学习（RLHF）偏好对，各自需要不同检查。FineWeb-Edu 的教育分不能直接用来过滤执行轨迹。AFM 的 mid / post-training 合成数据强调先验证再保留；预训练还需要保证覆盖。

再确定目标切片和锚点。目标能力要提高，英语通用、安全及已有 locale 等重要能力不能明显退步。只报告平均 loss 下降，可能只是模型更熟悉主数据来源，见 `dt-data-mix-quota`。

最后保留复盘信息：URL 或文档 id、过滤器版本、教师版本，以及与固定评测的重叠。下周指标变化 $\Delta$ 如果对应不上数据版本，就无法证明是哪批数据带来的效果，见 `dt-repro-lineage`。

DataComp-LM 固定模型和算力，只更换数据，再用下游评测比较。资源有限时，也可以用小模型做同预算对照。

## 几个容易误判的信号

质量分高，可能只是分类器偏爱英语教科书。低资源语言的论坛答疑虽然有用，仍可能被打低分，见 `dt-quality-clf-synth`。

网页很干净，也可能是代码、公式和对话被滤掉了，导致代码和工具能力下降。AFM 2025 提到，过强启发式会丢弃有用 token。

数据量大，也要看其中有多少 unique token。重复和近重复会消耗训练步数，见 `dt-repeat-epoch`、`dt-exact-dedup-code`。

内容像评测题，更要查污染。如果训练里出现 GSM8K 题面，检查分数可能很好看，却不能证明泛化，见 `dt-contamination`。

在苹果场景中，还要确认许可与隐私条件。公开方向是许可语料、公开页面和经过验证的合成数据；用户交互默认不进入基础模型，见 `dt-license-is-quality`。

## 追问

- 没有下游 $\Delta$，能先收集吗？可以进入隔离区（quarantine）或开发池，先不要加入训练 mix。收集和用于训练是两个决定。
- 人和模型谁判断质量？人制定协议、做抽查，模型扩大筛选覆盖。人际一致性 $\kappa$ 反映协议是否清楚、标签是否可靠，见 `dt-kappa-code`。
- 苹果场景还要检查什么？除效果和可追溯性外，还要通过许可、隐私检查。不能把用户交互默认当成基础模型训练来源，见 `dt-license-is-quality`。
