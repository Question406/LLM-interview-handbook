---
id: dt-eval-no-gold
section: labs
order: 52
level: A
title: Cohere / Harvey：没有金标、专家很贵，评测集怎么造？
quick: "按任务能不能自动判分来分配专家时间。能执行检查、有标准答案的任务做成自动评测，人只抽查；专家负责写评分标准、标边界案例，并用少量样本校准模型评分。LLM judge 可以辅助开发，未经校准不能当标准答案；生产日志也不能直接变成评测集。"
companies:
  - apple
tags:
  - Cohere
  - Harvey
  - Evaluation
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "LLM-as-a-Judge (Zheng et al.)"
    url: https://arxiv.org/abs/2306.05685
    type: primary
  - title: LiveBench
    url: https://arxiv.org/abs/2406.19314
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

先按「能不能自动判分」把任务分开，再决定专家时间花在哪。专家预算花在写评分协议、标边界题和校准 judge 上，大量的「哪个更好」比较交给自动题和校准过的 judge。

这题来自 Cohere / Harvey 的公开面试指南，两家都问过「客户没有标注数据，上线前后怎么评」。常见的错误答案有两种：把生产日志直接当评测集，或者让 LLM judge 自己给自己打分。

## 三类任务，三种做法

1. **能执行或有标准答案的任务**：直接造自动题，人只抽查。LiveBench 就把客观金标当作对抗 judge 偏见的设计。
2. **检索任务**：检查引用能否在检索结果里找到支持。让人判断「源文档里有没有这条信息」，比判断「回答写得好不好」更容易统一标准。引用题可以和 `dt-webgpt-cite`、`dt-grounding-data` 对照着练。
3. **开放生成**：先写评分协议，人标一小批样本来校准 judge（Zheng 等人的 LLM-as-judge），之后 judge 只用作开发阶段的回归检查。

## 金标从哪来

校准样本和金标来自 user study、许可脚本和内部研究集。企业客户的文档走权限感知检索，租户数据不进基础模型，见 `dt-prompt-rag-ft`。

## 追问

- **上线后怎么评？** 抽样人评加自动切片，A/B 只看用户同意过的指标。复制、重试这类隐式信号有偏，只能当触发条件，不能当门禁。
- **专家一周只能标 200 条？** 把这 200 条当校准和门禁的种子，其余用自动题扩充。这 200 条要覆盖各类失败模式，不要随手抽方便的样本。
- **没有检索、纯聊天怎么办？** 先分别评测该拒绝的请求、应该回答的请求、是否迎合用户、是否遵循指令，最后再评文风。文风最贵，放在最后标。
