---
id: dt-judge-bias
section: panel
order: 16
level: A
title: Panel：LLM-as-judge 会偏什么，什么时候能用？
quick: "LLM judge 适合开发集的快速回归，和人评金标校准过才能拿它的赢率做参考，发布仍看人评。它会偏爱长答案、同家族文风、先出现的候选和礼貌套话，所以要按长度分层、交换候选顺序、保留独立人评。可执行任务用规则验证，judge 替代不了 oracle。"
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

LLM judge 可以拿来加快开发集回归，但用它的赢率之前，要先和人工参考标签算一致率；发布门禁还是人评。一致率低时去查协议和提示是不是含糊，调高 judge 的采样温度解决不了标准不清楚的问题。

举个例子，学生模型是从某个教师蒸馏出来的，又拿同一家族的模型当 judge，judge 会给教师的文风打高分，看起来赢率涨了，其实只是文风像。这就是自偏好，所以生成器、合成题和 judge 要来自不同系。

judge 还有几种已知的偏置，面试里要主动报出来。长答案更容易赢，对照要按长度分层（`dt-length-hack-data`）。成对比较时，候选的左右或先后顺序会影响结果，交换顺序或随机排列就能压住。礼貌套话也可能被过度奖励，这和奖励模型（RM）被 hack 的风险类似。

用法上，我会把 judge 放在开发集的快速回归上，并和人评金标算同意率。同意率低，就按 `dt-annotator-protocol` 里协议含糊的那条路处理，改协议和提示。AFM 在多语 hill-climb 时用过 GPT-4o 当 AlpacaEval / IFEval 的 judge，也是先调 judge 的 prompt，让自动判断和人评对上，再用它加速迭代，门禁仍是人评和 locale。代码、数学、工具状态这类可执行的任务直接走规则检查，规则就是 oracle（`dt-reward-pref`）。

## 追问

**多个 judge 投票行不行？**
能压住单个 judge 的噪声，压不住它们共有的长度偏置。

**能不能用 judge 造偏好对？**
可以当候选，经过人工抽查或 cohesion 过滤后再进直接偏好优化（DPO）。UltraFeedback 一类公开集也走这条路，生产上要再校准。

**IFEval 算 judge 吗？**
不算。它检查的是可验证的指令约束，更像规则奖励，适合做格式回归，人评那部分它管不了。

**judge 和人评对不上，调高温度多采几次行不行？**
不行。对不上多半是标准没写清，温度解决不了，要回去改协议和提示。
