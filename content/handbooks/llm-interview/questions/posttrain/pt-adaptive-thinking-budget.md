---
id: pt-adaptive-thinking-budget
section: posttrain
order: 27
level: S
title: 同一延迟 / Token 预算下，如何让模型决定要不要继续想、想多久、何时停止？
quick: 不把长思考当免费能力。先定义任务质量、延迟和 token 成本的 Pareto 目标，再用难度或不确定性触发更多推理，并以独立题集验证预算控制器没有只偏向“写得更长”。
tags:
  - Test-time Scaling
  - Reasoning
  - Budget
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: Qwen3 Technical Report
    url: https://arxiv.org/abs/2505.09388
    type: primary
---

先把问题写成受预算约束的决策：在总 token、端到端延迟和调用次数固定时，决定每题的 reasoning budget。简单的全局固定长度容易在简单题浪费预算、在难题过早停止；更合理的信号包括初始答案的置信度、多个样本的分歧、verifier 不确定性和任务的已知难度分桶。

控制器必须允许“直接回答、继续单条思考、并行采样、交给 verifier”几种动作，并为每种动作记账。验收不只看平均准确率，还要画 quality–cost 曲线，按简单/困难/长上下文切片看 P95 latency、平均 reasoning token 和失败率。

常见误区是把输出更长误认为思考更充分。需要用固定预算消融、隐藏题集和人类/可执行 oracle 检查，确认增益来自更好的计算分配而不是训练集风格或长度偏差。
