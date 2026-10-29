---
id: dt-gemini-rl-env
kind: design
situation: 报告中的 Agent 训练包含不同反馈来源。
task: 提取可迁移的环境和数据原则。
approach: 分开任务生成、执行验证与 policy optimization。
result: 按原文限定事实，方案要独立实验支持。
---

## 可以这样回答

报告中的 Agent 训练包含不同反馈来源。

Gemini 2.5 报告把奖励分成 verifiable reward 和模型生成式奖励，agent 环境以测试、解释器、状态 assertion 当主要判定依据，模型评分补规则覆盖不到的目标，并且要做 calibration。环境要支持多步动作和工具、保存中间状态，才能审计改测试、重复执行但没有推进任务、假装运行这类 hack。直接奖励「想得长」，模型会写更长的推理却没完成任务，所以长度要和最终对错绑在一起。
