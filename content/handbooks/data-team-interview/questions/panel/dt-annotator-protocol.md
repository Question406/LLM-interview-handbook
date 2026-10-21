---
id: dt-annotator-protocol
section: panel
order: 11
level: A
title: Panel：人标协议怎么写，一致率低怎么办？
quick: "先写协议再开标：每个评价维度写清定义、正例、反例和不允许的判断捷径，再让两人独立标注、算一致率。一致率低时先查原因：协议含糊、题本身不可比，还是有长度捷径，查清了再决定要不要加人。AFM 报告里 20-30% 的偏好对人与人之间不同意，他们用 cohesion 挑更容易达成一致的 prompt。"
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

我会先写协议再开标。每个维度写定义、正例、反例和不允许的捷径。主观题一致率低，往往说明题目或协议有问题，所以先查分歧的原因，再决定要不要加标注员。

## 为什么协议要先于标注

如果只给一句「选更好的」就开始标，每个人心里的「好」都不一样。换一批人重标，还会出现同样的分歧，只是多花了一份钱。协议不清楚时，加人手也很难得到可靠标签。

分歧有多常见，AFM 报告给过一个数：随机抽偏好对，人与人在 20-30% 上不同意，这些题通常主观、难或含糊。他们另训了一个 cohesion 头，在相近的问题里挑标注员更容易达成一致的 prompt，用于强化学习（RL）。这一步是在挑数据，标注员的判断照样各自独立。

## 协议怎么写

先把「好不好」拆成能单独判断的维度。比如摘要至少拆成忠实、剧透、长度三项。工具轨迹要逐步检查：参数是否合法、状态是否正确、最终给用户的回答是否准确，只看最后的状态会漏掉中间步骤的错误。常见的判断捷径也要明文禁止，例如永远选更长的、永远选更客气的。

然后决定双标比例。安全和高价值领域双标比例高一些，大批量的普通数据低一些。一致率同时报简单一致率和 Cohen's $\kappa$，因为如果大家都倾向选 A，简单一致率会被撑高，$\kappa$ 能扣掉这部分。最后冻结一份金标集，用来校准新标注员和 LLM judge，见 `dt-judge-bias`。

## 一致率低时先分原因

- **协议含糊**：改协议、补例子，再标一小批看一致率有没有回升。
- **题本身不可比**：两个回答没法放在一起比，就丢掉或改成绝对分。硬做 pairwise 会把噪声写进直接偏好优化（DPO）或奖励模型（RM）。
- **长度捷径**：标注员在偏好长回答，就分层抽样或做长度归一后再比，见 `dt-length-hack-data`。
- **locale**：让母语者标自己的母语。翻译过来的题人评会有偏差，AFM 也不用翻译题当多语门禁。

## 追问

- **三人投票破平行不行？** 可以，但仍要报三人里有没有系统性偏长。多数票本身也可能错。
- **专家和众包怎么分工？** 专家定协议和金标，众包负责扩量。专家之间都不一致时，先停下扩量。
- **模型预标、人再修改，算不算人标？** 算过程监督，AFM 的工具标注平台就是这样做的。要能回滚，预标错误率要写进 dataset card。

相关：人标预算怎么花见 `dt-human-budget`。
