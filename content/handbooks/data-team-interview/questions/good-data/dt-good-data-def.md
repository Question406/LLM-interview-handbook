---
id: dt-good-data-def
section: good-data
order: 2
level: S
title: 什么叫好数据？别用「高质量」三个字糊过去
quick: "好数据要对准一个训练阶段和目标任务：加进去以后，固定评测里的目标能力变好，其他重要能力不退步，来源、过滤器、教师版本和评测重叠都查得到。分类器分高、像教科书、token 多都只是信号，要靠下游对照确认。"
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

我会用三个条件来定义好数据：对准一个明确的训练阶段和目标任务；加进去以后，固定评测里的目标能力变好，其他重要能力没退步；结果能追溯到具体的数据版本。光说「高质量」，面试官还是不知道你怎么选、怎么验证。

先说阶段，因为一条数据值多少，取决于它用在哪里。同一篇文档，放进预训练网页数据和放进工具监督微调（SFT），作用可能完全不同，甚至一个有益、一个有害。FineWeb-Edu 的教育分就不能直接拿来过滤执行轨迹。Albalak 等的数据选择综述用效用函数来描述这种依赖。阶段定了，检查也就跟着定了：预训练网页、数学 continued PT、工具 SFT 轨迹、基于人类反馈的强化学习（RLHF）偏好对，各有各的检查；mid / post-training 的合成数据要先验证再保留，预训练还要保证覆盖。

接着定目标切片和锚点。目标能力要提高，英语通用、安全和已有语言这些重要能力不能明显退步。只报平均 loss 下降，可能只是模型更熟悉主要的数据来源了，见 `dt-data-mix-quota`。

然后做对照。DataComp-LM 的做法是固定模型和算力、只换数据，再比下游评测；资源有限时，用小模型做同预算对照也能提供证据。

最后把复盘需要的信息留好：URL 或文档 id、过滤器版本、教师版本，以及和固定评测的重叠。下周指标变化 $\Delta$ 对不上数据版本，就说不清是哪批数据带来了效果，见 `dt-repro-lineage`。数据还得能合法用于训练，许可和隐私不合格的样本发布不了，见 `dt-license-is-quality`。

## 容易看走眼的信号

分类器分数高、写得像教科书、token 多，这些都只是信号。质量分高，可能只是分类器偏爱英语教科书，低资源语言里有用的论坛答疑照样会被打低分，见 `dt-quality-clf-synth`。网页看着很干净，也可能是代码、公式和对话被滤掉了，结果代码和工具能力跟着掉。AFM 2025 就提到，过强的启发式会丢掉有用的 token。

## 追问

**还没有下游 $\Delta$，能先把数据收进来吗？**
可以。先放进隔离区（quarantine）或开发池，暂时不加进训练 mix。收集和用于训练是两个决定。

**质量由人判断还是由模型判断？**
人制定协议、做抽查，模型负责扩大筛选的覆盖。人际一致性 $\kappa$ 能反映协议写得清不清楚、标签可不可靠，见 `dt-kappa-code`。

**数据量大，算不算好？**
先看里面有多少 unique token。重复和近重复会白白消耗训练步数，见 `dt-repeat-epoch`、`dt-exact-dedup-code`。

**内容很像评测题，是不是更有用？**
先查污染。训练数据里出现了 GSM8K 题面，检查分数会很好看，却证明不了泛化，见 `dt-contamination`。
