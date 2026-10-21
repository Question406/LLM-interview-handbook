---
id: dt-good-data-def
section: good-data
order: 2
level: S
title: 什么叫好数据？别用「高质量」三个字糊过去
quick: "好数据要针对明确的训练阶段和目标任务：加入后，固定评测中的目标能力改善，其他重要能力没有退步，而且来源、过滤器、教师版本和评测重叠情况都能追溯。分类器分高、像教科书或 token 多都只是信号，要靠下游对照来确认。"
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

我会把好数据定义成三个条件：针对明确的训练阶段和目标任务；加入后，固定评测里的目标能力变好、其他重要能力没有退步；结果能追溯到具体的数据版本。只说「高质量」，面试官仍然不知道你怎样选择和验证。

先讲阶段，是因为数据的价值取决于它用在哪里。同一篇文档，放进预训练网页数据和放进工具监督微调（SFT），作用可能完全不同，甚至一个有益、一个有害。Albalak 等的数据选择综述用效用函数来描述这种依赖关系。分类器分数高、写得像教科书或 token 多，都只是信号，要靠下游对照来确认。

## 怎么把定义落到实验

第一步是确定训练阶段。预训练网页、数学 continued PT、工具 SFT 轨迹，以及基于人类反馈的强化学习（RLHF）偏好对，各自需要不同的检查。比如 FineWeb-Edu 的教育分不能直接拿来过滤执行轨迹。mid / post-training 的合成数据要先验证再保留，预训练则还要保证覆盖。

第二步是定好目标切片和锚点。目标能力要提高，英语通用、安全及已有语言这些重要能力不能明显退步。只报告平均 loss 下降，可能只是模型更熟悉了主要的数据来源，见 `dt-data-mix-quota`。

第三步是做对照。DataComp-LM 固定模型和算力、只更换数据，再用下游评测比较。资源有限时，也可以用小模型做同预算对照。

最后保留复盘信息：URL 或文档 id、过滤器版本、教师版本，以及与固定评测的重叠。下周指标变化 $\Delta$ 如果对不上数据版本，就无法证明是哪批数据带来了效果，见 `dt-repro-lineage`。数据还要能合法用于训练，许可和隐私不合格的样本发布不了，见 `dt-license-is-quality`。

## 几个容易误判的信号

质量分高，可能只是分类器偏爱英语教科书。低资源语言的论坛答疑虽然有用，仍可能被打低分，见 `dt-quality-clf-synth`。

网页很干净，也可能是代码、公式和对话被滤掉了，结果代码和工具能力下降。AFM 2025 就提到，过强的启发式会丢掉有用的 token。

数据量大，还要看其中有多少 unique token。重复和近重复会白白消耗训练步数，见 `dt-repeat-epoch`、`dt-exact-dedup-code`。

内容像评测题，更要查污染。如果训练数据里出现了 GSM8K 题面，检查分数会很好看，却证明不了泛化，见 `dt-contamination`。

## 追问

- 还没有下游 $\Delta$，能先收集吗？可以先放进隔离区（quarantine）或开发池，暂不加入训练 mix。收集和用于训练是两个决定。
- 质量由人判断还是由模型判断？人制定协议、做抽查，模型负责扩大筛选的覆盖。人际一致性 $\kappa$ 反映协议是否清楚、标签是否可靠，见 `dt-kappa-code`。
