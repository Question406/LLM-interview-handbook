---
id: dt-eval-no-gold
section: labs
order: 52
level: A
title: Cohere / Harvey：没有金标、专家很贵，评测集怎么造？
quick: "先把能执行检查、或有标准答案的任务做成自动评测。专家负责制定标准、标注边界案例，并用少量样本校准模型评分。LLM judge 可以辅助开发，不能未经校准就当标准答案；生产日志也不能直接变成评测集。"
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

我会先把任务切成三桶。能执行或有标准答案的，造自动题，人只抽查。对检索任务，检查引用是否能在检索结果中找到支持。让人判断「源文档有没有这条信息」，比判断「回答写得好不好」更容易统一标准。开放生成：先写协议，人标一小截校准 judge，judge 只当开发回归。专家预算花在协议、边界题、校准，不花在十万条「哪个更好」。

不这么选的理由：Cohere 和 Harvey 的公开题都问过「客户没有标注数据，上线前后怎么评」。标准常见误区是生产日志当评测，或 judge 自嗨。LiveBench 把客观金标写成对抗 judge 偏见的设计。

接到苹果：用户交互默认不进评测集。校准和金标来自 user study、许可脚本、内部研究集。企业客户文档走权限感知检索，租户数据不进基础模型，见 `dt-prompt-rag-ft`。引用题和 `dt-webgpt-cite`、`dt-grounding-data` 对刷。

公开锚点：Zheng 等人的 LLM-as-judge；LiveBench。题型来自 Cohere / Harvey 公开面试指南。

## 追问

- **上线后呢？** 抽样人评加自动切片，A/B 只看同意过的指标。隐式信号（复制、重试）偏，只能当触发，不当门禁。
- **专家一周只能标 200 条？** 200 条当校准和门禁种子。其余用自动题扩。200 条要覆盖失败模式，不要随机方便样本。
- **没有检索、纯聊天？** 先分别评测该拒绝的请求、应该回答的请求、是否迎合用户，以及是否遵循指令，再评测文风。文风最贵，最后标。
