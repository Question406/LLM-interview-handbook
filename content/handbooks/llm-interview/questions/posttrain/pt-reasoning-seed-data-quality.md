---
id: pt-reasoning-seed-data-quality
section: posttrain
order: 42
level: S
title: 为什么少量高质量 expert CoT 有时能激活 reasoning，而大量普通 CoT 不行？
quick: Seed data 的价值在于把策略送进能探索、能被 verifier 区分的轨迹区域，不在 token 总量。优先看题目难度、答案与步骤正确性、关键决策密度、格式一致性和与目标任务的匹配，再做小规模 ablation。
tags:
  - Seed Data
  - Chain of Thought
  - SFT
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: The Challenge of Teaching Reasoning to LLMs Without RL or Distillation
    url: https://arxiv.org/abs/2507.09850
    type: primary
---

普通 CoT 常包含冗余模板、错误中间步或对目标模型过难/过易的任务；大规模混入后，模型只会学到“写很长”的表面风格。高质量 expert trace 则提供可验证的关键转折、稳定的格式和足够难的题，使后续 RL 能获得有意义的 reward 差异。

数据选择应分开检查 prompt 难度、最终答案正确、每步有效性、长度、语言/工具格式和 teacher–student capability gap。最有效的实验是固定总 token，替换不同质量/难度的 seed，测冷启动成功率、后续 RL 学习曲线和 OOD 泛化。

不要把少量高质量数据神化为通用规律。对于知识缺口任务，seed 仍需覆盖事实与工具使用；对于 verifier 有漏洞的任务，再漂亮的 CoT 也会把模型带向错误奖励。
