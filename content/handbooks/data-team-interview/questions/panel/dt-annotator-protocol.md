---
id: dt-annotator-protocol
section: panel
order: 11
level: A
title: Panel：人标协议怎么写，一致率低怎么办？
quick: "先写协议再开标，每个维度写清定义、正例、反例和不允许的判断捷径，再让两人独立标、算一致率。一致率低先查原因，是协议含糊、题本身不可比还是有长度捷径，查清了再决定要不要加人。AFM 报告里 20-30% 的偏好对人与人之间不同意，他们用 cohesion 挑更容易达成一致的 prompt。"
companies:
  - apple
tags:
  - Apple
  - Annotation
  - Preference
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: "Direct Preference Optimization"
    url: https://arxiv.org/abs/2305.18290
    type: primary
---

先写协议再开标；一致率低的时候先查分歧从哪来，查清楚了再决定要不要加人。主观题一致率低，往往说明题目或协议本身有问题。

举个例子，只给标注员一句「选更好的摘要」就开标，有人看忠实，有人看长度，有人看有没有剧透，每个人心里的「好」都不一样。换一批人重标，同样的分歧还会出现，只是多花了一份钱。协议不清楚，加人手也拿不到可靠的标签。这种分歧很常见，AFM 报告随机抽偏好对，人与人在 20-30% 上不同意，这些题通常主观、难或含糊。

## 协议怎么写

我会先把「好不好」拆成能单独判断的维度。摘要至少拆成忠实、剧透、长度三项。工具轨迹要逐步看：参数合不合法、状态对不对、最后给用户的回答准不准，只看最终状态会漏掉中间步骤的错。常见的判断捷径也写进协议、明文禁止，比如永远选更长的、永远选更客气的。

接着定双标比例，安全和高价值领域双标多一些，大批量的普通数据少一些。一致率同时报简单一致率和 Cohen's $\kappa$：如果大家都倾向选 A，简单一致率会被撑高，$\kappa$ 能把这部分扣掉。最后冻结一份金标集，用来校准新标注员和 LLM judge。

## 一致率低时先分原因

最常见的是协议含糊，那就改协议、补例子，再标一小批看一致率有没有回升。如果两个回答本身没法放在一起比，就丢掉或者改成绝对分，硬做 pairwise 会把噪声写进直接偏好优化（DPO）或奖励模型（RM）。如果标注员在偏好长回答，就分层抽样或做长度归一后再比。多语题让母语者标自己的母语，翻译过来的题人评会有偏差，AFM 也不用翻译题当多语门禁。

## 追问

**三人投票破平行不行？**
可以，但还要报三个人里有没有系统性偏长。多数票本身也可能错。

**专家和众包怎么分工？**
专家定协议和金标，众包负责扩量。专家之间都对不上时，先停下扩量。

**模型预标、人再改，算不算人标？**
算过程监督，AFM 的工具标注平台就是这么做的。要能回滚，预标的错误率写进 dataset card。

**AFM 那个 cohesion 头是做什么的？**
在相近的问题里挑标注员更容易达成一致的 prompt，拿去做强化学习（RL）。这一步是在挑数据，标注员的判断照样各自独立。

相关：`dt-human-budget`（人标预算怎么花）、`dt-judge-bias`、`dt-length-hack-data`
