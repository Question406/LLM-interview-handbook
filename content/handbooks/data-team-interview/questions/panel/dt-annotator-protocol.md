---
id: dt-annotator-protocol
section: panel
order: 11
level: A
title: Panel：人标协议怎么写，一致率低怎么办？
quick: "先写清每个评价维度的定义、正反例和不能使用的判断捷径，再让两人独立标注，计算一致率。AFM 发现偏好题中有 20-30% 存在人评分歧，并用 cohesion 选择更容易达成一致的 prompt。分歧要先找原因，不能只靠增加标注员。"
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

我会先写协议再开标。每一维写定义、正例、反例、不允许的捷径。主观题一致率低，可能说明题目或协议有问题。先查分歧的原因，再决定是否需要增加标注员。

只发一句「选更好的」就开始标注，标准太含糊。后面换一批人重标，也可能出现同样的分歧，还会增加成本。

## 协议要比模型先存在

摘要至少拆忠实 / 剧透 / 长度，不要一个「好不好」。工具轨迹逐步检查参数是否合法、状态是否正确，以及最终对用户的回答是否准确，不能只看最后的状态。不允许的捷径写进协议：永远选长的、永远选更客气的。

双标比例按严重度：安全和高价值域高一些，bulk 低一些。同意率用简单一致率和 Cohen's $\kappa$，避免「全选 A」把一致率撑高。金标集要冻结，用来校准新标注员和 LLM judge，见 `dt-judge-bias`。

AFM：随机抽偏好对，人在 20-30% 上不同意，题通常主观、难、含糊。他们另训 cohesion 头，选择相近问题中标注员更容易达成一致的 prompt，用于强化学习（RL）。这是在选择数据，不是强迫所有标注员给相同答案。

一致率低时，先区分原因：

- 协议含糊。改协议、加例子，再标一小批。
- 题本身不可比。丢掉或改成绝对分。硬做 pairwise 会把噪声写进 直接偏好优化（DPO） / 奖励模型（RM）。
- 长度捷径。分层抽样或长度归一后再比，见 `dt-length-hack-data`。
- locale。母语者标母语。翻译题的人评会偏，AFM 不用翻译题当多语门禁。

人标预算怎么花见 `dt-human-budget`。协议不清楚时，增加人手也很难得到可靠标签。

## 追问

- **三人投票破平？** 可以。仍要报「三人里有没有系统性偏长」。多数票不是 oracle。
- **专家和众包差在哪？** 专家定协议和金标；众包扩量。专家不一致时先停扩量。
- **模型预标再人改，算不算人标？** 算过程监督，AFM 工具平台就是。要能回滚，预标错误率进 dataset card。
