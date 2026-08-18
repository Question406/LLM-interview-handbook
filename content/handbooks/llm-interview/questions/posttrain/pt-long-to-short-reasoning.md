---
id: pt-long-to-short-reasoning
section: posttrain
order: 30
level: S
title: 如何把 Long-CoT Reasoner 蒸馏成短思考模型，同时尽量不掉能力？
quick: 不是简单删 token。先筛出正确且有信息密度的长轨迹，训练学生保留关键决策或答案，再用质量–token 曲线验证；若任务需要中间证明，应蒸馏状态转移而非只蒸馏最终答案。
tags:
  - Distillation
  - Chain of Thought
  - Efficiency
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: Kimi k1.5
    url: https://arxiv.org/abs/2501.12599
    type: primary
---

先用可验证答案或高质量 judge 过滤 teacher rollout；错误但写得漂亮的长 CoT 是有害监督。压缩目标可以是短 rationale、关键步骤摘要、工具计划，或只输出答案但保留内部训练信号；选择取决于下游是否需要可审计过程。

训练时同时约束正确性和长度，例如按 token bucket 训练不同预算版本，或把长度作为条件输入。评估必须报告相同题集上的准确率、平均/P95 token、延迟和预算退化曲线，而不是只报告“平均更短”。

失败模式包括删掉了真正的分支决策、学生只模仿表面措辞、以及 teacher 轨迹与学生实际会访问的状态分布不一致。此时可先让学生自己 rollout，再在其状态上蒸馏。
