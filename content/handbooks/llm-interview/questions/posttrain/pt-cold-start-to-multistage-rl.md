---
id: pt-cold-start-to-multistage-rl
section: posttrain
order: 31
level: S
title: 既然 R1-Zero 能纯 RL，为什么生产配方仍常用 cold-start CoT、RL、rejection sampling、二次 RL？
quick: 纯 RL 证明了探索可行，不代表它是最稳的产品配方。cold start 先提供格式、语言与基本解题 support；RL 扩探索和优化 reward；rejection sampling 回收高质量轨迹；二次 RL 再对齐通用能力和可读性。
tags:
  - Reasoning RL
  - Cold Start
  - Curriculum
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: DeepSeek-R1
    url: https://arxiv.org/abs/2501.12948
    type: primary
---

多阶段的核心是每阶段处理不同瓶颈。cold-start SFT 让策略进入可读、可解析、能拿到 reward 的区域；on-policy RL 才有机会在该区域附近发现更强的推理；rejection sampling 将验证过的成功轨迹转为稳定监督；随后可在更宽任务和偏好目标上再次对齐。

设计实验时要分别测探索能力、格式率、语言混杂、长思考长度、通用 instruction-following 与安全拒答。只把所有步骤放在一起跑，无法知道瓶颈是 seed quality、reward、rollout 还是 data mixing。

常见错误是把 RS 当成 RL 的同义词。RS 只能从已有候选里筛选，若正确轨迹覆盖率低、问题需要连续 state exploration，就仍需 on-policy 数据或更强 teacher。
