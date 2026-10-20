---
id: dt-judge-bias
section: panel
order: 16
level: A
title: Panel：LLM-as-judge 会偏什么，什么时候能用？
quick: "LLM judge 适合快速开发检查，但要先与人评校准。它可能偏爱长答案、同家族文风、先出现的候选和礼貌套话。按长度分层、交换候选顺序，并保留独立人评；可执行任务用规则验证，不让 judge 替代 oracle。"
companies:
  - apple
tags:
  - Apple
  - LLM Judge
  - Evaluation
  - Bias
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "AlpacaEval 2.0"
    url: https://arxiv.org/abs/2404.04475
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: "LLM-as-a-Judge (Zheng et al.)"
    url: https://arxiv.org/abs/2306.05685
    type: primary
---

LLM judge 可以加快开发集回归，但不能未经验证就用它的赢率决定发布。先与人工参考标签计算一致率；一致率低时，检查协议和提示是否含糊，增加采样温度不能解决标准不清楚。

不这么选的理由：AFM 多语 hill-climb 用过 GPT-4o 当 AlpacaEval / IFEval 的 judge，并写了要和人评对齐。生成器、合成题、judge 不能来自同一系。可执行任务不要用 judge 替代 oracle。

## 已知偏置，现场主动报

长度偏差：长答案更容易赢，所以对照要按长度分层，见 `dt-length-hack-data`。

自偏好。同家族模型给自己高分。学生若从该教师蒸馏，judge 会表扬教师腔。

位置偏差：成对比较中，候选的左右或先后顺序会影响结果。交换顺序或随机排列。

表面礼貌也可能被过度奖励，与奖励模型（RM）的 hack 风险类似。

用法：开发集快速回归，和人评金标算同意率。同意率低就当 `dt-annotator-protocol` 里协议含糊的那个分支，不要加 judge 温度。AFM 调整 judge 的 prompt，使自动判断与人评对齐，再加速迭代。门禁仍是人评和 locale。

可执行任务不要用 judge 替代 oracle。代码、数学、工具状态走规则，见 `dt-reward-pref`。

## 追问

- **多个 judge 投票？** 能压单点噪声，压不住共有的长度偏置。
- **能不能用 judge 造偏好对？** 可以当候选，人抽查或 cohesion 过滤后再进 直接偏好优化（DPO）。UltraFeedback 一类公开集也是这条，生产要再校准。
- **IFEval 算 judge 吗？** 不算。它是可验证的指令约束，更像规则奖励。适合格式回归，不替代人评。
